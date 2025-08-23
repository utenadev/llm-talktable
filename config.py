import yaml
import argparse
import os

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

    def __init__(self, topic: str, participants: list[ParticipantConfig]):
        self.topic = topic
        self.participants = participants
        self.db_path = DB_PATH


def load_config_from_file(config_path: str = CONFIG_FILE_PATH) -> AppConfig:
    """YAML設定ファイルから設定を読み込む"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)

    topic = config_data.get("topic")
    participants_data = config_data.get("participants", [])

    if not topic:
        raise ValueError("設定ファイルに 'topic' が指定されていません。")
    if len(participants_data) < 2:
        raise ValueError("設定ファイルには少なくとも2人の 'participants' が必要です。")

    participants = [
        ParticipantConfig(p["name"], p["model"], p["persona"])
        for p in participants_data
    ]

    return AppConfig(topic, participants)


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
    # 今後、データベースパスや最大ターン数などのオプションを追加できます
    return parser.parse_args()


def get_app_config() -> AppConfig:
    """アプリケーションの設定を取得する (ファイル -> 引数 の優先順位)"""
    args = parse_arguments()
    config = load_config_from_file(args.config)

    # コマンドライン引数でテーマが指定されていれば上書き
    if args.topic:
        config.topic = args.topic

    return config