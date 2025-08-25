# LLM TalkTable

This project is an application that uses the [`simonw/llm`](https://github.com/simonw/llm) library to facilitate conversations between two Large Language Models (LLMs) on specified topics. The conversations can range from comedic banter (manzai) to philosophical debates. The content of these conversations is recorded in a dedicated SQLite database.

## Features

*   **Conversations Between LLMs**: Configure two LLMs to discuss a topic in a back-and-forth format.
*   **Flexible Model Selection**: Utilize various LLM models supported by `simonw/llm` (e.g., OpenAI, Anthropic, Google Gemini, local models).
*   **Detailed Logging**: Saves the conversation topic, participating LLMs, prompts, and responses for each turn in an SQLite database (`logs/conversation.db`).
*   **YAML Configuration File**: Easily configure the participating LLMs' names, model IDs, and personas (roles/tone) using `config.yaml`.
*   **Command-Line Arguments**: Specify the conversation topic via command-line arguments at startup.
*   **Colored Console Output**: Each participant's remarks are displayed in different colors for better readability.
*   **Prompt Display Option**: Use the `--show-prompt` option to output the prompts sent to the LLMs to the console.
*   **Processing Indicator**: A spinner is displayed in the console while the LLMs are generating responses, providing a visual cue.
*   **Robust Interrupt Handling**: Allows interrupting the conversation with `Ctrl+C` and gives the user the option to continue or stop.
*   **Unified Logging**: Implemented unified logging functionality using the `logging` module.
*   **Complete Type Hinting**: Added and corrected type hints throughout the code to improve readability and safety.
*   **Enhanced Configuration Validation**: Added functionality to more strictly validate the contents of the configuration file.
*   **Refactored Exception Handling**: Simplified and made exception handling logic more consistent.
*   **Optimized Database Connection**: Centralized database connection and transaction management using context managers.

## Directory Structure

```
├── main.py              # Application entry point
├── config.py            # Configuration management (model names, DB paths, etc.)
├── conversation.py      # Conversation logic (LLM calls, turn management)
├── database.py          # Database operations (logging, reading)
├── requirements.txt     # Dependencies
├── config.yaml         # Configuration file (example)
└── logs/                # Location to save database files
    └── conversation.db  # SQLite database file (created after execution)
```

## Quick Start

### 1. Install Dependencies

```bash
# Move to the project directory (might not be necessary if already at the root)
# cd llm-talktable

# Install required libraries
pip install -r requirements.txt
```

### 2. Set LLM API Keys

Set the API keys for the LLMs you plan to use, following the standard method for `simonw/llm`.

```bash
# Example for OpenAI
llm keys set openai
# -> Enter API key

# Example for Anthropic
llm keys set anthropic
# -> Enter API key
```

For local models (Ollama, GPT4All, etc.):

```bash
# Install the corresponding llm plugin
llm install llm-ollama # or llm-gpt4all etc.

# Ensure the local model is runnable (e.g., ollama pull llama3.2)
```

### 3. Edit Configuration File

Edit `config.yaml` to configure the LLMs participating in the conversation.

```yaml
# config.yaml
topic: "The Future of Artificial Intelligence and its Impact on Society"

participants:
  - name: "Alice"
    model: "gpt-4o-mini" # LLM model ID to use
    persona: "You are a curious and optimistic AI researcher."

  - name: "Bob"
    model: "claude-3-5-sonnet" # LLM model ID to use
    persona: "You are a cautious and philosophical AI ethicist."
```

### 4. Run the Application

```bash
# Basic run (uses settings from config.yaml)
python main.py

# Specify the conversation topic from the command line
python main.py --topic "The Future of Space Travel"

# Use a different configuration file
python main.py --config my_other_config.yaml
```

After execution, the conversation content will be recorded in `logs/conversation.db`.

## Database Schema

Conversation logs are recorded in the following tables.

### `conversation_log` (Conversation Logs)

| Column Name       | Type         | Description                  |
| :---------------- | :----------- | :--------------------------- |
| `id`              | INTEGER      | Log ID (Primary Key)         |
| `conversation_id` | TEXT         | Conversation Session ID      |
| `turn_number`     | INTEGER      | Turn Number                  |
| `speaker_name`    | TEXT         | Name of the Speaker          |
| `model_used`      | TEXT         | LLM Model ID Used            |
| `prompt`          | TEXT         | Prompt Sent to LLM           |
| `response`        | TEXT         | Response from LLM            |
| `timestamp`       | DATETIME     | Timestamp (Automatic)        |

### `conversation_meta` (Conversation Metadata)

| Column Name               | Type     | Description                        |
| :------------------------ | :------- | :--------------------------------- |
| `conversation_id`         | TEXT     | Conversation Session ID (Primary)  |
| `topic`                   | TEXT     | Conversation Topic                 |
| `participant_a_name`      | TEXT     | Name of Participant A              |
| `participant_a_model`     | TEXT     | Model ID of Participant A          |
| `participant_b_name`      | TEXT     | Name of Participant B              |
| `participant_b_model`     | TEXT     | Model ID of Participant B          |
| `start_time`              | DATETIME | Conversation Start Time (Automatic)|

## Interrupt Handling

During application execution, especially while an LLM is generating a response, you can interrupt the conversation by pressing `Ctrl+C`.

- When an LLM's response generation is interrupted, a message `--- Conversation Interrupted ---` will be displayed.
- Following this, you'll see a prompt: `Do you want to end the conversation? (S[top] to end, C[ontinue] to continue):`.
  - Enter `S` or `stop` to end the conversation and exit the program.
  - Enter `C` or `continue` to resume processing the interrupted turn.

This feature allows for flexible control of the conversation without waiting for long-running LLM calls.

## License

Apache License 2.0