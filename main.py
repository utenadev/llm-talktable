#!/usr/bin/env python3
"""
LLM TalkTable アプリケーションのエントリーポイント
"""
import argparse
import sys
import io
from config import get_app_config, AppConfig
from conversation import ConversationManager
from database import init_db
import logging
from logger import setup_logger

# Windows環境で絵文字などを含む出力を可能にするため、標準出力/標準エラー出力のエンコーディングをUTF-8に設定
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ロガーの設定
logger = setup_logger(__name__)


def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        # 1. 設定を読み込む
        app_config = get_app_config()

        # 2. データベースを初期化
        init_db(app_config.db_path)
        logger.info(f"データベースを初期化しました: {app_config.db_path}")

        # 3. 会話マネージャーを作成し、会話を開始
        conversation_manager = ConversationManager(app_config)
        conversation_manager.start_conversation(max_turns=app_config.max_turns, show_prompt=app_config.show_prompt)

    except KeyboardInterrupt:
        # KeyboardInterruptを再送出し、conversation.pyのロジックに処理を委ねる
        logger.info("アプリケーションがユーザーにより中断されました。")
        raise
    except Exception as e:
        logger.error(f"アプリケーション実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()