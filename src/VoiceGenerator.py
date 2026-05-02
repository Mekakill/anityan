import asyncio
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class VoiceMessage:
    """Generated voice message"""
    path: str


class VoiceGenerator:
    """Voice generation using ElevenLabs API"""
    
    def __init__(self, api_key: str, voice_id: str = "pPdl9cQBQq4p6mRkZy2Z"):
        self.api_key = api_key
        self.voice_id = voice_id
    
    async def generate(self, text: str, language_code: str = "en", speed: float = 1.0) -> VoiceMessage:
        """Generate voice message"""
        import aiohttp
        
        url = "https://api.elevenlabs.io/v1/text-to-speech"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_multilingual_v2",
                    "language_code": language_code,
                    "voice_settings": {
                        "speed": speed
                    }
                }
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Save to file
                    voice_dir = Path("data/voice_messages")
                    voice_dir.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = asyncio.get_event_loop().time()
                    output_path = voice_dir / f"{timestamp}.mp3"
                    
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    
                    return VoiceMessage(path=str(output_path))
                else:
                    raise Exception(f"Failed to generate audio: {response.status}")