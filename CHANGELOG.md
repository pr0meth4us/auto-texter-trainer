# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added
- **Synchronous Config Pull**: Embedded Bifrost SDK directly into `bifrost_config.py` to synchronously pull and inject API keys straight into local memory at boot, removing the need for `bifrost_local.py` or cache threads.
- Created `chatbot-ui`, a Next.js web application for interacting with the AI Persona Clone.
  - Implemented a secure Next.js API Route for connecting to Google Gemini 3.5 Flash.
  - Included the sanitized dataset (`subset_10k_sanitized.txt`) in the UI `src/data/` folder for Vercel deployment support.
  - Designed a custom, responsive, vanilla CSS front-end with dark mode, gradients, and micro-animations.
  - Set up a `.env.local` configuration for handling the `GEMINI_API_KEY`.
