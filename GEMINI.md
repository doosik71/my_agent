# Gemini CLI Memories for my_agent Project

This file serves as a dedicated place to store project-specific instructions, conventions, and important notes for the Gemini CLI agent.

## Project Conventions:

- **Package Management:** This project exclusively uses `uv` for package management. All dependencies are managed via `pyproject.toml`. The `requirements.txt` file is NOT used and should be ignored. Always use `uv sync` after modifying `pyproject.toml` to update dependencies and `uv.lock`.
- **Telegram Bot Access:** The Telegram bot (`src/telegram_bot.py`) is configured to allow access only to users specified in the `TELEGRAM_AUTHORIZED_USERS` environment variable in the `.env` file. Refer to `README.md` for instructions on how to obtain user IDs.
