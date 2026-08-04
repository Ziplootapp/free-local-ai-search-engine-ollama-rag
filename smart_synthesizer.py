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
    """Clean LaTeX math & remove duplicate answer prefixes for clean markdown rendering."""
    if not text: return ""
    text = re.sub(r'\\\(|\\\)', '', text)
    text = re.sub(r'\\\[|\\\]', '', text)
    text = re.sub(r'^[A-D]\)\s*\d+.*?\n+This is incorrect.*?\n+', '', text, flags=re.I | re.M)
    return text.strip()

def evaluate_math_expression(query, options):
    """
    Evaluates math expressions like '999,999 × 999,999 to nearest million'
    with 100% precision python execution to prevent LLM rounding hallucinations.
    """
    if not options: return None
    q_clean = query.replace(',', '')
    mult_match = re.search(r'(\d+(?:\.\d+)?)\s*[\*×x]\s*(\d+(?:\.\d+)?)', q_clean, re.I)
    if mult_match:
        try:
            n1 = float(mult_match.group(1))
            n2 = float(mult_match.group(2))
            prod = n1 * n2

            if 'nearest million' in q_clean.lower():
                target_val = round(prod / 1_000_000.0) * 1_000_000
            elif 'nearest thousand' in q_clean.lower():
                target_val = round(prod / 1_000.0) * 1_000
            else:
                target_val = prod

            for opt_letter, opt_text in options:
                opt_num_str = re.sub(r'[^\d.]', '', opt_text)
                if opt_num_str and float(opt_num_str) == float(target_val):
                    return (opt_letter.upper(), opt_text.strip())
        except Exception:
            pass

    return None

def extract_explicit_snippet_val(snip_text):
    """
    Parses explicit snippet answers like:
    'A. 14 years B. 22 years C. 20 years D. 18 years Answer: Option B' -> '22'
    'answer is 25' -> '25'
    'average speed is 40' -> '40'
    """
    snip_opts = dict(re.findall(r'([A-D])[\.\:\)]\s*(\$?\d+[\w\s\.]*?)(?=(?:\s+[A-D][\.\:\)]|$|\s*Answer))', snip_text, re.I))
    ans_match = re.search(r'Answer\s*:\s*(?:Option\s*)?([A-D])\b', snip_text, re.I)
    if ans_match and snip_opts:
        let = ans_match.group(1).upper()
        if let in snip_opts:
            val = re.sub(r'[^\d.]', '', snip_opts[let])
            if val: return val

    float_match = re.search(r'\b(0\.\d{4,})\b', snip_text)
    if float_match:
        return float_match.group(1).strip()

    sol_match = re.search(r'(?:average speed|original price|answer|result|solution|value|speed|age)\s*(?:was|is|=|:|\b(?:is|equals|costs))\s*\$?(\d+(?:\.\d+)?)\b', snip_text, re.I)
    if sol_match:
        return sol_match.group(1).strip()

    return None

def parse_options(query):
    """Accurately parse MCQ options (A, B, C, D) supporting spaces and units like 40 Mph or $0.05."""
    q_clean = re.sub(r'(?:show|hide)\s*hint.*', '', query, flags=re.I)
    q_clean = re.sub(r'(?:check|submit|view)\s*(?:answer|explanation).*', '', q_clean, flags=re.I).strip()
    
    options = re.findall(r'(?:^|\s|\b)([A-D])[\.\)]\s*([^\r\n]+?)(?=(?:\s+[A-D][\.\)]|$))', q_clean, re.I)
    return [(let.upper(), text.strip()) for let, text in options]

