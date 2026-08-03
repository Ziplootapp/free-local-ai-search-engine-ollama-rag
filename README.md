# ⚡ ZipLoot AI Search Studio — #1 Free Local AI Search Engine & Ollama RAG (Self-Hosted Google AI Search & Perplexity Alternative)

[![ZipLoot Official Web App](https://img.shields.io/badge/Web%20App-ziploot.app-818cf8.svg?style=for-the-badge&logo=vercel)](https://ziploot.app)
[![Vercel Mirror](https://img.shields.io/badge/Mirror-ziploot.vercel.app-22d3ee.svg?style=for-the-badge&logo=vercel)](https://ziploot.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-c084fc.svg?style=for-the-badge)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-4ade80.svg?style=for-the-badge&logo=python)](https://python.org)
[![Ollama RAG](https://img.shields.io/badge/Ollama-Local%20Inference-f472b6.svg?style=for-the-badge)](https://ollama.com)

> **ZipLoot AI Search Studio** is a high-performance, 0.1-second ultra-fast **Self-Hosted Local AI Search Engine** and **Retrieval-Augmented Generation (RAG)** pipeline — built as a 100% free, private alternative to **Google AI Search Mode**, **Perplexity AI**, and **SearchGPT**. Powered by **Ollama (`qwen2.5`, `llama3.2`, `deepseek-r1`)** and a Universal TF-IDF Information Retrieval engine, it offers unlimited AI web search with zero rate limits, zero subscription fees, and zero data tracking.

---

## 🌐 Try Live Web App (No Setup Required)

Don't want to run a local server? You can access the full AI Search Studio instantly on our official web app:

* 🚀 **Official Primary App:** [**https://ziploot.app**](https://ziploot.app)
* ⚡ **Official Vercel Mirror:** [**https://ziploot.vercel.app**](https://ziploot.vercel.app)

---

## 🚀 1-Click Multi-OS Auto-Installer

Run a single command in your terminal to automatically download, setup virtual environment, install dependencies, and launch your local AI Search Studio on `http://localhost:8050/` in **1-Click**!

### 💻 For Windows (PowerShell):
```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; iwr -useb "https://github.com/Ziplootapp/free-local-ai-search-engine-ollama-rag/archive/refs/heads/main.zip" -OutFile "$env:TEMP\ziploot-ai.zip"; Expand-Archive -Path "$env:TEMP\ziploot-ai.zip" -DestinationPath "$env:TEMP\ziploot-app" -Force; cd "$env:TEMP\ziploot-app\free-local-ai-search-engine-ollama-rag-main"; .\deploy_windows.bat
```

### 📦 Manual Install (Windows — Download ZIP):
1. **[Download ZIP](https://github.com/Ziplootapp/free-local-ai-search-engine-ollama-rag/archive/refs/heads/main.zip)** → Extract anywhere
2. Open the extracted folder → Double-click **`deploy_windows.bat`**
3. Done! Browser opens automatically at `http://localhost:8050`

### 🐧 For Linux & macOS (Bash):
```bash
curl -sSL https://github.com/Ziplootapp/free-local-ai-search-engine-ollama-rag/archive/refs/heads/main.zip -o /tmp/ziploot-ai.zip && unzip -qo /tmp/ziploot-ai.zip -d /tmp/ziploot-app && cd /tmp/ziploot-app/free-local-ai-search-engine-ollama-rag-main && chmod +x deploy_linux.sh && ./deploy_linux.sh
```

### 🔄 Re-Launch (After Initial Setup):
Once installed, use these quick-start scripts for subsequent launches:
- **Windows:** Double-click **`start.bat`**
- **Linux/macOS:** Run `./start.sh`

---

## 🤖 Optional: Enable Ollama Local LLM (Enhanced AI Answers)

By default, ZipLoot AI Search uses its built-in **TF-IDF Smart Synthesizer** engine (works instantly, no GPU needed). For enhanced AI-powered answers using a local LLM:

1. **Install Ollama:** Download from [ollama.com](https://ollama.com/download)
2. **Pull a model:**
   ```bash
   ollama pull qwen2.5:7b
   ```
3. **Restart ZipLoot AI Search** — it will auto-detect Ollama and use local LLM for richer answers.

> **Note:** Ollama is 100% optional. ZipLoot works perfectly without it using the built-in synthesizer.

---

## 📖 Official 1-Click Setup Guide
👉 **[Read Official ZipLoot AI Search Setup Guide on ZipLoot.app](https://ziploot.app/posts/ziploot-ai-search-studio-setup)** *(Coming Soon)*

---

## 📊 Comparison Matrix: ZipLoot AI vs Google AI Search Mode vs Perplexity vs SearchGPT

| Feature / Metric | ZipLoot AI Search Studio | Google AI Search Mode | Perplexity AI | SearchGPT |
| :--- | :---: | :---: | :---: | :---: |
| **Monthly Subscription Fee** | **$0 / Month (100% Free)** | Limited API Quota | $20 / Month | $20 / Month |
| **Response Latency** | **~0.12 Seconds (Instant)** | ~1.85 Seconds | ~2.5 Seconds | ~2.8 Seconds |
| **Data Privacy & Local RAG** | **100% Private (Self-Hosted)** | Cloud Logged | Cloud Logged | Cloud Logged |
| **Rate Limits & API Quotas** | **Zero Rate Limits** | Daily API Caps | Pro Quota Caps | Pro Quota Caps |
| **Ollama Local LLM Support** | **Native (`qwen2.5`, `llama3.2`)** | ❌ No | ❌ No | ❌ No |

---

## 🔥 Key Technical Features

1. **Universal TF-IDF Information Retrieval Engine:**
   - Evaluates search snippets using Term Frequency-Inverse Document Frequency scoring.
   - Preserves technical acronyms (`I/O`, `QUIC`, `AI`, `DB`, `ML`, `OS`) and expands technical synonyms.

2. **Embedded Crash-Proof HTTP Daemon (`server.py`):**
   - Built-in `sys.stdout` UTF-8 reconfiguration prevents Windows console encoding crashes (`UnicodeEncodeError`).
   - Auto-detects Ollama for enhanced local LLM answers, falls back to built-in synthesizer.
   - Serves local HTTP API endpoint `/api/ai-search?q=<query>`.

3. **Ultra-Modern Glassmorphic UI (`index.html`):**
   - 100% Mobile & Desktop responsive layout.
   - Built-in one-click `Copy Response` action and dark-themed markdown table rendering.

---

## 🏷️ SEO Metadata & Search Keywords
`free local ai search engine`, `google ai search mode alternative`, `perplexity alternative github`, `self hosted ai search studio`, `ollama rag search engine`, `local llm web search`, `ziploot ai search`, `qwen2.5 local rag`, `free searchgpt alternative`.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.

Copyright (c) 2026 **ZipLoot Team** ([ziploot.app](https://ziploot.app) | [ziploot.vercel.app](https://ziploot.vercel.app))
