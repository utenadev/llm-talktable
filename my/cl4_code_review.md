# コードレビュー結果 (LLM TalkTable)

## レビュー概要

LLM TalkTable プロジェクトのコードベースを分析し、品質向上のための改善提案をまとめました。
全体的にはよく構造化されたコードですが、保守性・可読性・テスタビリティの観点で改善の余地があります。

## 改善提案

### 1. ログ機能の統一化 【優先度: 高】

**問題点:**
- `print()` 文が散在し、ログレベルの概念がない
- デバッグ時の情報制御が困難
- 本番環境での出力制御ができない

**解決策:**
```python
# 新しいファイル: logger.py
import logging
from colorama import Fore, Style

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper()))
    return logger
```

**修正箇所:**
- `conversation.py`: 全ての `print()` を `logger.info()` などに置換
- `main.py`: ログレベルの設定を追加

### 2. 型ヒントの完全化 【優先度: 中】

**問題点:**
- 一部の関数で戻り値型が不明確
- `Optional` や `Union` の使用が不十分
- IDE での型チェックが効かない箇所がある

**修正例:**
```python
# conversation.py の修正
from typing import Optional, List, Dict, Any

def _run_single_turn(
    self,
    speaker: ParticipantConfig,
    prompt_text: str,
    context_fragments: Optional[List[str]] = None,
    show_prompt: bool = False,
) -> str:
    """1人のLLMにプロンプトを送信し、レスポンスを取得する"""

def _print_colored_response(
    self, 
    speaker_name: str, 
    response_text: str
) -> None:
    """話者名に応じて色を付けたレスポンステキストを表示する"""

# database.py の修正
def log_conversation_turn(
    conversation_id: str,
    turn_number: int,
    speaker_name: str,
    model_used: str,
    prompt: str,
    response: str,
    db_path: str = DB_PATH,
) -> None:
    """1ターン分の会話をデータベースに記録する"""
```

### 3. 設定バリデーションの強化 【優先度: 高】

**問題点:**
- YAML読み込み時の型チェックが甘い
- 不正な設定値でも実行時まで検出されない
- エラーメッセージが不親切

**修正例:**
```python
# config.py の修正
from typing import Dict, Any, List

def _validate_participant(p: Dict[str, Any]) -> None:
    """参加者設定のバリデーション"""
    required_fields = ["name", "model", "persona"]
    for field in required_fields:
        if field not in p:
            raise ValueError(f"参加者設定に '{field}' が不足しています: {p}")
        if not isinstance(p[field], str):
            raise ValueError(f"'{field}' は文字列である必要があります: {p[field]}")
        if not p[field].strip():
            raise ValueError(f"'{field}' は空文字列にできません")

def _validate_config_data(config_data: Dict[str, Any]) -> None:
    """設定データ全体のバリデーション"""
    # topic のバリデーション
    if not config_data.get("topic"):
        raise ValueError("設定ファイルに 'topic' が指定されていません。")
    
    # participants のバリデーション
    participants_data = config_data.get("participants", [])
    if len(participants_data) < 2:
        raise ValueError("設定ファイルには少なくとも2人の 'participants' が必要です。")
    
    for i, p in enumerate(participants_data):
        try:
            _validate_participant(p)
        except ValueError as e:
            raise ValueError(f"参加者 {i+1} の設定エラー: {e}") from e
    
    # max_turns のバリデーション
    max_turns = config_data.get("max_turns", 10)
    if not isinstance(max_turns, int) or max_turns <= 0:
        raise ValueError(f"'max_turns' は正の整数である必要があります: {max_turns}")
```

### 4. 例外処理の整理 【優先度: 中】

**問題点:**
- `KeyboardInterrupt` 処理が重複している
- 例外の再送出が不適切な箇所がある
- エラーハンドリングが一貫していない

**修正例:**
```python
# conversation.py の修正
def _run_single_turn(self, speaker: ParticipantConfig, prompt_text: str, 
                    context_fragments: Optional[List[str]] = None,
                    show_prompt: bool = False) -> str:
    """1人のLLMにプロンプトを送信し、レスポンスを取得する"""
    model = self._get_llm_model(speaker)
    
    # プロンプトの構築
    system_fragments = [speaker.persona] if speaker.persona else []
    fragments = context_fragments if context_fragments else []

    logger.info(f"{speaker.name} ({speaker.model}) の発言開始")
    if show_prompt:
        logger.debug(f"プロンプト: {prompt_text}")

    try:
        response_text = ""
        with yaspin(Spinners.bouncingBall, color="magenta",
                    text=f"{speaker.name} is thinking...") as spinner:
            response = model.prompt(
                prompt_text,
                system_fragments=system_fragments,
                fragments=fragments,
            )
            response_text = response.text()

        self._print_colored_response(speaker.name, response_text)
        
        # データベースに記録
        log_conversation_turn(
            conversation_id=self.conversation_id,
            turn_number=self.turn_count,
            speaker_name=speaker.name,
            model_used=speaker.model,
            prompt=prompt_text,
            response=response_text,
        )
        
        return response_text
        
    except KeyboardInterrupt:
        logger.info("LLM呼び出しが中断されました")
        raise  # 上位で処理
    except Exception as e:
        error_msg = f"LLM '{speaker.name}' の呼び出しに失敗しました: {e}"
        logger.error(error_msg)
        
        # エラーもログに記録
        log_conversation_turn(
            conversation_id=self.conversation_id,
            turn_number=self.turn_count,
            speaker_name=speaker.name,
            model_used=speaker.model,
            prompt=prompt_text,
            response=f"[エラー] {error_msg}",
        )
        raise RuntimeError(error_msg) from e
```

