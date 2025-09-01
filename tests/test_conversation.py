import unittest
from unittest.mock import patch, MagicMock
import logging
from config import AppConfig, ParticipantConfig
from conversation import ConversationManager

class TestConversationManager(unittest.TestCase):
    """conversation.py のテストクラス"""

    def setUp(self):
        """テスト前処理"""
        # テスト用のロガーを作成 (出力を無効化)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.CRITICAL + 1)

        # テスト用のAppConfigを作成
        self.participants = [
            ParticipantConfig("Alice", "test-model-a", "Alice's persona"),
            ParticipantConfig("Bob", "test-model-b", "Bob's persona")
        ]
        self.moderator = ParticipantConfig("MC", "test-model-mc", "MC's persona")
        self.config = AppConfig(
            topic="Test Topic",
            participants=self.participants,
            moderator=self.moderator,
            max_turns=2,
            llm_wait_time=0, # テスト時は待機時間を0にする
            show_prompt=False
        )

    @patch('conversation.llm.get_model')
    def test__get_llm_model_success(self, mock_get_model):
        """_get_llm_model メソッドの成功テスト"""
        # モックの設定
        mock_model = MagicMock()
        mock_get_model.return_value = mock_model
        
        # ConversationManagerのインスタンスを作成
        cm = ConversationManager(self.config, self.logger)
        
        # テスト
        model = cm._get_llm_model(self.participants[0])
        
        # 検証
        mock_get_model.assert_called_once_with("test-model-a")
        self.assertEqual(model, mock_model)

    @patch('conversation.llm.get_model')
    def test__get_llm_model_failure(self, mock_get_model):
        """_get_llm_model メソッドの失敗テスト"""
        # モックの設定
        mock_get_model.side_effect = Exception("Model not found")
        
        # ConversationManagerのインスタンスを作成
        cm = ConversationManager(self.config, self.logger)
        
        # テストと検証
        with self.assertRaises(ValueError) as context:
            cm._get_llm_model(self.participants[0])
        
        self.assertIn("モデル 'test-model-a' の取得に失敗しました", str(context.exception))

    @patch('conversation.log_conversation_turn')
    @patch('conversation.llm.get_model')
    def test__run_single_turn(self, mock_get_model, mock_log_conversation_turn):
        """_run_single_turn メソッドのテスト"""
        # モックの設定
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text.return_value = "Test response"
        # ストリーミングレスポンスをシミュレート
        mock_response.__iter__.return_value = iter(["Test ", "response"])
        mock_model.prompt.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # ConversationManagerのインスタンスを作成
        cm = ConversationManager(self.config, self.logger)
        cm.conversation_id = "test-conversation-id"
        cm.turn_count = 1
        
        # テスト
        response_text = cm._run_single_turn(
            speaker=self.participants[0],
            prompt_text="Test prompt",
            show_prompt=False
        )
        
        # 検証
        mock_get_model.assert_called_once_with("test-model-a")
        mock_model.prompt.assert_called_once()
        # ストリーミングレスポンスの処理が行われたことを確認
        self.assertEqual(response_text, "Test response")
        mock_log_conversation_turn.assert_called_once_with(
            conversation_id="test-conversation-id",
            turn_number=1,
            speaker_name="Alice",
            model_used="test-model-a",
            prompt="Test prompt",
            response="Test response",
            is_moderator=False
        )

if __name__ == '__main__':
    unittest.main()