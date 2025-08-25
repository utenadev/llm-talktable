# LLM TalkTable

このプロジェクトは、 [`simonw/llm`](https://github.com/simonw/llm) ライブラリを利用して、2つの大規模言語モデル (LLM) 同士に指定されたテーマについて会話させるアプリケーションです。会話は漫才から哲学的ディベートまでです。
会話の内容は、アプリケーション専用の SQLite データベースに記録されます。

## 機能

*   **LLM 同士の会話**: 2体のLLMを設定し、往復形式でテーマについて議論させます。
*   **柔軟なモデル選択**: `simonw/llm` がサポートするさまざまなLLMモデル（OpenAI, Anthropic, Google Gemini, ローカルモデルなど）を利用できます。
*   **詳細なログ記録**: 会話のテーマ、参加LLM、各ターンのプロンプトとレスポンスをSQLiteデータベース (`logs/conversation.db`) に保存します。
*   **YAML 設定ファイル**: 参加するLLMの名前、モデルID、ペルソナ（役割/口調）を `config.yaml` で簡単に設定できます。
*   **コマンドライン引数対応**: 会話のテーマは起動時に引数で指定可能です。
*   **色付きコンソール出力**: 各参加者の発言は異なる色で表示され、視認性が向上します。
*   **プロンプト表示オプション**: `--show-prompt` オプションで、LLMに送信されたプロンプトをコンソールに出力できます。
*   **ストリーミング表示（タイプライター効果）**: LLMからのレスポンスは、生成されるにつれて逐次コンソールに表示されます。
*   **処理中インジケーター**: LLMが応答を生成している間、コンソールにスピナーが表示され、処理中であることが視覚的に示されます。
*   **モデレーター (MC) 機能**: 会話の開始、ラウンド管理、終了をMCがアナウンスします。
*   **堅牢なインタラプト処理**: `Ctrl+C` による会話の中断と、ユーザーによる継続/終了選択が可能です。
*   **統一的なロギング**: `logging` モジュールを使用した統一的なログ出力機能を実装しました。
*   **型ヒントの完全化**: コード全体に型ヒントを追加・修正し、コードの可読性と安全性を向上させました。
*   **設定バリデーションの強化**: 設定ファイルの内容をより厳密に検証する機能を追加しました。
*   **例外処理の整理**: 例外処理のロジックを簡潔化し、一貫性を高めました。
*   **データベース接続の最適化**: コンテキストマネージャーを使用してデータベース接続とトランザクション管理を一元化しました。
*   **カスタムプロンプト設定**: 会話の最大ターン数、LLM呼び出し間の待機時間などを `config.yaml` で設定可能です。
*   **ユニットテスト**: `config.py`, `database.py`, `conversation.py` の主要機能に対するユニットテストを実装しました。

## ディレクトリ構造

```
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
# プロジェクトディレクトリに移動 (既にルートにあるため不要かもしれません)
# cd llm-talktable

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

`config.yaml` を編集して、会話に参加させるLLMとMCを設定します。

```yaml
# config.yaml
# 会話するテーマ (コマンドライン引数でも指定可)
topic: "人工知能の未来と社会への影響について"

# 会話の最大ターン数
max_turns: 10

# LLM呼び出し間の待機時間 (秒)
llm_wait_time: 1

# プロンプトをコンソールに出力するかどうか (デフォルト: false)
show_prompt: false

# モデレーター(MC)の設定
moderator:
  name: "MC"
  model: "gpt-4o-mini" # 使用するLLMモデルID (llmが認識できるもの)
  persona: "あなたはこの会話のモデレーターです。会話のテーマ紹介、参加者の紹介、ラウンドの管理、会話の要約と締めくくりを行います。"

# 会話参加者設定
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
| `is_moderator`   | BOOLEAN      | MCの発言かどうか         |
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

## インタラプト処理

アプリケーションの実行中、特にLLMが応答を生成している最中に `Ctrl+C` を押すことで、会話を中断できます。

- LLMの応答生成が中断されると、`--- 会話が中断されました ---` というメッセージが表示されます。
- その後、`会話を終了しますか？ (S[top] で終了, C[ontinue] で継続):` というプロンプトが表示されるので、
  - `S` または `stop` と入力すると、会話が終了し、プログラムが終了します。
  - `C` または `continue` と入力すると、中断されたターンの処理が再開されます。

この機能により、長時間かかるLLMの呼び出しを待たずに、柔軟に会話をコントロールできます。

## ライセンス

Apache License 2.0