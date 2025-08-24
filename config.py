import argparse
import os

# Use yaml_include for !include tag support
import yaml_include # <- yaml_include パッケージをインポート
import yaml


CONFIG_FILE_PATH = "config.yaml"
DB_PATH = os.path.join("logs", "conversation.db")


class ParticipantConfig:
    """会話参加者の設定を保持するクラス"""

    def __init__(self, name: str, model: str, persona: str):
        self.name = name
        self.model = model
        self.persona = persona

    def __repr__(self):
        return f"<ParticipantConfig name='{self.name}' model='{self.model}'>"


class AppConfig:
    """アプリケーション全体の設定を保持するクラス"""

    def __init__(self, topic: str, participants: list[ParticipantConfig], max_turns: int = 10, show_prompt: bool = False):
        self.topic = topic
        self.participants = participants
        self.max_turns = max_turns
        self.show_prompt = show_prompt
        self.db_path = DB_PATH


def load_config_from_file(config_path: str = CONFIG_FILE_PATH) -> AppConfig:
    """YAML設定ファイルから設定を読み込む"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    # Use yaml.load with yaml_include's IncludeLoader to support !include tag
    with open(config_path, 'r', encoding='utf-8') as file:
        # 修正: yaml_include.IncludeLoader を使用
        config_data = yaml.load(file, Loader=yaml_include.IncludeLoader)

    topic = config_data.get("topic")
    participants_data = config_data.get("participants", [])
    max_turns = config_data.get("max_turns", 10) # デフォルト値は10
    show_prompt = config_data.get("show_prompt", False) # デフォルト値はFalse

    if not topic:
        raise ValueError("設定ファイルに 'topic' が指定されていません。")
    if len(participants_data) < 2:
        raise ValueError("設定ファイルには少なくとも2人の 'participants' が必要です。")

    participants = [
        ParticipantConfig(p["name"], p["model"], p["persona"])
        for p in participants_data
    ]

    return AppConfig(topic, participants, max_turns, show_prompt)


def parse_arguments() -> argparse.Namespace:
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(
        description="LLM同士がテーマについて会話するアプリケーション"
    )
    parser.add_argument(
        "--config", "-c",
        default=CONFIG_FILE_PATH,
        help="設定ファイルのパス (デフォルト: config.yaml)"
    )
    parser.add_argument(
        "--topic", "-t",
        help="会話のテーマ (設定ファイルの値を上書き)"
    )
    parser.add_argument(
        "--show-prompt", "-p",
        action="store_true",
        help="プロンプトをコンソールに出力する"
    )
    # 今後、データベースパスなどのオプションを追加できます
    return parser.parse_args()


def get_app_config() -> AppConfig:
    """アプリケーションの設定を取得する (ファイル -> 引数 の優先順位)"""
    args = parse_arguments()
    config = load_config_from_file(args.config)

    # コマンドライン引数でテーマが指定されていれば上書き
    if args.topic:
        config.topic = args.topic
    # コマンドライン引数でshow_promptが指定されていれば上書き
    if args.show_prompt:
        config.show_prompt = args.show_prompt

    return config