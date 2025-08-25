import unittest
import os
import tempfile
from config import load_config_from_file, AppConfig, ParticipantConfig

class TestConfig(unittest.TestCase):
    """config.py のテストクラス"""

    def setUp(self):
        """テスト前処理"""
        # 一時的な設定ファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.config_file_path = os.path.join(self.temp_dir, "test_config.yaml")
        
        # テスト用のYAMLコンテンツ
        self.test_yaml_content = """
topic: "Test Topic"
max_turns: 5
llm_wait_time: 2
show_prompt: true

moderator:
  name: "Test MC"
  model: "test-model-mc"
  persona: "Test MC Persona"

participants:
  - name: "Alice"
    model: "test-model-a"
    persona: "Alice's persona"
  - name: "Bob"
    model: "test-model-b"
    persona: "Bob's persona"
"""
        with open(self.config_file_path, 'w', encoding='utf-8') as f:
            f.write(self.test_yaml_content)

    def tearDown(self):
        """テスト後処理"""
        # 一時ファイルを削除
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_config_from_file_success(self):
        """設定ファイルの読み込み成功テスト"""
        config = load_config_from_file(self.config_file_path)
        
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.topic, "Test Topic")
        self.assertEqual(config.max_turns, 5)
        self.assertEqual(config.llm_wait_time, 2)
        self.assertEqual(config.show_prompt, True)
        
        # MCの設定確認
        self.assertIsInstance(config.moderator, ParticipantConfig)
        self.assertEqual(config.moderator.name, "Test MC")
        self.assertEqual(config.moderator.model, "test-model-mc")
        self.assertEqual(config.moderator.persona, "Test MC Persona")
        
        # 参加者の設定確認
        self.assertEqual(len(config.participants), 2)
        self.assertIsInstance(config.participants[0], ParticipantConfig)
        self.assertEqual(config.participants[0].name, "Alice")
        self.assertEqual(config.participants[0].model, "test-model-a")
        self.assertEqual(config.participants[0].persona, "Alice's persona")
        
        self.assertIsInstance(config.participants[1], ParticipantConfig)
        self.assertEqual(config.participants[1].name, "Bob")
        self.assertEqual(config.participants[1].model, "test-model-b")
        self.assertEqual(config.participants[1].persona, "Bob's persona")

    def test_load_config_from_file_not_found(self):
        """設定ファイルが見つからない場合のテスト"""
        with self.assertRaises(FileNotFoundError):
            load_config_from_file("non_existent_file.yaml")

    def test_load_config_from_file_invalid_yaml(self):
        """無効なYAMLコンテンツのテスト"""
        # 参加者の数が不足している場合のテスト
        invalid_yaml_content = """
topic: "Test Topic"
# participants が不足している
"""
        invalid_config_file_path = os.path.join(self.temp_dir, "invalid_config.yaml")
        with open(invalid_config_file_path, 'w', encoding='utf-8') as f:
            f.write(invalid_yaml_content)
        
        with self.assertRaises(ValueError) as context:
            load_config_from_file(invalid_config_file_path)
        
        self.assertIn("participants", str(context.exception))

if __name__ == '__main__':
    unittest.main()