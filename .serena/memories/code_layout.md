# LLM TalkTable Project Layout

## Overview
This project enables two Large Language Models (LLMs) to hold a conversation on a specified topic using the `simonw/llm` library. Conversation logs are stored in a dedicated SQLite database.

## Key Files and Directories

- `llm_talktable/`: Main project directory.
  - `main.py`: Application entry point.
  - `config.py`: Handles loading configuration from `config.yaml` and command-line arguments.
  - `conversation.py`: Core logic for managing the LLM conversation loop.
  - `database.py`: Module for initializing the SQLite database and logging conversation turns.
  - `requirements.txt`: Lists Python dependencies (e.g., `llm`, `PyYAML`).
  - `config.yaml`: Example configuration file defining conversation topic and participant LLMs/personas.
  - `README.ja.md`: Project documentation in Japanese.
  - `LICENSE`: Project license (Apache License 2.0).
  - `logs/`: Directory for the SQLite database file (`conversation.db`).