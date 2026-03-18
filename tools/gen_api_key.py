#!/usr/bin/env python3
"""Generate API keys for the audit service.

Usage:
    python tools/gen_api_key.py [count]

Generates one or more API keys. Add them to .env API_KEYS (comma-separated).
"""
import secrets
import sys

PREFIX = "ask-"  # audit-service-key


def generate_key() -> str:
    return PREFIX + secrets.token_hex(24)


def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    keys = [generate_key() for _ in range(count)]
    for key in keys:
        print(key)
    if count > 1:
        print(f"\nFor .env:\nAPI_KEYS={','.join(keys)}")


if __name__ == "__main__":
    main()
