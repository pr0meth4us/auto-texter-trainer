# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- **Bifrost Integration**: Consolidated local `src/utils/bifrost_config.py` into a redirection proxy to consume the central client SDK, and refactored name extraction scripts (`src/extract_names.py`) to resolve keys dynamically.

### Added
- **Training and Diagnostic Scripts**:
  - `scripts/check_messages.py` and `scripts/list_groups.py` for Telegram metadata validation.
  - `src/cancel_jobs.py` for fine-tuning pipeline control.
  - `src/test_inference.py` for local inference evaluations.
  - `src/train_model.ipynb` Jupyter Notebook for LLM training workflow.
- **Synchronous Config Pull**: Embedded Bifrost SDK directly into `bifrost_config.py` to synchronously pull and inject API keys straight into local memory at boot, removing the need for `bifrost_local.py` or cache threads.
- Created `chatbot-ui`, a Next.js web application for interacting with the AI Persona Clone.
  - Implemented a secure Next.js API Route for connecting to Google Gemini 3.5 Flash.
  - Included the sanitized dataset (`subset_10k_sanitized.txt`) in the UI `src/data/` folder for Vercel deployment support.
  - Designed a custom, responsive, vanilla CSS front-end with dark mode, gradients, and micro-animations.
  - Set up a `.env.local` configuration for handling the `GEMINI_API_KEY`.
  - Migrated `chatbot-ui` AI route to use Vertex AI and pull ADC securely from Bifrost Vault.
