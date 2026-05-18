# openai_key_store.py 改善版
# -*- coding: utf-8 -*-
"""OpenAI API KeyをOS資格情報ストアで安全に管理する。"""
from __future__ import annotations

from typing import Any, cast

SERVICE_NAME: str = "logger_project_openai"
ACCOUNT_NAME: str = "OPENAI_API_KEY"


# if TYPE_CHECKING:
#     import keyring


# =========================
# keyring取得
# =========================
def _load_keyring() -> Any | None:
    """keyringモジュールを読み込む。利用不可ならNoneを返す。"""
    try:
        import keyring
    except ImportError:
        return None

    return keyring


# =========================
# keyring利用可否
# =========================
def is_keyring_available() -> bool:
    """keyringが利用可能ならTrue。"""
    return _load_keyring() is not None


# =========================
# API Key取得
# =========================
def get_openai_api_key() -> str | None:
    """保存済みのOpenAI API Keyを取得する。"""
    keyring_module: Any | None = _load_keyring()

    if keyring_module is None:
        return None

    key: str | None = cast(
        str | None,
        keyring_module.get_password(SERVICE_NAME, ACCOUNT_NAME),
    )

    return key


# =========================
# API Key存在確認
# =========================
def has_openai_api_key() -> bool:
    """OpenAI API Keyが保存済みか確認する。"""
    return get_openai_api_key() is not None


# =========================
# API Key保存
# =========================
def save_openai_api_key(api_key: str) -> None:
    """OpenAI API KeyをOS資格情報ストアへ保存する。"""
    keyring_module: Any | None = _load_keyring()

    if keyring_module is None:
        raise RuntimeError("keyring module is not installed")

    if not api_key.strip():
        raise ValueError("api_key is empty")

    keyring_module.set_password(
        SERVICE_NAME,
        ACCOUNT_NAME,
        api_key,
    )


# =========================
# API Key削除
# =========================
def delete_openai_api_key() -> None:
    """保存済みのOpenAI API Keyを削除する。"""
    keyring_module: Any | None = _load_keyring()

    if keyring_module is None:
        raise RuntimeError("keyring module is not installed")

    try:
        keyring_module.delete_password(
            SERVICE_NAME,
            ACCOUNT_NAME,
        )

    except Exception:
        # 未登録時など
        return
