#!/usr/bin/env python3
"""
LLM TalkTable: LLM同士がテーマについて会話するアプリケーション
"""
import sys
from config import get_app_config
from database import init_db
from conversation import ConversationManager


def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        # 1. 設定を読み込む
        app_config = get_app_config()

        # 2. データベースを初期化
        init_db(app_config.db_path)
        print(f"データベースを初期化しました: {app_config.db_path}")

        # 3. 会話マネージャーを作成し、会話を開始
        conversation_manager = ConversationManager(app_config)
        conversation_manager.start_conversation(max_turns=app_config.max_turns, show_prompt=app_config.show_prompt)

    except KeyboardInterrupt:
        # KeyboardInterruptを再送出し、conversation.pyのロジックに処理を委ねる
        raise
    except Exception as e:
        print(f"アプリケーション実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()