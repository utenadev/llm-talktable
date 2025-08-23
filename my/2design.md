# 設計文書 (LLM TalkTable)

## 概要

PythonベースのLLM会話アプリケーションです。`simonw/llm`ライブラリを使用して複数のLLMとやり取りし、会話の進行を管理します。会話ログはSQLiteデータベースに保存され、モデレーター（MC）が会話の構造化と品質向上を図ります。YAML設定ファイルとCLI引数で動作をカスタマイズできます。

## アーキテクチャ

### 技術スタック

- **言語**: Python 3.x
- **LLMライブラリ**: `simonw/llm`
- **設定ファイル**: YAML
- **データベース**: SQLite (標準ライブラリ `sqlite3`)
- **依存関係管理**: `requirements.txt` (pip)

### アプリケーション構造

```
├── main.py              # アプリケーションのエントリーポイント
├── config.py            # 設定管理（モデル名、DBパス等）
├── conversation.py      # 会話ロジック（LLM呼び出し、ターン管理）
├── database.py          # データベース操作（ログ記録、読み込み）
├── requirements.txt     # 依存関係
├── config.yaml         # 設定ファイル (例)
├── README.ja.md        # ドキュメント
├── LICENSE             # ライセンス
└── logs/                # データベースファイルの保存場所
    └── conversation.db  # SQLiteデータベースファイル
```

## コンポーネントとインターフェース

### 主要コンポーネント

#### 1. main.py

- アプリケーションの起動ポイント。
- `config.py` から設定を読み込む。
- `database.py` を初期化する。
- `conversation.py` の `ConversationManager` を作成し、会話を開始する。

#### 2. config.py

- `config.yaml` とコマンドライン引数から設定を読み込む `AppConfig` クラスと関数を提供。
- `ParticipantConfig` クラスで、各LLM参加者の設定（名前、モデル、ペルソナ）を保持。

#### 3. conversation.py

- 会話のコアロジックを実装する `ConversationManager` クラス。
- LLMの呼び出し、ターン管理（LLM-A <-> LLM-B <-> MC <-> ...）、プロンプト構築、レスポンス処理を行う。
- データベースへのログ記録を `database.py` を介して行う。

#### 4. database.py

- SQLiteデータベースの初期化（テーブル作成）を行う関数を提供。
- 会話ログ (`conversation_log`) と会話メタデータ (`conversation_meta`) を記録する関数を提供。
- MCフラグなどの拡張情報を含むログスキーマを定義。

### インターフェース定義

```python
# config.py
class ParticipantConfig:
    name: str
    model: str
    persona: str

class AppConfig:
    topic: str
    participants: list[ParticipantConfig] # 最初の2つが会話参加者
    # MCの設定も含む可能性あり

# conversation.py
class ConversationManager:
    def __init__(self, config: AppConfig):
        pass

    def start_conversation(self, max_turns: int = 10):
        # 会話を開始し、MCロジックを組み込む
        pass

# database.py
def init_db(db_path: str):
    # データベースとテーブルを初期化
    pass

def log_conversation_turn(...):
    # 1ターン分のログを記録
    pass

def log_conversation_meta(...):
    # 会話メタデータを記録
    pass
```

## データモデル

### 会話ログ (`conversation_log` テーブル)

| カラム名         | 型           | 説明                     |
| :--------------- | :----------- | :----------------------- |
| `id`             | INTEGER      | ログID (主キー)          |
| `conversation_id`| TEXT         | 会話セッションID         |
| `turn_number`    | INTEGER      | ターン番号               |
| `speaker_name`   | TEXT         | 発言者の名前             |
| `model_used`     | TEXT         | 使用されたLLMモデルID    |
| `prompt`         | TEXT         | LLMに送ったプロンプト    |
| `response`       | TEXT         | LLMからのレスポンス      |
| `is_moderator`   | BOOLEAN      | 発言者がMCかどうか       |
| `timestamp`      | DATETIME     | タイムスタンプ (自動)    |