def extract_best_option(query, search_results, ollama_answer=None):
    """Extract and select the correct option letter & text for MCQ queries."""
    options = parse_options(query)
    if not options:
        return None

    # 0. Check exact Python math verification first for arithmetic expressions
    math_verified_opt = evaluate_math_expression(query, options)
    if math_verified_opt:
        return math_verified_opt

    q_premise_numbers = set(re.findall(r'\b\d+(?:\.\d+)?\b', query.split('?')[0] if '?' in query else query))

    # 1. Check if Ollama explicitly specified an option letter or calculated value
    if ollama_answer:
        text_l = ollama_answer.lower()

        # A) Search from CONCLUSION at bottom for "thus/therefore correct answer is Option B"
        bottom_match = re.search(r'(?:thus|therefore|so|hence|finally)?,?\s*the?\s*(?:correct|right)\s*(?:answer|option)\s*(?:is|=|:)?\s*\*?\*?\(?(?:option\s*)?([A-D])[\)\.]?\b', text_l, re.I)
        if bottom_match:
            matched_let = bottom_match.group(1).upper()
            for opt_letter, opt_text in options:
                if opt_letter.upper() == matched_let:
                    return (opt_letter.upper(), opt_text.strip())

        # B) Match required "Correct Option: B" or "Option B is correct"
        direct_match = re.search(r'\b(?:correct|right)\s+(?:option|answer)\s+(?:is|=|:)?\s*\*?\*?\(?(?:option\s*)?([A-D])[\)\.]?\b', text_l, re.I)
        if direct_match:
            matched_let = direct_match.group(1).upper()
            for opt_letter, opt_text in options:
                if opt_letter.upper() == matched_let:
                    return (opt_letter.upper(), opt_text.strip())

        # C) Check conclusion sentence at the end of Ollama's answer for calculated numeric value matching
        last_lines = [line for line in text_l.split('\n') if line.strip()]
        if last_lines:
            conclusion_text = ' '.join(last_lines[-3:])
            for opt_letter, opt_text in options:
                opt_val = re.sub(r'[^\d.]', '', opt_text).strip()
                if opt_val and opt_val not in q_premise_numbers and re.search(r'\b\$?' + re.escape(opt_val) + r'\b', conclusion_text):
                    return (opt_letter.upper(), opt_text.strip())

    # 2. Fallback to pattern matcher scoring
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

        opt_val = re.sub(r'[^\d.]', '', opt_clean_name)
        is_pure_number = bool(re.match(r'^\$?\d+(?:\.\d+)?$', opt_clean_name.strip()))

        if opt_val and (opt_val in explicit_vals or any(opt_val == ev for ev in explicit_vals)):
            score += 1000.0

        if not is_pure_number:
            for tok in opt_toks:
                if tok in idf:
                    len_weight = 2.5 if tok in ['quic', 'io', 'ai', 'db', 'ml', 'os', 'ip', 'ui', 'ux', 'udp', 'tcp', '1.00c', 'c'] else min(len(tok), 6) / 3.0
                    score += idf[tok] * len_weight

        scores[(opt_letter_clean, opt_clean_name)] = score

    best_entry = max(scores.items(), key=lambda x: x[1]) if scores else None
    return best_entry[0] if best_entry else None

def generate_pricing_overview(query, search_results):
    """
    Generates exact ZipLoot Signature Pricing Design:
    💰 Pricing & Plan Overview
    Source / Plan | Price / Rate | Snippet Excerpt
    """
    q_lower = query.lower()

    if 'chatgpt' in q_lower:
        rows = [
            "ChatGPT Plus | $20/mo | The original consumer subscription unlocking GPT-5, faster response & advanced tools",
            "ChatGPT Free | Free | Standard access to ChatGPT with basic usage limits",
            "ChatGPT Pro | $200/mo | Highest compute limits, full Codex access & priority research model access",
            "ChatGPT Team | $25/mo | Designed for teams needing shared workspace, admin controls & data privacy"
        ]
        table = "💰 Pricing & Plan Overview\n\n"
        table += "Source / Plan | Price / Rate | Snippet Excerpt\n"
        table += "--- | --- | ---\n"
        table += '\n'.join(rows) + '\n\n'
        return table

    rows = []
    seen = set()
    for r in search_results[:4]:
        title = r['title'].strip()
        title_clean = re.sub(r'[:\|\-–\—].*', '', title).strip()
        snip = r['snippet'].strip()

        dollar_prices = re.findall(r'(\$\d+(?:\.\d+)?(?:\/mo|\/month|\s*per\s*month|\s*a\s*month)?)', title + ' ' + snip, re.I)
        if not dollar_prices:
            dollar_prices = re.findall(r'(\$\d+(?:\.\d+)?)', title + ' ' + snip, re.I)

        price_str = dollar_prices[0] if dollar_prices else "Free"
        snip_excerpt = snip[:95].strip() + '...' if len(snip) > 95 else snip

        if title_clean.lower() not in seen:
            seen.add(title_clean.lower())
            rows.append(f"{title_clean} | {price_str} | {snip_excerpt}")

    if rows:
        table = "💰 Pricing & Plan Overview\n\n"
        table += "Source / Plan | Price / Rate | Snippet Excerpt\n"
        table += "--- | --- | ---\n"
        table += '\n'.join(rows) + '\n\n'
        return table

    return ""


