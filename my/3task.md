# 実装計画 (LLM TalkTable)

- [ ] 0. 重要対応事項
  - リポジトリ llm-talktable 直下にディレクトリllm-talktable があり、そこに .pyなどの実装ファイルがある。この構造で llm-talktable を無くし、リポジトリ直下に実装ファイルを移動して欲しい。

- [ ] 1. プロジェクト基盤とセットアップ
  - Pythonプロジェクトの基本構造を作成
  - 必要な依存関係 (`llm`, `PyYAML`) をインストール
  - 基本的なディレクトリ構造とファイル (`main.py`, `config.py` など) を作成
  - README.ja.md, LICENSE ファイルを作成
  - _要件: 全般_

- [x] 2. 基本的なLLM会話機能の実装
  - `config.py`: YAML設定ファイルとCLI引数からの設定読み込みを実装
  - `database.py`: SQLiteデータベースの初期化と会話ログ記録機能を実装
  - `conversation.py`: 2体のLLMによる往復形式会話のコアロジックを実装
  - `main.py`: アプリケーションのエントリーポイントと全体フローを実装
  - `config.yaml`: 設定例ファイルを作成
  - _要件: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4_
  - 修正・新規追加ファイル: `main.py`, `config.py`, `conversation.py`, `database.py`, `requirements.txt`, `config.yaml`, `README.ja.md`, `LICENSE`

- [ ] 2.1. チャット表示機能の強化
  - `config.py`: `max_turns` を `config.yaml` から読み込む機能を追加
  - `conversation.py`: レスポンステキストのコンソール出力に色を付ける機能を実装
  - `conversation.py`: レスポンステキストのストリーム表示（タイプライター効果）機能を実装（`llm` ライブラリのストリーミングサポートに依存）
  - `requirements.txt`: `colorama` などの必要なライブラリを追加
  - `config.yaml`: `max_turns` の設定項目を追加
  - _要件: 2.1, 2.2, 2.3_
  - 修正・新規追加ファイル: `config.py`, `conversation.py`, `requirements.txt`, `config.yaml`

- [ ] 3. モデレーター(MC)機能の実装
  - `config.py`: MCの設定を読み込む機能を追加
  - `database.py`: MC発言を識別するためのフラグをログテーブルに追加
  - `conversation.py`: 会話ロジックを変更し、MCの開始/ラウンド管理/終了発言を組み込む
  - `config.yaml`: MCの設定例を追加
  - _要件: 3.1, 3.2, 3.3, 3.4_
  - 修正・新規追加ファイル: `config.py`, `database.py`, `conversation.py`, `config.yaml`

- [ ] 4. 会話要約・評価機能の実装
  - `conversation.py`: 会話セッション終了時に、MCが全体の要約を行う機能を追加
  - (オプション) 外部LLMによる会話の客観的評価機能を検討
  - _要件: 4.1, 4.2_

- [ ] 5. ターン制御とカスタムプロンプトの実装
  - `config.py`: カスタムプロンプト設定の読み込みを拡張
  - `conversation.py`: ターン数、LLM呼び出し間の待機時間などを設定可能にする
  - _要件: 5.1, 5.2_

- [ ] 6. テストの実装
  - `conversation.py` ロジックの単体テストを作成
  - 設定読み込み、データベース操作のテストを作成
  - 統合テスト/E2Eテスト計画を検討
  - _要件: 全要件の検証_

- [ ] 7. 最終統合とポリッシュ
  - 全機能の統合と最終テスト
  - README.ja.md の更新
  - サンプル設定ファイル、実行スクリプトの追加
  - _要件: 全要件の最終検証_