### 会話メタデータ (`conversation_meta` テーブル)

| カラム名                  | 型       | 説明                           |
| :------------------------ | :------- | :----------------------------- |
| `conversation_id`         | TEXT     | 会話セッションID (主キー)      |
| `topic`                   | TEXT     | 会話テーマ                     |
| `participant_a_name`      | TEXT     | 参加者Aの名前                  |
| `participant_a_model`     | TEXT     | 参加者AのモデルID              |
| `participant_b_name`      | TEXT     | 参加者Bの名前                  |
| `participant_b_model`     | TEXT     | 参加者BのモデルID              |
| `moderator_name`          | TEXT     | MCの名前 (nullable)            |
| `moderator_model`         | TEXT     | MCのモデルID (nullable)        |
| `start_time`              | DATETIME | 会話開始時刻 (自動)            |

## エラーハンドリング

### LLM呼び出しエラー

- `llm` ライブラリの例外（ネットワークエラー、認証エラー、モデル未指定など）をキャッチ。
- エラー内容をコンソールに出力し、該当ターンのログにエラー情報を記録。
- 致命的なエラーの場合はアプリケーションを終了、一時的なエラーの場合は再試行オプションを検討。

### 設定ファイル読み込みエラー

- `config.yaml` の構文エラー、必須項目の欠落を検出。
- 明確なエラーメッセージを表示してアプリケーションを終了。

### データベースエラー

- SQLiteファイルの書き込み権限、ディスク容量不足などのエラーをハンドリング。
- データベース操作時の例外をキャッチし、ログに出力。

### ユーザーによる中断 (`Ctrl+C`)

- `KeyboardInterrupt` をキャッチし、ユーザーに継続/終了の選択肢を提示。
- 選択に応じて処理を継続または終了。

## テスト戦略

### 単体テスト

- `config.py` の設定読み込みロジック。
- `database.py` のデータベース操作関数（モックDBを使用）。
- `conversation.py` のプロンプト構築ロジック（LLM呼び出し部分はモック）。

### 統合テスト

- 設定ファイル読み込み -> データベース初期化 -> 会話開始 までの基本的なフロー。
- MC機能が正しく発言されているか（ログ内容の検証）。

### E2Eテスト

- 実際のLLM（モックサーバーまたは特定のローカルモデル）を使用して、アプリケーション全体の動作を検証。
- 会話ログが期待通りにデータベースに記録されているかを確認。

## 実装詳細

### 会話フロー（MC機能追加後）

1.  `main.py` が `config.py` を通じて設定を読み込む。
2.  `database.py` がDBを初期化。
3.  `ConversationManager` が作成され、`start_conversation` を呼び出す。
4.  `start_conversation`:
    *   MCが会話開始アナウンスをする（ターン0）。
    *   参加者Aがテーマに対して発言（ターン1）。
    *   参加者Bがそれに対して返答（ターン2）。
    *   MCがラウンド1を要約（ターン3）。
    *   参加者Aが続き（ターン4）... と繰り返し。
    *   指定ラウンド数終了後、MCが会話を締めくくる。
5.  各ターンで、`conversation.py` がLLMを呼び出し、結果を `database.py` に記録。

### レスポンシブ対応

- このアプリケーションはCLIベースのため、タッチ/GUI対応は不要。

### アクセシビリティ

- CLI出力は標準的なテキスト形式。将来、色付き出力や構造化ログを検討。

## パフォーマンス考慮事項

### APIレート制限

- 各LLM呼び出しの間に `time.sleep()` による短い待機時間を設けることで、APIレート制限を考慮。

### メモリ管理

- 大きなテキストを処理する可能性があるが、Pythonのガベージコレクションに任せる。
- ログの蓄積によるメモリ/ディスク使用量は、長期実行時に注意。

### 読み込み最適化

- 設定ファイルやデータベース接続は起動時一度だけ。