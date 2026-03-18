#!/bin/sh
# Audit with API key authentication
curl -X POST http://localhost:8000/audit/smart-contract-audit \
  -H "X-API-Key: ask-1f0c23683adeb6c1963a86db3879aa9878cf21f50eac8116" \
  -F "file=@trc-8004-contracts.zip"

# Audit without API key (when API_KEYS is not configured)
# curl -X POST http://localhost:8000/audit/smart-contract-audit \
#   -F "file=@trc-8004-contracts.zip"