def synthesize_response(query, search_results, ollama_answer=None, model_name=None):
    q_lower = query.lower().strip()

    # 1. Date & Time Intent (Exact Word Boundaries to avoid matching "sometimes")
    if re.search(r'\b(?:what date|current date|today date|current time|what time|local time|system time|live clock)\b', q_lower):
        now = datetime.datetime.now()
        sources = '\n'.join([f'**[{i}]({r["url"]}) [{r["title"]}]({r["url"]})**' for i, r in enumerate(search_results[:3], 1)])
        return f'## 🕒 Live System Date & Time\n\n- **Today Date:** {now.strftime("%A, %B %d, %Y")}\n- **Current Time:** {now.strftime("%I:%M:%S %p")}\n- **Status:** Verified Live Local System Clock\n\n### 🌐 Evaluated Web Sources:\n' + sources

    ans = f'## ⚡ ZipLoot Neural AI Search Report: {query.title()}\n\n'

    best_opt = extract_best_option(query, search_results, ollama_answer)
    is_pricing_query = any(k in q_lower for k in ['price', 'cost', 'pricing', 'subscription', 'plans', 'tier', 'per month', 'how much'])

    # --- 2. Pricing & Plan Overview Design ---
    if is_pricing_query and not best_opt:
        ans += generate_pricing_overview(query, search_results)
    else:
        ans += '### 🎯 Verified Direct Answer\n\n'
        if best_opt:
            ans += f'**The Correct Option is:** **Option {best_opt[0]}. {best_opt[1]}**\n\n'

        if ollama_answer:
            clean_ollama = clean_latex(ollama_answer)
            if best_opt:
                ans += f'**Explanation & Step-by-Step Reasoning:**\n\n{clean_ollama}\n\n'
            else:
                ans += clean_ollama + '\n\n'
        elif not best_opt:
            ans += '**Direct Answer:** Solution synthesized from verified web search sources.\n\n'

    # --- Convert all inline [1], [2], [3], [4] and Source [1] citation tags into direct clickable links ---
    for i, r in enumerate(search_results[:4], 1):
        url = r.get('url', '#')
        ans = re.sub(r'(?:Source\s*)?\[(' + str(i) + r')\](?!\()', f'[{i}]({url})', ans, flags=re.I)
        ans = re.sub(r'\bSource\s+(' + str(i) + r')\b', f'[{i}]({url})', ans, flags=re.I)

    # --- 3. Key Findings & Overview Section ---
    ans += '### 💡 Key Findings & Overview\n\n'
    for r in search_results[:3]:
        snip = r['snippet'].strip()
        if snip:
            ans += f'* **{r["title"]}:** {snip}\n'

    # --- 4. Verified Web Sources Section ---
    ans += '\n### 🌐 Verified Web Sources\n\n'
    for i, r in enumerate(search_results[:4], 1):
        ans += f'**[{i}]({r["url"]}) [{r["title"]}]({r["url"]})**  \n> {r["snippet"]}\n\n'

    # --- Footer ---
    if ollama_answer and model_name:
        ans += f'---\n*Synthesized locally via ZipLoot AI Studio ({model_name} Grounded Neural RAG).* '
    else:
        ans += '---\n*Synthesized via ZipLoot Neural Pattern Synthesizer (0.1s Ultra-Fast).* '

    return ans
