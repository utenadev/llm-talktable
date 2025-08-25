#!/usr/bin/env python3
"""
LLM TalkTable テストランナー
"""
import sys
import os
import unittest

# プロジェクトルートディレクトリを Python パスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

if __name__ == '__main__':
    # テストスイートを作成
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')

    # テストランナーを作成して実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # テスト結果に基づいて終了コードを設定
    sys.exit(not result.wasSuccessful())