# 結合テスト/E2Eテスト計画 (LLM TalkTable)

## 目的

LLM TalkTable アプリケーションの主要機能（LLM会話、MC機能、設定読み込み、データベースログ）が正しく連携し、期待通りに動作することを検証する。

## テスト環境

- OS: Windows/Linux/macOS (主要OS)
- Python バージョン: 3.8以上
- `simonw/llm` がインストールされ、少なくとも1つのLLMモデル（例: `llm-markov` プラグイン）が利用可能。
- SQLite データベース（Python標準ライブラリ）

## テストケース

### テストケース 1: 基本的なLLM会話とMC機能

**目的:** 2体のLLMがMCの進行のもとで会話できることを確認する。

**前提条件:**

- `test_config_basic.yaml` が存在し、以下の内容を含む:
  ```yaml
  topic: "Test topic for basic conversation"
  participants:
    - name: "LLM_A"
      model: "markov" # テスト用のシンプルなモデル
      persona: "You are a straightforward AI."
    - name: "LLM_B"
      model: "markov"
      persona: "You are a slightly skeptical AI."
    - name: "MC"
      model: "markov"
      persona: "You are a neutral moderator."
  ```

**手順:**

1.  `llm-markov` プラグインがインストールされていることを確認する。
2.  上記の `test_config_basic.yaml` を使用してアプリケーションを実行する。
    ```bash
    python main.py --config test_config_basic.yaml
    ```
3.  アプリケーションが正常に起動し、会話が開始されることを確認する（コンソール出力）。
4.  会話が進行し（最低3ラウンド）、MCの発言（開始、ラウンド要約、終了）が含まれていることを確認する（コンソール出力）。
5.  会話が正常に終了することを確認する。
6.  `logs/conversation.db` データベースが作成/更新されていることを確認する。
7.  `conversation_log` テーブルをクエリし、以下のことを検証する:
    *   レコードが存在する。
    *   `speaker_name` に "LLM_A", "LLM_B", "MC" が含まれる。
    *   `is_moderator` フラグがMCの発言には `1` (True)、それ以外には `0` (False) になっている。
    *   `turn_number` が連続している（MC含む）。
8.  `conversation_meta` テーブルをクエリし、会話のメタデータ（テーマ、参加者名/モデル）が正しく記録されていることを検証する。

**期待結果:**

- アプリケーションはエラーなく実行され、会話ログがデータベースに正しく記録される。

---

### テストケース 2: 設定ファイルのバリデーション

**目的:** 不正な設定ファイルが与えられた場合に、アプリケーションが適切にエラー処理を行うことを確認する。

**前提条件:**

- `test_config_invalid.yaml` が存在し、以下の不正な内容を含む:
  ```yaml
  # topic が欠落
  participants:
    - name: "OnlyOneParticipant"
      model: "markov"
      persona: "Test"
    # MCが欠落
  ```

**手順:**

1.  上記の `test_config_invalid.yaml` を使用してアプリケーションを実行する。
    ```bash
    python main.py --config test_config_invalid.yaml
    ```
2.  アプリケーションが起動直後にエラーを出力し、終了することを確認する（終了コードもチェック）。

**期待結果:**

- アプリケーションは `"設定ファイルに 'topic' が指定されていません。"` や `"会話には少なくとも2人の 'participants' が必要です。"` のような明確なエラーメッセージを表示し、非ゼロの終了コードで終了する。

---

### テストケース 3: ユーザーによる中断処理 (`Ctrl+C`)

**目的:** 会話中の `Ctrl+C` インタラプトが正しく処理され、ユーザーの選択（継続/停止）が機能することを確認する。

**前提条件:**

- テストケース1と同様の有効な設定ファイル。

**手順:**

1.  有効な設定ファイルでアプリケーションを実行開始する。
2.  会話が開始されたことを確認後、会話中に `Ctrl+C` を送信する。
3.  `"--- 会話が中断されました ---"` および `"会話を終了しますか？ ..."` のプロンプトが表示されることを確認する。
4.  `S` (Stop) を入力する。アプリケーションが終了することを確認する。
5.  別のセッションで、再度アプリケーションを実行し、今度は `C` (Continue) を入力する。
6.  会話が中断されずに継続することを確認する（または、同じターンが再試行されること）。

**期待結果:**

- `Ctrl+C` によるインタラプトがキャッチされ、ユーザーの入力に応じて会話が停止または継続する。

---

### テストケース 4: 無効なLLMモデル指定

**目的:** 設定ファイルで指定されたLLMモデルが存在しない場合のエラー処理を確認する。

**前提条件:**

- `test_config_invalid_model.yaml` が存在し、存在しないモデルを指定:
  ```yaml
  topic: "Test with invalid model"
  participants:
    - name: "A"
      model: "non-existent-model-id"
      persona: "Test"
    - name: "B"
      model: "markov"
      persona: "Test"
    - name: "MC"
      model: "markov"
      persona: "Test"
  ```

**手順:**

1.  上記の `test_config_invalid_model.yaml` を使用してアプリケーションを実行する。
    ```bash
    python main.py --config test_config_invalid_model.yaml
    ```
2.  アプリケーションが起動直後に、`"モデル 'non-existent-model-id' の取得に失敗しました"` のようなエラーメッセージを表示し、終了することを確認する。

**期待結果:**

- 存在しないLLMモデルを指定した場合、アプリケーションは明確なエラーを表示して終了する。

---

## 自動化について

これらのテストケースは、現時点では手動で実行することを想定しています。将来的に、`pytest` やサブプロセス制御を用いた自動化を検討できます。