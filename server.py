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
from smart_synthesizer import synthesize_response

PORT = 8050
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

# ─── Ollama Auto-Detection ───────────────────────────────────
OLLAMA_AVAILABLE = False
OLLAMA_MODEL = "qwen2.5:7b"

def check_ollama():
    """Check if Ollama is running locally and has a model available."""
    global OLLAMA_AVAILABLE
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/tags",
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = [m.get('name', '') for m in data.get('models', [])]
            if any(OLLAMA_MODEL.split(':')[0] in m for m in models):
                OLLAMA_AVAILABLE = True
                print(f"  [OLLAMA] Detected! Using {OLLAMA_MODEL} for enhanced answers.")
            elif models:
                OLLAMA_AVAILABLE = True
                print(f"  [OLLAMA] Detected with models: {', '.join(models[:3])}")
            else:
                print("  [OLLAMA] Running but no models found. Run: ollama pull qwen2.5:7b")
    except Exception:
        print("  [OLLAMA] Not running - using ZipLoot Smart Synthesizer.")

def ollama_generate(query, search_results):
    """Generate AI answer using local Ollama LLM."""
    sources_text = ""
    for idx, r in enumerate(search_results[:3], 1):
        sources_text += f"Source [{idx}]: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet']}\n\n"

    prompt = f"""You are ZipLoot Universal AI Engine (Grounded RAG Engine).
Synthesize a concise, direct Markdown response for: "{query}"

Web Data:
{sources_text}

Rules:
1. State the exact main answer immediately.
2. Keep response concise and accurate.
3. Include source links.

Answer:"""

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 140,
            "num_thread": 8
        }
    }).encode('utf-8')

    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=payload,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            ai_text = data.get("response", "").strip()
            if ai_text:
                return ai_text + f"\n\n---\n*Synthesized locally via ZipLoot AI Studio ({OLLAMA_MODEL} Grounded RAG).* "
    except Exception as e:
        print(f"  [OLLAMA] Generation failed, falling back to synthesizer: {e}")

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

                # Try Ollama first, fall back to synthesizer
                ai_answer = None
                if OLLAMA_AVAILABLE:
                    ai_answer = ollama_generate(query, search_results)
                if ai_answer is None:
                    ai_answer = synthesize_response(query, search_results)

                payload = {
                    "query": query,
                    "status": "success",
                    "engine": "ollama-rag" if OLLAMA_AVAILABLE and ai_answer else "smart-synthesizer",
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

    # Auto-detect Ollama
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
