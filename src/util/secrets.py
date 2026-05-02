import toml
from pathlib import Path
from typing import Any


def secrets() -> dict[str, Any]:
    """Load secrets from data/secrets.toml"""
    secrets_path = Path("data") / "secrets.toml"
    
    if not secrets_path.exists():
        secrets_path.parent.mkdir(parents=True, exist_ok=True)
        
        template = """# SECRETS file, kuni project
# WARNING - SENSITIVE DATA! DO NOT SHARE NOR COMMIT THIS FILE!!!

[telegram_api]
# tdlib API key, see https://core.telegram.org/api/obtaining_api_id
id = 0
hash = ""

[ollama]
# uncomment and specify this if you want Ollama web search
# bearer_key = ""

[elevenlabs]
# ElevenLabs API key for TTS
# api_key = ""
# Optional default voice ID. If omitted, the built-in default voice id is used.
# voice_id = "pPdl9cQBQq4p6mRkZy2Z"
"""
        
        with open(secrets_path, 'w') as f:
            f.write(template)
        
        raise FileNotFoundError(f"Please create {secrets_path} with your API keys")
    
    with open(secrets_path, 'r') as f:
        return toml.load(f)