import argparse
import os
from typing import List, Dict, Any


# Use yaml_include for !include tag support
import yaml
import yaml_include


# --- !include タグのためのセットアップ ---
# yaml_include.Constructor のインスタンスを作成
include_constructor = yaml_include.Constructor()

# PyYAML のローダー (例: FullLoader) に !include コンストラクターを登録
# 第一引数はタグ名 (!include), 第二引数はコンストラクター関数
yaml.add_constructor('!include', include_constructor, Loader=yaml.FullLoader)
# --- セットアップ完了 ---


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

    def __init__(self, topic: str, participants: List[ParticipantConfig], moderator: ParticipantConfig, max_turns: int = 10, llm_wait_time: int = 1, show_prompt: bool = False):
        self.topic = topic
        self.participants = participants
        self.moderator = moderator
        self.max_turns = max_turns
        self.llm_wait_time = llm_wait_time
        self.show_prompt = show_prompt
        self.db_path = DB_PATH


def _validate_participant(p: Dict[str, Any], index: int) -> None:
    """参加者設定のバリデーション"""
    required_fields = ["name", "model", "persona"]
    for field in required_fields:
        if field not in p:
            raise ValueError(f"参加者 {index+1} の設定に '{field}' が不足しています。")
        if not isinstance(p[field], str):
            raise ValueError(f"参加者 {index+1} の '{field}' は文字列である必要があります: {p[field]}")
        if not p[field].strip():
            raise ValueError(f"参加者 {index+1} の '{field}' は空文字列にできません")


def _validate_config_data(config_data: Dict[str, Any]) -> None:
    """設定データ全体のバリデーション"""
    # topic のバリデーション
    if not config_data.get("topic"):
        raise ValueError("設定ファイルに 'topic' が指定されていません。")
    if not isinstance(config_data["topic"], str):
        raise ValueError("'topic' は文字列である必要があります。")
    if not config_data["topic"].strip():
        raise ValueError("'topic' は空文字列にできません")

    # participants のバリデーション
    participants_data = config_data.get("participants", [])
    if len(participants_data) < 2:
        raise ValueError("設定ファイルには少なくとも2人の 'participants' が必要です。")
    
    for i, p in enumerate(participants_data):
        try:
            _validate_participant(p, i)
        except ValueError as e:
            raise ValueError(f"参加者 {i+1} の設定エラー: {e}") from e

    # max_turns のバリデーション
    max_turns = config_data.get("max_turns", 10)
    if not isinstance(max_turns, int) or max_turns <= 0:
        raise ValueError(f"'max_turns' は正の整数である必要があります: {max_turns}")
    
    # show_prompt のバリデーション (オプション)
    show_prompt = config_data.get("show_prompt", False)
    if not isinstance(show_prompt, bool):
        raise ValueError(f"'show_prompt' は真偽値 (true/false) である必要があります: {show_prompt}")
        
    # moderator のバリデーション (オプション)
    moderator_data = config_data.get("moderator")
    if moderator_data:
        try:
            _validate_participant(moderator_data, -1) # -1 はMCを示すインデックス
        except ValueError as e:
            raise ValueError(f"MCの設定エラー: {e}") from e
            
    # llm_wait_time のバリデーション (オプション)
    llm_wait_time = config_data.get("llm_wait_time", 1)
    if not isinstance(llm_wait_time, int) or llm_wait_time < 0:
        raise ValueError(f"'llm_wait_time' は0以上の整数である必要があります: {llm_wait_time}")


def load_config_from_file(config_path: str = CONFIG_FILE_PATH) -> AppConfig:
    """YAML設定ファイルから設定を読み込む"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    # 標準的な yaml.load を使用し、事前に登録した FullLoader で !include を処理
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.load(file, Loader=yaml.FullLoader)

    # 設定データのバリデーション
    _validate_config_data(config_data)

    topic = config_data["topic"]
    participants_data = config_data["participants"]
    max_turns = config_data.get("max_turns", 10) # デフォルト値は10
    show_prompt = config_data.get("show_prompt", False) # デフォルト値はFalse

    participants = [
        ParticipantConfig(p["name"], p["model"], p["persona"])
        for p in participants_data
    ]
    
    # moderator の設定を読み込む (デフォルト値を設定)
    moderator_data = config_data.get("moderator", {
        "name": "MC",
        "model": "gemini/gemini-2.5-flash",
        "persona": "あなたはこの会話のモデレーターです。会話のテーマ紹介、参加者の紹介、ラウンドの管理、会話の要約と締めくくりを行います。"
    })
    moderator = ParticipantConfig(moderator_data["name"], moderator_data["model"], moderator_data["persona"])
    
    # llm_wait_time の設定を読み込む (デフォルト値は1秒)
    llm_wait_time = config_data.get("llm_wait_time", 1)

    return AppConfig(topic, participants, moderator, max_turns, llm_wait_time, show_prompt)


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