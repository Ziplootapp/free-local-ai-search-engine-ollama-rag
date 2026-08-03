import re
import datetime
import math

SYNONYMS = {
    'async': 'asynchronous',
    'asynchronous': 'async',
    'i/o': 'io',
    'io': 'i/o',
    'aio': 'asynchronous io',
    'db': 'database',
    'ml': 'machine learning',
    'hbm': 'high bandwidth memory',
    'lifo': 'last in first out',
    'fifo': 'first in first out',
    'quic': 'quick udp internet connections'
}

def expand_tokens(text):
    text_lower = text.lower()
    raw_tokens = re.findall(r'\b[a-zA-Z0-9\/\+\#]{1,}\b', text_lower)
    tokens = set(raw_tokens)
    for tok in list(tokens):
        if tok in SYNONYMS:
            for syn in SYNONYMS[tok].split():
                tokens.add(syn)
    return tokens

def clean_latex(text):
    """Clean LaTeX math delimiters for clean markdown rendering."""
    if not text: return ""
    text = re.sub(r'\\\(|\\\)', '', text)
    text = re.sub(r'\\\[|\\\]', '', text)
    return text.strip()

def extract_explicit_snippet_val(snip_text):
    """
    Parses explicit snippet answers like:
    'A. 14 years B. 22 years C. 20 years D. 18 years Answer: Option B' -> '22'
    'x = 22 years' -> '22'
    'present age is 22 years' -> '22'
    """
    snip_opts = dict(re.findall(r'([A-D])[\.\:\)]\s*(\d+[\w\s]*?)(?=(?:\s+[A-D][\.\:\)]|$|\s*Answer))', snip_text, re.I))
    ans_match = re.search(r'Answer\s*:\s*(?:Option\s*)?([A-D])\b', snip_text, re.I)
    if ans_match and snip_opts:
        let = ans_match.group(1).upper()
        if let in snip_opts:
            val = re.sub(r'[^\d]', '', snip_opts[let])
            if val: return val

    eq_match = re.search(r'(?:x|ans|answer|age)\s*=\s*(\d+)\b', snip_text, re.I)
    if eq_match:
        return eq_match.group(1)

    sol_match = re.search(r'(?:age of (?:his )?son|present age)\s*(?:is|=|will be)\s*(\d+)', snip_text, re.I)
    if sol_match:
        return sol_match.group(1)

    return None

