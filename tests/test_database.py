import unittest
import os
import tempfile
import sqlite3
from database import init_db, log_conversation_turn, log_conversation_meta, get_db_connection

class TestDatabase(unittest.TestCase):
    """database.py のテストクラス"""

    def setUp(self):
        """テスト前処理"""
        # 一時的なデータベースファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_conversation.db")
        
    def tearDown(self):
        """テスト後処理"""
        # 一時ファイルを削除
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_db(self):
        """データベース初期化テスト"""
        init_db(self.db_path)
        
        # テーブルが正しく作成されていることを確認
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            
            # conversation_log テーブルの存在確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_log'")
            self.assertIsNotNone(cursor.fetchone())
            
            # conversation_meta テーブルの存在確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversation_meta'")
            self.assertIsNotNone(cursor.fetchone())
            
            # conversation_log テーブルのスキーマ確認
            cursor.execute("PRAGMA table_info(conversation_log)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            expected_columns = ['id', 'conversation_id', 'turn_number', 'speaker_name', 'model_used', 'prompt', 'response', 'is_moderator', 'timestamp']
            for col in expected_columns:
                self.assertIn(col, column_names)
                
            # conversation_meta テーブルのスキーマ確認
            cursor.execute("PRAGMA table_info(conversation_meta)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            expected_columns = ['conversation_id', 'topic', 'participant_a_name', 'participant_a_model', 'participant_b_name', 'participant_b_model', 'start_time']
            for col in expected_columns:
                self.assertIn(col, column_names)

    def test_log_conversation_turn(self):
        """会話ターンログ記録テスト"""
        init_db(self.db_path)
        
        # テストデータ
        conversation_id = "test-conversation-id"
        turn_number = 1
        speaker_name = "Alice"
        model_used = "test-model-a"
        prompt = "Test prompt"
        response = "Test response"
        is_moderator = False
        
        # ログを記録
        log_conversation_turn(
            conversation_id=conversation_id,
            turn_number=turn_number,
            speaker_name=speaker_name,
            model_used=model_used,
            prompt=prompt,
            response=response,
            is_moderator=is_moderator,
            db_path=self.db_path
        )
        
        # ログが正しく記録されていることを確認
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversation_log WHERE conversation_id=?", (conversation_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[1], conversation_id) # conversation_id
            self.assertEqual(row[2], turn_number)     # turn_number
            self.assertEqual(row[3], speaker_name)    # speaker_name
            self.assertEqual(row[4], model_used)      # model_used
            self.assertEqual(row[5], prompt)          # prompt
            self.assertEqual(row[6], response)        # response
            self.assertEqual(row[7], is_moderator)    # is_moderator

    def test_log_conversation_meta(self):
        """会話メタデータログ記録テスト"""
        init_db(self.db_path)
        
        # テストデータ
        conversation_id = "test-conversation-id"
        topic = "Test Topic"
        participant_a_name = "Alice"
        participant_a_model = "test-model-a"
        participant_b_name = "Bob"
        participant_b_model = "test-model-b"
        
        # ログを記録
        log_conversation_meta(
            conversation_id=conversation_id,
            topic=topic,
            participant_a_name=participant_a_name,
            participant_a_model=participant_a_model,
            participant_b_name=participant_b_name,
            participant_b_model=participant_b_model,
            db_path=self.db_path
        )
        
        # ログが正しく記録されていることを確認
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM conversation_meta WHERE conversation_id=?", (conversation_id,))
            row = cursor.fetchone()
            
            self.assertIsNotNone(row)
            self.assertEqual(row[0], conversation_id)         # conversation_id
            self.assertEqual(row[1], topic)                   # topic
            self.assertEqual(row[2], participant_a_name)      # participant_a_name
            self.assertEqual(row[3], participant_a_model)     # participant_a_model
            self.assertEqual(row[4], participant_b_name)      # participant_b_name
            self.assertEqual(row[5], participant_b_model)     # participant_b_model

if __name__ == '__main__':
    unittest.main()