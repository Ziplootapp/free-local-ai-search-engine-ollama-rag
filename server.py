from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os
import sys

# Configure UTF-8 encoding for Windows console output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from fast_search import fast_web_search
from smart_synthesizer import synthesize_response, parse_options

PORT = 8050
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# ─── Dynamic Ollama Auto-Detection & Selection ────────────────
OLLAMA_AVAILABLE = False
OLLAMA_MODEL = "qwen2.5:7b"

def check_ollama():
    """Check if Ollama is running locally and dynamically pick the largest/best available model."""
    global OLLAMA_AVAILABLE, OLLAMA_MODEL
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/tags",
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = [m.get('name', '') for m in data.get('models', [])]
            if models:
                OLLAMA_AVAILABLE = True
                preferred = [m for m in models if any(k in m.lower() for k in ['qwen', 'llama', 'deepseek', 'mistral', 'gemma'])]
                if preferred:
                    preferred.sort(key=lambda m: (
                        '0.5b' in m.lower(),
                        '1.5b' in m.lower(),
                        '3b' in m.lower(),
                        not any(k in m.lower() for k in ['7b', '8b', '14b', '32b', '70b', 'latest'])
                    ))
                    OLLAMA_MODEL = preferred[0]
                else:
                    OLLAMA_MODEL = models[0]
                print(f"  [OLLAMA] Active & Connected! Selected model: '{OLLAMA_MODEL}'")
            else:
                print("  [OLLAMA] Service active on port 11434 (No models pulled yet).")
    except Exception:
        OLLAMA_AVAILABLE = False

def ollama_generate(query, search_results):
    """Generate raw AI reasoning using local Ollama LLM with ZipLoot signature format rules."""
    sources_text = ""
    for idx, r in enumerate(search_results[:4], 1):
        sources_text += f"Source [{idx}]: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n\n"

    is_mcq = bool(parse_options(query))

    if is_mcq:
        rules_prompt = """Rules:
1. Calculate and reason step-by-step with 100% precision.
2. At the very end of your answer, state the final conclusion clearly: "Therefore, the correct answer is Option [Letter]. [Text]"."""
    else:
        rules_prompt = """Rules:
1. State the direct answer clearly and concisely in clean natural language paragraphs.
2. Provide concise, helpful bullet points for key details.
3. Do NOT mention option letters like Option A or Option B unless options A/B/C/D were in the question."""

    prompt = f"""You are ZipLoot Universal AI Engine (Grounded RAG Engine).
Synthesize a precise, direct, accurate solution for: "{query}"

Verified Web Context:
{sources_text}

{rules_prompt}

Answer:"""

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 600,
            "num_thread": 8
        }
    }).encode('utf-8')

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            ai_text = data.get("response", "").strip()
            if ai_text:
                return ai_text
    except Exception as e:
        print(f"  [OLLAMA] Generation failed or timed out, falling back to synthesizer: {e}")

    return None


class ZipLootServer(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)

            # 1. API Endpoint for AI Search
            if parsed.path == "/api/ai-search":
                query = urllib.parse.parse_qs(parsed.query).get("q", [""])[0]
                if not query:
                    self.send_response(400)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    return

                try:
                    print(f"  [ZIPLOOT ENGINE] Query: {query}")
                    sys.stdout.flush()
                except Exception:
                    pass

                search_results = fast_web_search(query)

                if not OLLAMA_AVAILABLE:
                    check_ollama()

                # Try Ollama first for LLM reasoning
                raw_ollama_ans = None
                if OLLAMA_AVAILABLE:
                    raw_ollama_ans = ollama_generate(query, search_results)

                # Combine Ollama reasoning + ZipLoot signature v7.0 UI structure
                ai_answer = synthesize_response(
                    query, 
                    search_results, 
                    ollama_answer=raw_ollama_ans, 
                    model_name=OLLAMA_MODEL if raw_ollama_ans else None
                )

                payload = {
                    "query": query,
                    "status": "success",
                    "engine": f"ollama-rag ({OLLAMA_MODEL})" if raw_ollama_ans else "smart-synthesizer",
                    "sources": search_results,
                    "answer": ai_answer
                }

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8"))
                return

            # 2. Static HTML File Serving (Root /, /index.html, /ai-search)
            file_path = os.path.join(DIR_PATH, "index.html")

            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(b"404 ZipLoot App Page Not Found")

        except Exception as err:
            try:
                print(f"  [ZIPLOOT ERROR]: {err}")
                sys.stdout.flush()
            except Exception:
                pass
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            err_payload = {"status": "error", "error": str(err)}
            self.wfile.write(json.dumps(err_payload, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress verbose default HTTP logging."""
        pass


def run_server():
    print("")
    print("========================================================")
    print("  ZipLoot AI Search Studio v2.0 - Server Daemon")
    print("  Local Web App: http://localhost:8050/")
    print("  Official Portal: https://ziploot.app")
    print("========================================================")
    print("")

    # Dynamic Auto-Detect Ollama Model
    check_ollama()
    print("")

    try:
        server = HTTPServer(("0.0.0.0", PORT), ZipLootServer)
    except OSError as e:
        if "address already in use" in str(e).lower() or "10048" in str(e):
            print(f"  [ERROR] Port {PORT} is already in use!")
            print(f"  Close any existing instance or check: netstat -an | findstr {PORT}")
        else:
            print(f"  [ERROR] Could not start server: {e}")
        sys.stdout.flush()
        input("\n  Press Enter to exit...")
        sys.exit(1)

    print(f"  [LIVE] ZipLoot AI Engine active on http://localhost:{PORT}/")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  [INFO] Server stopped by user.")
        server.server_close()


if __name__ == "__main__":
    run_server()
