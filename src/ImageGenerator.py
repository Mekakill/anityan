import asyncio
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from OpenAIChat import Message, Role

@dataclass
class GalleryImage:
    """Generated image"""
    image: bytes
    path: str


class ImageGenerator:
    """Image generation using Stable Diffusion"""
    
    def __init__(self, sd_client, chat_client):
        self.sd_client = sd_client
        self.chat_client = chat_client
    
    async def generate(self, description: str) -> GalleryImage:
        """Generate image from description"""
        # Step 1: Engineer prompt using LLM
        positive_prompt, negative_prompt = await self._engineer_prompt(description)
        
        # Step 2: Generate image using Stable Diffusion
        response = await self.sd_client.txt2img({
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "steps": 30,
            "width": 512,
            "height": 512
        })
        
        # Step 3: Assess image quality using vision model
        assessment = await self._assess_image(response["images"][0], description)
        
        if not assessment["satisfied"]:
            return await self.generate(description)  # Retry
        
        return GalleryImage(
            image=response["images"][0],
            path=f"generated_{asyncio.get_event_loop().time()}.png"
        )
    
    async def _engineer_prompt(self, description: str) -> tuple:
        """Engineer prompt using LLM"""
        from OpenAIChat import OpenAIChat
        
        system_prompt = f"""You are an expert Stable Diffusion prompt engineer.
Transform this description into a high-quality SD prompt.

Description: {description}

Output format:
{{
    "positivePrompt": "...",
    "negativePrompt": "..."
}}"""
        
        chat = OpenAIChat(system_prompt=system_prompt)
        response = await chat.chat([
            Message(role=Role.USER, content=f"Generate prompt for: {description}")
        ])
        
        import json
        data = json.loads(response.choices[0]["message"]["content"])
        return data["positivePrompt"], data["negativePrompt"]
    
    async def _assess_image(self, image: bytes, description: str) -> dict:
        """Assess image quality using vision model"""
        from OpenAIChat import OpenAIChat
        
        system_prompt = f"""You are an image critic. Assess this image against the description.

Description: {description}

Output format:
{{
    "satisfied": true/false,
    "feedback": "..."
}}"""
        
        chat = OpenAIChat(system_prompt=system_prompt)
        response = await chat.chat([
            Message(role=Role.USER, content=f"Assess this image:\n{image}")
        ])
        
        import json
        data = json.loads(response.choices[0]["message"]["content"])
        return data