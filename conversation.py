import llm
import uuid
from config import AppConfig, ParticipantConfig
from database import log_conversation_turn, log_conversation_meta
import time
import sys

# colorama for colored console output
from colorama import init as colorama_init, Fore, Style
colorama_init() # Initialize colorama


class ConversationManager:
    """LLM同士の会話を管理するクラス"""

    def __init__(self, config: AppConfig):
        self.config = config
        self.conversation_id = str(uuid.uuid4())
        self.turn_count = 0

    def _get_llm_model(self, participant: ParticipantConfig):
        """ParticipantConfigからllm.Modelインスタンスを取得"""
        try:
            model = llm.get_model(participant.model)
            # llmのキー設定は外部で行われている前提
            return model
        except Exception as e:
            raise ValueError(
                f"モデル '{participant.model}' の取得に失敗しました (参加者: {participant.name}): {e}"
            ) from e

    def _print_colored_response(self, speaker_name: str, response_text: str):
        """話者名に応じて色を付けたレスポンステキストを表示する"""
        # 話者ごとの色を定義
        speaker_colors = {
            self.config.participants[0].name: Fore.CYAN,  # 参加者A: 水色
            self.config.participants[1].name: Fore.MAGENTA,  # 参加者B: マゼンタ
            # MCが実装された場合はここに追加
            # "MC": Fore.YELLOW,
        }
        # デフォルト色
        default_color = Fore.WHITE

        color = speaker_colors.get(speaker_name, default_color)
        print(f"{color}{response_text}{Style.RESET_ALL}")

    def _run_single_turn(
        self,
        speaker: ParticipantConfig,
        prompt_text: str,
        context_fragments: list[str] = None,
    ) -> str:
        """1人のLLMにプロンプトを送信し、レスポンスを取得する"""
        model = self._get_llm_model(speaker)

        # プロンプトの構築
        # speaker.persona をシステムフラグメントとして使用
        system_fragments = [speaker.persona] if speaker.persona else []
        fragments = context_fragments if context_fragments else []

        print(f"\n--- {speaker.name} ({speaker.model}) の発言 ---")
        print(f"プロンプト: {prompt_text}")

        try:
            response = model.prompt(
                prompt_text,
                system_fragments=system_fragments,
                fragments=fragments,
                stream=True  # ストリーミングを有効にする (llmライブラリが対応していれば)
            )

            print("レスポンス:")
            response_text = ""
            # ストリームからテキストを逐次取得して表示
            for chunk in response:
                # chunk が文字列であることを期待 (llmライブラリの仕様に依存)
                if isinstance(chunk, str):
                    print(chunk, end='', flush=True) # 即時表示
                    response_text += chunk
                else:
                    # chunk が他のオブジェクトの場合 (例: OpenAIのChatCompletionChunk)
                    # この場合、chunk.choices[0].delta.content などからテキストを取得する必要がある
                    # ここでは簡略化のため、str(chunk) を使用
                    chunk_str = str(chunk)
                    print(chunk_str, end='', flush=True)
                    response_text += chunk_str
            print("\n") # ストリーム終了後に改行
            print("-" * 20)

            # データベースに記録
            log_conversation_turn(
                conversation_id=self.conversation_id,
                turn_number=self.turn_count,
                speaker_name=speaker.name,
                model_used=speaker.model,
                prompt=prompt_text,
                response=response_text, # ストリームから構成された完全なテキスト
            )

            return response_text
        except Exception as e:
            error_msg = f"LLM '{speaker.name}' の呼び出しに失敗しました: {e}"
            print(f"エラー: {error_msg}")
            # エラーもログに記録
            log_conversation_turn(
                conversation_id=self.conversation_id,
                turn_number=self.turn_count,
                speaker_name=speaker.name,
                model_used=speaker.model,
                prompt=prompt_text,
                response=f"[エラー] {error_msg}",
            )
            raise

    def start_conversation(self, max_turns: int = 10):
        """会話を開始する"""
        if len(self.config.participants) < 2:
            raise ValueError("会話には少なくとも2人の参加者が必要です。")

        participant_a = self.config.participants[0]
        participant_b = self.config.participants[1]

        print(f"会話セッション開始 (ID: {self.conversation_id})")
        print(f"テーマ: {self.config.topic}")
        print(f"参加者A: {participant_a.name} ({participant_a.model})")
        print(f"参加者B: {participant_b.name} ({participant_b.model})")
        print(f"最大ターン数: {max_turns}")
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
            print(f"\n[ターン {self.turn_count}]")

            try:
                # 現在のスピーカーにプロンプトを送信
                response_text = self._run_single_turn(
                    speaker=current_speaker,
                    prompt_text=current_prompt,
                )

                # 次のターンの準備: レスポンスを次のプロンプトにする
                current_prompt = response_text
                # スピーカーを交代
                current_speaker, next_speaker = next_speaker, current_speaker

                # 少し待機してAPIレート制限を考慮 (必要に応じて調整)
                time.sleep(1)

            except Exception as e:
                print(f"会話中にエラーが発生しました。会話を終了します。: {e}")
                break

        print(f"\n会話セッション終了 (ID: {self.conversation_id}, 最大ターン数: {max_turns})")


# --- メイン実行用の関数 (オプション) ---
# `main.py` から直接 `ConversationManager` をインポートして使用するため、
# ここに `if __name__ == "__main__":` ブロックは不要です。