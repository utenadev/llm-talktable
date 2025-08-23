# LLM TalkTable

このプロジェクトは、 [`simonw/llm`](https://github.com/simonw/llm) ライブラリを利用して、2つの大規模言語モデル (LLM) 同士に指定されたテーマについて会話させるアプリケーションです。
会話の内容は、アプリケーション専用の SQLite データベースに記録されます。

## 機能

*   **LLM 同士の会話**: 2体のLLMを設定し、往復形式でテーマについて議論させます。
*   **柔軟なモデル選択**: `simonw/llm` がサポートするさまざまなLLMモデル（OpenAI, Anthropic, Google Gemini, ローカルモデルなど）を利用できます。
*   **詳細なログ記録**: 会話のテーマ、参加LLM、各ターンのプロンプトとレスポンスをSQLiteデータベース (`logs/conversation.db`) に保存します。
*   **YAML 設定ファイル**: 参加するLLMの名前、モデルID、ペルソナ（役割/口調）を `config.yaml` で簡単に設定できます。
*   **コマンドライン引数対応**: 会話のテーマは起動時に引数で指定可能です。

## ディレクトリ構造

```
llm_talktable/
├── main.py              # アプリケーションのエントリーポイント
├── config.py            # 設定管理（モデル名、DBパス等）
├── conversation.py      # 会話ロジック（LLM呼び出し、ターン管理）
├── database.py          # データベース操作（ログ記録、読み込み）
├── requirements.txt     # 依存関係
├── config.yaml         # 設定ファイル (例)
└── logs/                # データベースファイルの保存場所
    └── conversation.db  # SQLiteデータベースファイル (実行後に作成)
```

## クイックスタート

### 1. 依存関係のインストール

```bash
# プロジェクトディレクトリに移動
cd llm_talktable

# 必要なライブラリをインストール
pip install -r requirements.txt
```

### 2. LLM APIキーの設定

使用するLLMに応じてAPIキーを設定してください。`simonw/llm` の標準的な方法で設定します。

```bash
# OpenAI の例
llm keys set openai
# -> APIキーを入力

# Anthropic の例
llm keys set anthropic
# -> APIキーを入力
```

ローカルモデル (Ollama, GPT4All など) を使用する場合:

```bash
# 対応する llm プラグインをインストール
llm install llm-ollama # または llm-gpt4all など

# ローカルでモデルを実行可能にしておく (例: ollama pull llama3.2)
```

### 3. 設定ファイルの編集

`config.yaml` を編集して、会話に参加させるLLMを設定します。

```yaml
# config.yaml
topic: "人工知能の未来と社会への影響について"

participants:
  - name: "アリス"
    model: "gpt-4o-mini" # 使用するLLMモデルID
    persona: "あなたは好奇心旺盛で楽観的なAI研究者です。"

  - name: "ボブ"
    model: "claude-3-5-sonnet" # 使用するLLMモデルID
    persona: "あなたは慎重で哲学的なAI倫理学者です。"
```

### 4. アプリケーションの実行

```bash
# 基本実行 (config.yaml の設定を使用)
python main.py

# 会話テーマをコマンドラインから指定
python main.py --topic "宇宙旅行の未来"

# 異なる設定ファイルを使用
python main.py --config my_other_config.yaml
```

実行後、会話内容は `logs/conversation.db` に記録されます。

## データベーススキーマ

会話ログは以下のテーブルに記録されます。

### `conversation_log` (会話ログ)

| カラム名         | 型           | 説明                     |
| :--------------- | :----------- | :----------------------- |
| `id`             | INTEGER      | ログID (主キー)          |
| `conversation_id`| TEXT         | 会話セッションID         |
| `turn_number`    | INTEGER      | ターン番号               |
| `speaker_name`   | TEXT         | 発言者の名前             |
| `model_used`     | TEXT         | 使用されたLLMモデルID    |
| `prompt`         | TEXT         | LLMに送ったプロンプト    |
| `response`       | TEXT         | LLMからのレスポンス      |
| `timestamp`      | DATETIME     | タイムスタンプ (自動)    |

### `conversation_meta` (会話メタデータ)

| カラム名                  | 型       | 説明                           |
| :------------------------ | :------- | :----------------------------- |
| `conversation_id`         | TEXT     | 会話セッションID (主キー)      |
| `topic`                   | TEXT     | 会話テーマ                     |
| `participant_a_name`      | TEXT     | 参加者Aの名前                  |
| `participant_a_model`     | TEXT     | 参加者AのモデルID              |
| `participant_b_name`      | TEXT     | 参加者Bの名前                  |
| `participant_b_model`     | TEXT     | 参加者BのモデルID              |
| `start_time`              | DATETIME | 会話開始時刻 (自動)            |

## ライセンス

Apache License 2.0