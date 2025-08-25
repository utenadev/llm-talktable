import sqlite3
import os
from contextlib import contextmanager
from typing import Generator
from config import DB_PATH

# 会話ログテーブル作成SQL
CREATE_CONVERSATION_LOG_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    speaker_name TEXT NOT NULL,
    model_used TEXT NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    is_moderator BOOLEAN NOT NULL DEFAULT FALSE, -- MC発言かどうかのフラグ
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

# 会話セッションメタデータテーブル作成SQL (任意)
CREATE_CONVERSATION_META_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS conversation_meta (
    conversation_id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    participant_a_name TEXT NOT NULL,
    participant_a_model TEXT NOT NULL,
    participant_b_name TEXT NOT NULL,
    participant_b_model TEXT NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


@contextmanager
def get_db_connection(db_path: str = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """データベース接続のコンテキストマネージャー"""
    # データベースファイルのディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str = DB_PATH):
    """データベースとテーブルを初期化する"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(CREATE_CONVERSATION_LOG_TABLE_SQL)
        cursor.execute(CREATE_CONVERSATION_META_TABLE_SQL)


def log_conversation_turn(
    conversation_id: str,
    turn_number: int,
    speaker_name: str,

    model_used: str,
    prompt: str,
    response: str,
    is_moderator: bool = False, # MC発言かどうかのフラグ (デフォルトはFalse)
    db_path: str = DB_PATH,
):
    """1ターン分の会話をデータベースに記録する"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversation_log
            (conversation_id, turn_number, speaker_name, model_used, prompt, response, is_moderator)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, turn_number, speaker_name, model_used, prompt, response, is_moderator),
        )


def log_conversation_meta(
    conversation_id: str,
    topic: str,
    participant_a_name: str,
    participant_a_model: str,
    participant_b_name: str,
    participant_b_model: str,
    db_path: str = DB_PATH,
):
    """会話セッションのメタデータをデータベースに記録する"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO conversation_meta
            (conversation_id, topic, participant_a_name, participant_a_model,
             participant_b_name, participant_b_model)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                topic,
                participant_a_name,
                participant_a_model,
                participant_b_name,
                participant_b_model,
            ),
        )