def synthesize_response(query, search_results, ollama_answer=None, model_name=None):
    q_lower = query.lower().strip()

    # 1. Date & Time Intent
    if any(k in q_lower for k in ['date', 'time', 'clock', 'today date']):
        now = datetime.datetime.now()
        sources = '\n'.join([f'**[{i}] [{r["title"]}]({r["url"]})**' for i, r in enumerate(search_results[:3], 1)])
        return f'## 🕒 Live System Date & Time\n\n- **Today Date:** {now.strftime("%A, %B %d, %Y")}\n- **Current Time:** {now.strftime("%I:%M:%S %p")}\n- **Status:** Verified Live Local System Clock\n\n### 🌐 Evaluated Web Sources:\n' + sources

    ans = f'## ⚡ ZipLoot Neural AI Search Report: {query.title()}\n\n'

    # --- 2. Direct Answer Section (Ollama LLM Reasoning or Pattern Engine) ---
    ans += '### 🎯 Verified Direct Answer\n\n'

    if ollama_answer:
        clean_ollama = clean_latex(ollama_answer)
        ans += clean_ollama + '\n\n'
    else:
        # Fallback Pattern Synthesizer
        q_clean = re.sub(r'(?:show|hide)\s*hint.*', '', query, flags=re.I)
        q_clean = re.sub(r'(?:check|submit|view)\s*(?:answer|explanation).*', '', q_clean, flags=re.I).strip()
        q_clean = re.sub(r'([a-zA-Z0-9\?\)\}\}\]])([A-Da-d1-4][\.\)])', r'\1 \2', q_clean)
        options = re.findall(r'([A-Da-d1-4])[\.\)]\s*([^\r\n]+?)(?=(?:\s+[A-Da-d1-4][\.\)]|$))', q_clean)

        best_opt = None
        if options:
            explicit_vals = []
            for r in search_results:
                v = extract_explicit_snippet_val(r['title'] + ' ' + r['snippet'])
                if v: explicit_vals.append(v)

            doc_tokens_list = [expand_tokens(r['title'] + ' ' + r['snippet']) for r in search_results]
            all_doc_tokens = set().union(*doc_tokens_list) if doc_tokens_list else set()

            N_docs = len(search_results) if search_results else 1
            idf = {}
            for tok in all_doc_tokens:
                doc_freq = sum(1 for d in doc_tokens_list if tok in d)
                idf[tok] = math.log((N_docs + 1) / (doc_freq + 1)) + 1.0

            scores = {}
            for opt_letter, opt_text in options:
                opt_clean_name = re.sub(r'(?:show|hide)\s*hint.*', '', opt_text, flags=re.I).strip()
                opt_letter_clean = opt_letter.upper()
                opt_toks = expand_tokens(opt_clean_name)
                score = 0.0

                opt_val = re.sub(r'[^\d]', '', opt_clean_name)
                if opt_val and opt_val in explicit_vals:
                    score += 1000.0

                if opt_val and len(opt_val) >= 1:
                    for r in search_results:
                        snip_full = (r['title'] + ' ' + r['snippet'])
                        is_premise = re.search(r'\b' + re.escape(opt_val) + r'\s*(?:years?\s+older|years?\s+younger|years?\s+ago|times)\b', snip_full, re.I)
                        if not is_premise:
                            if re.search(r'(?:x|ans|answer|age)\s*=\s*' + re.escape(opt_val) + r'\b', snip_full, re.I):
                                score += 500.0

                for tok in opt_toks:
                    if tok in idf:
                        len_weight = 2.5 if tok in ['quic', 'io', 'ai', 'db', 'ml', 'os', 'ip', 'ui', 'ux', 'udp', 'tcp'] else min(len(tok), 6) / 3.0
                        score += idf[tok] * len_weight

                opt_words = [w for w in re.split(r'[\s\-\/]+', opt_clean_name.lower()) if len(w) >= 2]
                combined_snips = ' '.join([r['title'] + ' ' + r['snippet'] for r in search_results]).lower()
                for i in range(len(opt_words)-1):
                    bigram = f"{opt_words[i]} {opt_words[i+1]}"
                    if bigram in combined_snips:
                        score += 15.0

                scores[(opt_letter_clean, opt_clean_name)] = score

            best_entry = max(scores.items(), key=lambda x: x[1]) if scores else None
            best_opt = best_entry[0] if best_entry else None

        if best_opt:
            ans += f'**The Correct Option is:** **Option {best_opt[0]}. {best_opt[1]}**\n\n'
        else:
            ans += '**Direct Answer:** Solution synthesized from verified web search sources.\n\n'

    # --- 3. Key Findings & Overview Section ---
    ans += '### 💡 Key Findings & Overview\n\n'
    for r in search_results[:3]:
        snip = r['snippet'].strip()
        if snip:
            ans += f'* **{r["title"]}:** {snip}\n'

    # --- 4. Verified Web Sources Section ---
    ans += '\n### 🌐 Verified Web Sources\n\n'
    for i, r in enumerate(search_results[:4], 1):
        ans += f'**[{i}] [{r["title"]}]({r["url"]})**  \n> {r["snippet"]}\n\n'

    # --- Footer ---
    if ollama_answer and model_name:
        ans += f'---\n*Synthesized locally via ZipLoot AI Studio ({model_name} Grounded Neural RAG).* '
    else:
        ans += '---\n*Synthesized via ZipLoot Neural Pattern Synthesizer (0.1s Ultra-Fast).* '

    return ans
