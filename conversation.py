import llm
import uuid
from config import AppConfig, ParticipantConfig
from database import log_conversation_turn, log_conversation_meta
import time
import sys
from typing import Optional, List
import importlib

# colorama for colored console output
from colorama import init as colorama_init, Fore, Style
colorama_init() # Initialize colorama

# yaspin for waiting indicator (spinner)
from yaspin import yaspin
from yaspin.spinners import Spinners

# logging
from logger import setup_logger
logger = setup_logger(__name__, level="DEBUG")

# llm-gemini プラグインがロードされるように、llm モジュールをリロードする
importlib.reload(llm)
llm.load_plugins()
logger.debug(f"モジュールロード時にロードされているプラグイン: {list(llm.pm.list_name_plugin())}")


class ConversationManager:
    """LLM同士の会話を管理するクラス"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.conversation_id = str(uuid.uuid4())
        self.turn_count = 0

    def _get_llm_model(self, participant: ParticipantConfig):
        """ParticipantConfigからllm.Modelインスタンスを取得"""
        try:
            logger.debug(f"モデル '{participant.model}' を取得します。")
            # モジュールロード時に llm.load_plugins() を呼び出しているため、
            # ここでは呼び出さない。
            # llm.load_plugins()
            # デバッグ用にプラグインマネージャーの状態を出力
            logger.debug(f"プラグインマネージャー: {llm.pm}")
            logger.debug(f"ロードされているプラグイン: {list(llm.pm.list_name_plugin())}")
            # デバッグ用に登録されているモデルとエイリアスの一覧を出力
            models_with_aliases = llm.get_models_with_aliases()
            logger.debug(f"登録されているモデルとエイリアス:")
            for mwa in models_with_aliases:
                logger.debug(f"  モデル: {mwa.model}, エイリアス: {mwa.aliases}")
            model = llm.get_model(participant.model)
            logger.debug(f"モデル '{participant.model}' を取得しました。")
            # llmのキー設定は外部で行われている前提
            return model
        except Exception as e:
            logger.error(f"モデル '{participant.model}' の取得に失敗しました (参加者: {participant.name}): {e}")
            raise ValueError(
                f"モデル '{participant.model}' の取得に失敗しました (参加者: {participant.name}): {e}"
            ) from e

    def _print_colored_response(self, speaker_name: str, response_text: str):
        """話者名に応じて色を付けたレスポンステキストを表示する"""
        # 話者ごとの色を定義 (config.yaml から読み込むように拡張可能)
        speaker_colors = {
            self.config.participants[0].name: Fore.CYAN,    # 参加者A: 水色
            self.config.participants[1].name: Fore.MAGENTA, # 参加者B: マゼンタ
            # MCが実装された場合はここに追加
            # "MC": Fore.YELLOW,
        }
        # デフォルト色
        default_color = Fore.WHITE

        color = speaker_colors.get(speaker_name, default_color)
        print(f"{color}{response_text}{Style.RESET_ALL}")

    def _print_colored_chunk(self, speaker_name: str, chunk: str):
        """話者名に応じて色を付けたレスポンステキストのチャンクを表示する (ストリーム用)"""
        # 話者ごとの色を定義 (config.yaml から読み込むように拡張可能)
        speaker_colors = {
            self.config.participants[0].name: Fore.CYAN,    # 参加者A: 水色
            self.config.participants[1].name: Fore.MAGENTA, # 参加者B: マゼンタ
            # MCが実装された場合はここに追加
            # "MC": Fore.YELLOW,
        }
        # デフォルト色
        default_color = Fore.WHITE

        color = speaker_colors.get(speaker_name, default_color)
        print(f"{color}{chunk}{Style.RESET_ALL}", end="", flush=True)

    def _run_single_turn(
        self,
        speaker: ParticipantConfig,
        prompt_text: str,
        context_fragments: Optional[List[str]] = None,
        show_prompt: bool = False, # 新しい引数
        is_moderator: bool = False, # MC発言かどうかのフラグ (デフォルトはFalse)
    ) -> str:
        """1人のLLMにプロンプトを送信し、レスポンスを取得する"""
        model = self._get_llm_model(speaker)

        # プロンプトの構築
        # speaker.persona をシステムフラグメントとして使用
        system_fragments = [speaker.persona] if speaker.persona else []
        fragments = context_fragments if context_fragments else []

        logger.info(f"{speaker.name} ({speaker.model}) の発言開始")
        # show_prompt が True の場合のみプロンプトを表示
        if show_prompt:
            logger.debug(f"プロンプト: {prompt_text}")

        # show_prompt が True の場合のみ "レスポンス:" ラベルを表示
        if show_prompt:
            print("レスポンス:")
        else:
            # プロンプト非表示時は、レスポンス本文の前に何も表示しない
            pass

        # LLM呼び出し中にスピナーを表示
        response_text = "" # 例外発生時に空文字を返すため事前に定義
        try:
            with yaspin(Spinners.bouncingBall, color="magenta",
                        text=f"{speaker.name} is thinking...") as spinner:
                response = model.prompt(
                    prompt_text,
                    system_fragments=system_fragments,
                    fragments=fragments,
                    # stream=True # ストリーミングを使用 (デフォルトでTrueの可能性あり)
                )
                # スピナーを停止
                spinner.stop()
                # レスポンスをストリームで処理 (タイプライター効果)
                for chunk in response:
                    self._print_colored_chunk(speaker.name, chunk)
                    response_text += chunk
        except KeyboardInterrupt:
            # LLM呼び出し中にCtrl+Cが押された場合、スピナーを停止し、例外を再送出
            spinner.stop()
            logger.info("LLM呼び出しが中断されました")
            raise # KeyboardInterruptを呼び出し元に伝播

        # レスポンステキスト表示後に改行と区切り線を表示
        print("\n") # レスポンステキスト表示後に改行
        print("-" * 20)

        # データベースに記録
        log_conversation_turn(
            conversation_id=self.conversation_id,
            turn_number=self.turn_count,
            speaker_name=speaker.name,
            model_used=speaker.model,
            prompt=prompt_text,
            response=response_text,
            is_moderator=is_moderator, # MCフラグを記録
        )

        return response_text

    def start_conversation(self, max_turns: int = 10, show_prompt: bool = False): # 引数を追加
        """会話を開始する"""
        if len(self.config.participants) < 2:
            raise ValueError("会話には少なくとも2人の参加者が必要です。")

        participant_a = self.config.participants[0]
        participant_b = self.config.participants[1]
        moderator = self.config.moderator # MCを取得

        logger.info(f"会話セッション開始 (ID: {self.conversation_id})")
        
        # MCによる会話の開始
        self.turn_count = 0
        logger.info("[MC] 会話の開始")
        # MCに会話のテーマと参加者を紹介するプロンプトを送信
        mc_intro_prompt = f"テーマ: {self.config.topic}\n参加者A: {participant_a.name} ({participant_a.model})\n参加者B: {participant_b.name} ({participant_b.model})\n\nこれらの情報を使って、会話の開始をアナウンスしてください。"
        self._run_single_turn(
            speaker=moderator,
            prompt_text=mc_intro_prompt,
            show_prompt=show_prompt,
            is_moderator=True, # MCフラグを設定
        )
        
        print("-" * 40)

        # 会話メタデータをデータベースに記録
        log_conversation_meta(
            conversation_id=self.conversation_id,
            topic=self.config.topic,
            participant_a_name=participant_a.name,
            participant_a_model=participant_a.model,
            participant_b_name=participant_b.name,
            participant_b_model=participant_b.model,
        )

        # 初期プロンプト: テーマを提示
        current_prompt = self.config.topic
        current_speaker = participant_a
        next_speaker = participant_b

        for turn in range(max_turns):
            self.turn_count = turn + 1
            logger.info(f"[ターン {self.turn_count}] 開始")
            
            # ラウンドの開始 (2ターンごと: A->B->A)
            if turn % 2 == 0:
                logger.info("[MC] ラウンドの開始")
                # MCにラウンドの焦点や期待を述べるプロンプトを送信
                round_number = (turn // 2) + 1
                mc_round_prompt = f"ラウンド {round_number} を開始してください。{current_speaker.name} から {self.config.topic} についての発言をお願いします。"
                self._run_single_turn(
                    speaker=moderator,
                    prompt_text=mc_round_prompt,
                    show_prompt=show_prompt,
                    is_moderator=True, # MCフラグを設定
                )

            # --- インタラプト処理の追加 ---
            conversation_continues = True
            while conversation_continues:
                try:
                    # 現在のスピーカーにプロンプトを送信
                    response_text = self._run_single_turn(
                        speaker=current_speaker,
                        prompt_text=current_prompt,
                        show_prompt=show_prompt,
                    )
                    conversation_continues = False # 成功したらループを抜ける

                except KeyboardInterrupt:
                    print("\n\n--- 会話が中断されました ---")
                    while True:
                        try:
                            choice = input("会話を終了しますか？ (S[top] で終了, C[ontinue] で継続): ").strip().upper()
                            if choice in ["S", "STOP"]:
                                print("会話を終了します。")
                                return # メソッドを正常終了 (sys.exitは呼ばない)
                            elif choice in ["C", "CONTINUE"]:
                                print("会話を継続します。")
                                break # 内側のループを抜けて、現在のターンを再試行
                            else:
                                print("無効な入力です。'S' または 'C' を入力してください。")
                        except (EOFError, KeyboardInterrupt):
                            # 入力時にもう一度Ctrl+Cされた場合、プログラムを終了
                            print("\n再度中断されました。プログラムを終了します。")
                            raise # KeyboardInterruptをさらに上位に伝播 (main.pyでsys.exit(0)される)
            
            # ラウンドの終了 (2ターンごと: A->B->A)
            if turn % 2 == 1:
                logger.info("[MC] ラウンドの終了")
                # MCに両者の発言を要約し、次のラウンドへの橋渡しをするプロンプトを送信
                round_number = (turn // 2) + 1
                mc_summary_prompt = f"ラウンド {round_number} で {participant_a.name} と {participant_b.name} が交わした意見:\n{current_prompt}\n{response_text}\n\nこれらを要約し、次のラウンドへの期待を述べてください。"
                self._run_single_turn(
                    speaker=moderator,
                    prompt_text=mc_summary_prompt,
                    show_prompt=show_prompt,
                    is_moderator=True, # MCフラグを設定
                )

            # 次のターンの準備: レスポンスを次のプロンプトにする
            current_prompt = response_text
            # スピーカーを交代
            current_speaker, next_speaker = next_speaker, current_speaker

            # 少し待機してAPIレート制限を考慮 (設定値を使用)
            time.sleep(self.config.llm_wait_time)
        
        # MCによる会話の締めくくり
        logger.info("[MC] 会話の締めくくり")
        # MCに会話を締めくくるプロンプトを送信
        mc_conclusion_prompt = f"{max_turns} ターンの会話を経て、{self.config.topic} についての討論を締めくくってください。"
        self._run_single_turn(
            speaker=moderator,
            prompt_text=mc_conclusion_prompt,
            show_prompt=show_prompt,
            is_moderator=True, # MCフラグを設定
        )

        logger.info(f"会話セッション終了 (ID: {self.conversation_id}, 最大ターン数: {max_turns})")
        print(f"\n会話セッション終了 (ID: {self.conversation_id}, 最大ターン数: {max_turns})")


# --- メイン実行用の関数 (オプション) ---
# `main.py` から直接 `ConversationManager` をインポートして使用するため、
# ここに `if __name__ == "__main__":` ブロックは不要です。