#!/bin/sh
# PR audit with API key authentication
curl -X POST http://localhost:8000/audit-pr/code-review \
  -H "X-API-Key: ask-1f0c23683adeb6c1963a86db3879aa9878cf21f50eac8116" \
  -F "file=@code.zip" \
  -F "from_branch=main" \
  -F "to_branch=feature/new-token"

# PR audit without API key (when API_KEYS is not configured)
# curl -X POST http://localhost:8000/audit-pr/code-review \
#   -F "file=@code.zip" \
#   -F "from_branch=main" \
#   -F "to_branch=feature/new-token"
