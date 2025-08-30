# LLM TalkTable Project Layout

## Overview
This project enables two Large Language Models (LLMs) to hold a conversation on a specified topic using the `simonw/llm` library. Conversation logs are stored in a dedicated SQLite database.

## Key Files and Directories

- `main.py`: Application entry point.
- `config.py`: Handles loading configuration from `config.yaml` and command-line arguments.
- `conversation.py`: Core logic for managing the LLM conversation loop.
- `database.py`: Module for initializing the SQLite database and logging conversation turns.
- `requirements.txt`: Lists Python dependencies (e.g., `llm`, `PyYAML`).
- `config.yaml`: Example configuration file defining conversation topic and participant LLMs/personas.
- `README.ja.md`: Project documentation in Japanese.
- `LICENSE`: Project license (Apache License 2.0).
- `logs/`: Directory for the SQLite database file (`conversation.db`).
- `personas/`: Directory containing participant persona files (e.g., `alice_persona.txt`, `karen_persona.txt`).
- `my/`: Directory containing project management files and task tracking.
- `.serena/`: Directory for Serena memory files tracking project progress and structure.
- `tests/`: Directory for unit tests and test utilities.

## Database Structure
- `conversation_log` table: Stores all conversation turns with fields for conversation_id, turn_number, speaker_name, model_used, prompt, response, is_moderator flag, and timestamp.
- `conversation_meta` table: Stores metadata about conversation sessions.

## Key Features Implemented
- **Moderator (MC) System**: Automated conversation management with round summaries and session wrap-up.
- **Multi-LLM Support**: Integration with various LLM providers (Gemini, OpenRouter) through the `simonw/llm` library.
- **Persona System**: Character-based conversation participants with distinct personalities loaded from external files.
- **Visual Feedback**: Spinner indicators during LLM processing and colored console output for different speakers.
- **Robust Logging**: Complete conversation history saved to SQLite database with full metadata.