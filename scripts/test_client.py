#!/usr/bin/env python3

import asyncio
import sys
import re
sys.path.insert(0, '.opencode/skills/funasr-asr/scripts')

from funasr_ws_client import FunASRClient, clean_sensevoice_text


def test_clean_sensevoice_text():
    text = "<|zh|><|NEUTRAL|><|Speech|>欢迎大家"
    result = clean_sensevoice_text(text)
    assert result == "欢迎大家", f"Expected '欢迎大家', got '{result}'"
    print("test_clean_sensevoice_text: PASS")


def test_clean_sensevoice_text_empty():
    text = "<|nospeech|><|EMO_UNKNOWN|>"
    result = clean_sensevoice_text(text)
    assert result == "", f"Expected empty string, got '{result}'"
    print("test_clean_sensevoice_text_empty: PASS")


def test_clean_sensevoice_text_mixed():
    text = "<|en|><|HAPPY|>Hello World"
    result = clean_sensevoice_text(text)
    assert result == "Hello World", f"Expected 'Hello World', got '{result}'"
    print("test_clean_sensevoice_text_mixed: PASS")


def test_client_init_defaults():
    client = FunASRClient()
    assert client.host == "localhost"
    assert client.port == 10095
    assert client.ssl_enabled == True
    assert client.mode == "2pass"
    print("test_client_init_defaults: PASS")


def test_client_init_custom():
    client = FunASRClient(
        host="192.168.1.100",
        port=10096,
        ssl_enabled=False,
        mode="online"
    )
    assert client.host == "192.168.1.100"
    assert client.port == 10096
    assert client.ssl_enabled == False
    assert client.mode == "online"
    print("test_client_init_custom: PASS")


def test_client_get_ws_uri_ssl():
    client = FunASRClient(host="localhost", port=10095, ssl_enabled=True)
    uri = client._get_ws_uri()
    assert uri == "wss://localhost:10095", f"Expected 'wss://localhost:10095', got '{uri}'"
    print("test_client_get_ws_uri_ssl: PASS")


def test_client_get_ws_uri_no_ssl():
    client = FunASRClient(host="localhost", port=10096, ssl_enabled=False)
    uri = client._get_ws_uri()
    assert uri == "ws://localhost:10096", f"Expected 'ws://localhost:10096', got '{uri}'"
    print("test_client_get_ws_uri_no_ssl: PASS")


def test_client_chunk_size_parsing():
    client = FunASRClient(chunk_size="5,10,5")
    assert client.chunk_size == [5, 10, 5]
    print("test_client_chunk_size_parsing: PASS")


def test_client_get_ssl_context_enabled():
    client = FunASRClient(ssl_enabled=True)
    ctx = client._get_ssl_context()
    assert ctx is not None
    print("test_client_get_ssl_context_enabled: PASS")


def test_client_get_ssl_context_disabled():
    client = FunASRClient(ssl_enabled=False)
    ctx = client._get_ssl_context()
    assert ctx is None
    print("test_client_get_ssl_context_disabled: PASS")


if __name__ == "__main__":
    print("Running FunASR Client Tests...")
    print("=" * 50)
    
    test_clean_sensevoice_text()
    test_clean_sensevoice_text_empty()
    test_clean_sensevoice_text_mixed()
    test_client_init_defaults()
    test_client_init_custom()
    test_client_get_ws_uri_ssl()
    test_client_get_ws_uri_no_ssl()
    test_client_chunk_size_parsing()
    test_client_get_ssl_context_enabled()
    test_client_get_ssl_context_disabled()
    
    print("=" * 50)
    print("All tests passed!")
