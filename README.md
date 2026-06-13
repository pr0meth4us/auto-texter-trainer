# AI Persona Clone Data Pipeline

This repository contains a robust data engineering pipeline designed to generate highly contextual, bilingual, and privacy-safe AI persona clones from raw conversational data.

**Note: For privacy reasons, the `data/` directory is strictly ignored by `.gitignore`. You must provide your own raw chat data locally to use these scripts.**

## 🧠 System Architecture: What it is & How it works

Training a Large Language Model (LLM) to accurately mimic a highly specific, idiosyncratic conversational persona (especially one utilizing mixed-language slang like Latinized Khmer) requires massive amounts of few-shot context. However, feeding raw chat logs directly into an LLM context window is a massive security risk, as it exposes Personally Identifiable Information (PII) to the inference engine.

This pipeline solves the "Context vs. Privacy" problem through a localized, automated anonymization framework.

### 1. Zero-Shot Named Entity Recognition (NER)
To scrub the dataset, we cannot rely on standard English dictionaries because bilingual texting contains phonetic slang and non-standard capitalization.
- **How it works:** The `src/extract_names.py` script leverages the Gemini 3.5 Flash inference engine to perform contextual Named Entity Recognition. It scans the raw conversational history in chunks and flags linguistic patterns that represent names, relationship identifiers (e.g., "mom", "boss", "babe", "my ex"), and locations.
- **The Result:** An exhaustive `data/blocklist.txt` tailored specifically to the user's localized dialect.

### 2. High-Throughput Dataset Anonymization
Once the blocklist is generated, the dataset must be aggressively scrubbed before it ever touches a production LLM's prompt state.
- **How it works:** The `src/sanitize_history.py` script executes a bulk Regex string-replacement operation across the entire dataset. It safely swaps all identified PII boundaries with the generic placeholder token `[FRIEND]`. 
- **The Result:** The LLM can safely ingest the `subset_10k_sanitized.txt` dataset. It learns the phonetic spelling, grammar, and emotional pacing of the persona without ever seeing real names.

### 3. Adversarial Prompt Validation
Before deploying the persona prompt to production, it must be hardened against social engineering.
- **How it works:** The `tests/test_secrets.py` script functions as an automated red-teaming suite. It subjects the finalized AI Clone (equipped with the sanitized dataset and system instructions) to 25 aggressive adversarial prompts (e.g., asking for bank pins, physical addresses, or relationship history). 
- **The Result:** Validates that the AI agent strictly adheres to its system constraints—successfully deflecting, acting confused, or ignoring PII requests while maintaining character.

---

## 🛠️ Tech Stack

This pipeline is powered entirely by native Python, leveraging modern AI and data-processing tools:
- **Language**: Python 3.10+
- **AI Engine**: Google Gemini 3.5 Flash
- **SDK Integration**: Official `google-genai` Python SDK
- **Data Engineering**: Regular Expressions (Regex), contextual Named Entity Recognition (NER), and adversarial LLM testing.

## 🗂️ Repository Structure

```text
auto-texter-trainer/
├── data/               # All raw text, datasets, and blocklists (gitignored)
├── src/                # Core ML/Pipeline processing code 
├── tests/              # Core test suites for adversarial security
├── scripts/            # Utility scripts (caching, token counting)
└── archive/            # Old testing scratchpads and legacy scripts
```

## 🚀 Local Setup
To run this pipeline locally, you must install the required dependencies and authenticate with Google Cloud:
```bash
pip install google-genai
```
You must also export your API key to your environment before executing any scripts:
```bash
export GEMINI_API_KEY="your_api_key_here"
```
