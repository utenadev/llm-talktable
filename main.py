#!/usr/bin/env python3
"""
LLM TalkTable アプリケーションのエントリーポイント
"""
import argparse
import sys
import io
import os
from config import get_app_config, AppConfig
from conversation import ConversationManager
from database import init_db
import logging
from colorama import init as colorama_init

# coloramaを初期化
colorama_init()

# Windows環境で絵文字などを含む出力を可能にするため、標準出力/標準エラー出力のエンコーディングをUTF-8に設定
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def setup_logger(log_level_str: str) -> logging.Logger:
    """ロガーをセットアップする"""
    # ルートロガーのハンドラをクリア
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    logger = logging.getLogger("__main__")  # ロガー名を "__main__" に固定
    logger.setLevel(logging.DEBUG)  # ロガー自体のレベルはDEBUGに設定

    # 既存のハンドラをクリア
    if logger.hasHandlers():
        logger.handlers.clear()

    # コンソールハンドラ (常に追加)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter('%(levelname)s:%(name)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # log_level_str に基づいてコンソールハンドラのレベルを設定
    if log_level_str.lower() == "debug":
        console_handler.setLevel(logging.DEBUG)
    elif log_level_str.lower() == "info":
        console_handler.setLevel(logging.INFO)
    else:  # "none" or others
        console_handler.setLevel(logging.CRITICAL) # CRITICAL以上のみ出力 -> 実質出力なし
    
    logger.addHandler(console_handler)

    # ファイルハンドラ (log_levelがinfoまたはdebugの場合のみ追加)
    if log_level_str.lower() in ["info", "debug"]:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        if log_level_str.lower() == "debug":
            file_handler.setLevel(logging.DEBUG)
        else:  # "info"
            file_handler.setLevel(logging.INFO)
            
        logger.addHandler(file_handler)

    return logger


def main():
    """アプリケーションのメインエントリーポイント"""
    try:
        # 1. 設定を読み込む
        app_config = get_app_config()
        
        # 2. ロガーをセットアップ
        logger = setup_logger(app_config.log_level)

        # 3. データベースを初期化
        init_db(app_config.db_path)
        logger.info(f"データベースを初期化しました: {app_config.db_path}")

        # 4. 会話マネージャーを作成し、会話を開始
        conversation_manager = ConversationManager(app_config, app_config.log_level)
        conversation_manager.start_conversation(
            max_turns=app_config.max_turns, 
            show_prompt=app_config.show_prompt,
            show_summary=app_config.show_summary
        )

    except KeyboardInterrupt:
        # KeyboardInterruptを再送出し、conversation.pyのロジックに処理を委ねる
        if 'logger' in locals():
            logger.info("アプリケーションがユーザーにより中断されました。")
        else:
            print("アプリケーションがユーザーにより中断されました。")
        raise
    except Exception as e:
        if 'logger' in locals():
            logger.error(f"アプリケーション実行中にエラーが発生しました: {e}")
        else:
            print(f"アプリケーション実行中にエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()