### 5. 設定の外部化 【優先度: 低】

**問題点:**
- マジックナンバーのハードコーディング
- 設定値が散在している

**修正例:**
```python
# config.py に追加
class AppConfig:
    def __init__(self, topic: str, participants: List[ParticipantConfig], 
                 max_turns: int = 10, show_prompt: bool = False):
        self.topic = topic
        self.participants = participants
        self.max_turns = max_turns
        self.show_prompt = show_prompt
        self.db_path = DB_PATH
        
        # 新しい設定項目
        self.turn_delay = 1.0  # APIレート制限考慮の待機時間
        self.spinner_type = "bouncingBall"
        self.max_response_length = 2000  # レスポンスの最大長
        self.retry_count = 3  # LLM呼び出しのリトライ回数
```

### 6. データベース接続の最適化 【優先度: 中】

**問題点:**
- データベース接続を毎回開いている
- トランザクション管理が不十分

**修正例:**
```python
# database.py の修正
import sqlite3
from contextlib import contextmanager
from typing import Generator

@contextmanager
def get_db_connection(db_path: str = DB_PATH) -> Generator[sqlite3.Connection, None, None]:
    """データベース接続のコンテキストマネージャー"""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()

def log_conversation_turn(
    conversation_id: str,
    turn_number: int,
    speaker_name: str,
    model_used: str,
    prompt: str,
    response: str,
    db_path: str = DB_PATH,
) -> None:
    """1ターン分の会話をデータベースに記録する"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversation_log
            (conversation_id, turn_number, speaker_name, model_used, prompt, response)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, turn_number, speaker_name, model_used, prompt, response),
        )
```

### 7. テスタビリティの向上 【優先度: 中】

**問題点:**
- LLM呼び出しが直接埋め込まれている
- 依存関係の注入ができない
- ユニットテストが困難

**修正例:**
```python
# 新しいファイル: llm_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional

class LLMInterface(ABC):
    """LLMの抽象インターフェース"""
    
    @abstractmethod
    def prompt(self, text: str, system_fragments: Optional[List[str]] = None,
               fragments: Optional[List[str]] = None) -> str:
        """プロンプトを送信してレスポンスを取得"""
        pass

class RealLLMAdapter(LLMInterface):
    """実際のLLMを使用するアダプター"""
    
    def __init__(self, model_id: str):
        self.model = llm.get_model(model_id)
    
    def prompt(self, text: str, system_fragments: Optional[List[str]] = None,
               fragments: Optional[List[str]] = None) -> str:
        response = self.model.prompt(text, system_fragments=system_fragments,
                                   fragments=fragments)
        return response.text()

class MockLLMAdapter(LLMInterface):
    """テスト用のモックLLM"""
    
    def __init__(self, responses: List[str]):
        self.responses = responses
        self.call_count = 0
    
    def prompt(self, text: str, system_fragments: Optional[List[str]] = None,
               fragments: Optional[List[str]] = None) -> str:
        if self.call_count < len(self.responses):
            response = self.responses[self.call_count]
            self.call_count += 1
            return response
        return "Mock response"
```

## 実装優先順位

1. **ログ機能の統一化** - デバッグとメンテナンスが大幅に改善
2. **設定バリデーションの強化** - 実行時エラーの早期発見
3. **データベース接続の最適化** - パフォーマンスと安定性の向上
4. **型ヒントの完全化** - 開発時の安全性向上
5. **例外処理の整理** - コードの可読性向上
6. **テスタビリティの向上** - 将来的なテスト実装のため
7. **設定の外部化** - 設定の柔軟性向上

## 追加の改善提案

### エラーメッセージの国際化
```python
# messages.py
MESSAGES = {
    "ja": {
        "config_topic_missing": "設定ファイルに 'topic' が指定されていません。",
        "config_participants_insufficient": "設定ファイルには少なくとも2人の 'participants' が必要です。",
        "llm_call_failed": "LLM '{name}' の呼び出しに失敗しました: {error}",
    },
    "en": {
        "config_topic_missing": "Topic is not specified in the config file.",
        "config_participants_insufficient": "At least 2 participants are required in the config file.",
        "llm_call_failed": "Failed to call LLM '{name}': {error}",
    }
}
```

### 設定ファイルのスキーマ定義
```yaml
# config_schema.yaml
type: object
required: [topic, participants]
properties:
  topic:
    type: string
    minLength: 1
  participants:
    type: array
    minItems: 2
    items:
      type: object
      required: [name, model, persona]
      properties:
        name:
          type: string
          minLength: 1
        model:
          type: string
          minLength: 1
        persona:
          type: string
          minLength: 1
  max_turns:
    type: integer
    minimum: 1
    default: 10
  show_prompt:
    type: boolean
    default: false
```

## まとめ

このコードベースは基本的な機能は実装されていますが、上記の改善を行うことで：

- **保守性**: ログ機能とエラーハンドリングの改善
- **安全性**: 型ヒントと設定バリデーションの強化
- **パフォーマンス**: データベース接続の最適化
- **テスタビリティ**: 依存性注入とモック対応

これらの観点で大幅に品質が向上します。特に優先度の高い項目から段階的に実装することを推奨します。