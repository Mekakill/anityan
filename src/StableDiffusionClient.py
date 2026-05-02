
# Converted from src/StableDiffusionClient.cpp
# Python implementation without AUI

import asyncio
import base64
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
import json
# ============================================================================
# CONFIGURATION (как config.h в C++)
# ============================================================================

class Config:
    """Конфигурация клиента."""
    
    REQUEST_TIMEOUT: int = 30  # секунд (как config::REQUEST_TIMEOUT)


# ============================================================================
# DATA STRUCTURES (как структуры в StableDiffusionClient.h)
# ============================================================================

@dataclass
class Txt2ImgRequest:
    """Запрос txt2img (как AJSON_FIELDS_ENTRY в C++)."""
    
    prompt: str
    negative_prompt: str = ""
    styles: List[str] = None
    seed: int = -1
    subseed: int = -1
    subseed_strength: float = 0.0
    seed_resize_from_h: int = -1
    seed_resize_from_w: int = -1
    sampler_name: str = "DPM++ 2M"
    scheduler: str = "Automatic"
    batch_size: int = 1
    n_iter: int = 1
    steps: int = 50
    cfg_scale: float = 2.0
    width: int = 512
    height: int = 512
    send_images: bool = True
    save_images: bool = False
    enable_hr: bool = False
    hr_scale: float = 2.0
    hr_upscaler: str = "Latent"
    hr_second_pass_steps: int = 0
    denoising_strength: float = 0.7
    
    def __post_init__(self):
        if self.styles is None:
            self.styles = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует request в словарь для JSON."""
        result = {
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "styles": self.styles,
            "seed": self.seed,
            "subseed": self.subseed,
            "subseed_strength": self.subseed_strength,
            "seed_resize_from_h": self.seed_resize_from_h,
            "seed_resize_from_w": self.seed_resize_from_w,
            "sampler_name": self.sampler_name,
            "scheduler": self.scheduler,
            "batch_size": self.batch_size,
            "n_iter": self.n_iter,
            "steps": self.steps,
            "cfg_scale": self.cfg_scale,
            "width": self.width,
            "height": self.height,
            "send_images": self.send_images,
            "save_images": self.save_images,
            "enable_hr": self.enable_hr,
            "hr_scale": self.hr_scale,
            "hr_upscaler": self.hr_upscaler,
            "hr_second_pass_steps": self.hr_second_pass_steps,
            "denoising_strength": self.denoising_strength,
        }
        # Удаляем параметры со значениями по умолчанию
        return {k: v for k, v in result.items() if not (isinstance(v, (int, float, str)) and v in [None, -1, "", False, 0]) or ("seed" in k and v == -1)}


@dataclass
class Txt2ImgResponse:
    """Ответ txt2img (как AVector<AImage> images + AJson info)."""
    
    images: List[bytes] = None
    info: str = ""
    
    def __post_init__(self):
        if self.images is None:
            self.images = []


# ============================================================================
# STABLEDIFFUSION CLIENT (основная реализация без AUI)
# ============================================================================

class StableDiffusionClient:
    """Клиент Stable Diffusion API."""
    
    def __init__(
        self, 
        endpoint_url: Optional[str] = None,
        bearer_key: Optional[str] = None
    ):
        """
        Инициализирует клиент.
        
        Args:
            endpoint_url: URL API (как config::ENDPOINT_SD)
            bearer_key: Авторизационный ключ (как endpoint.bearerKey)
        
        Raises:
            ValueError: Если URL не настроен
        """
        # В реальном использовании URL должен быть из конфигурации
        self.endpoint_url = endpoint_url or "http://127.0.0.1:7860/sdapi/v1/txt2img"
        self.bearer_key = bearer_key
    
    @property
    def configured(self) -> bool:
        """Проверяет, правильно ли настроены параметры."""
        return len(self.endpoint_url) > 0 and "://notconfigured" not in self.endpoint_url
    
    async def txt2img(
        self, 
        request: Txt2ImgRequest
    ) -> Txt2ImgResponse:
        """
        Генерирует изображение из текста через Stable Diffusion API.
        
        Args:
            request: Объект запроса (как const Txt2ImgRequest& в C++)
        
        Returns:
            Txt2ImgResponse с изображениями и метаданными
        
        Raises:
            ValueError: Если endpoint URL не настроен
            Exception: При ошибках API вызова
        """
        
        # Проверка конфигурации (как в C++: если (!endpoint.bearerKey.empty())...)
        if not self.endpoint_url or "://notconfigured" in self.endpoint_url:
            raise ValueError("Stable Diffusion endpoint URL not configured")
        
        # Подготовка JSON тела запроса (как AJson::toString(aui::to_json(request)))
        request_body = json.dumps(request.to_dict())
        
        print(f"[DEBUG] StableDiffusionClient::txt2img")
        print(f"Request preview: {request_body[:200]}...")
        
        # Заголовки (как AVector<AString> headers)
        headers = {
            "Content-Type": "application/json",
        }
        if self.bearer_key and len(self.bearer_key.strip()) > 0:
            headers["Authorization"] = f"Bearer {self.bearer_key}"
        
        # Выполняем POST запрос (как ACurl::Builder(...).runAsync())
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint_url,
                    headers=headers,
                    data=request_body.encode("utf-8"),
                    timeout=Config.REQUEST_TIMEOUT  # как config::REQUEST_TIMEOUT
                ) as response:
                    
                    if not response.ok:
                        error_text = await response.text()
                        print(f"[ERROR] API returned {response.status}: {error_text[:500]}")
                        raise Exception(f"API Error {response.status}: {error_text}")
                    
                    # Получаем JSON ответ (как AJson::fromBuffer(responseBody))
                    response_json = await response.json()
        
        except ImportError:
            print("[WARNING] aiohttp not installed. Using requests as fallback.")
            
            import requests
            
            response = requests.post(
                self.endpoint_url,
                headers=headers,
                data=request_body.encode("utf-8"),
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if not response.ok:
                print(f"[ERROR] API returned {response.status}: {response.text[:500]}")
                raise Exception(f"API Error {response.status}: {response.text}")
            
            response_json = response.json()
        
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            raise
        
        # Парсим ответ (как ranges::views::transform + to_vector в C++)
        images_data = []
        
        if "images" in response_json and isinstance(response_json["images"], list):
            for img_base64 in response_json["images"]:
                if isinstance(img_base64, str) and len(img_base64) > 0:
                    try:
                        # Конвертируем base64 в bytes (как AImage::fromBuffer(AByteBuffer::fromBase64String(...)))
                        image_data = base64.b64decode(img_base64.split(",", 1)[1] if "," in img_base64 else img_base64)
                        images_data.append(image_data)
                    except Exception as e:
                        print(f"[WARNING] Failed to decode base64 image: {e}")
        
        # Создаем ответ (как Txt2ImgResponse res; в C++)
        result = Txt2ImgResponse(
            images=images_data,
            info=response_json.get("info", "")
        )
        
        print(f"[SUCCESS] Images generated: {len(result.images)}")
        print(f"Info preview: {result.info[:200]}...")
        
        return result
    
    async def txt2img_sync(
        self, 
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 50,
        cfg_scale: float = 2.0,
        **kwargs
    ) -> bytes:
        """
        Удобный синхронный метод для генерации одного изображения.
        
        Args:
            prompt: Описание изображения
            negative_prompt: Негативный промпт
            width: Ширина изображения
            height: Высота изображения
            steps: Количество итераций
            cfg_scale: Scale CFG
            **kwargs: Дополнительные параметры
        
        Returns:
            Бинарные данные PNG изображения
        """
        request = Txt2ImgRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            **kwargs
        )
        
        response = await self.txt2img(request)
        
        if len(response.images) == 0:
            raise ValueError("No images generated")
        
        return response.images[0]


# ============================================================================
# HELPER FUNCTION (для упрощенного использования)
# ============================================================================

async def generate_image(
    prompt: str,
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 50,
    cfg_scale: float = 2.0,
    endpoint_url: Optional[str] = None,
    bearer_key: Optional[str] = None
) -> bytes:
    """
    Функция для генерации изображения из текста (упрощенная обертка).
    
    Args:
        prompt: Описание изображения
        negative_prompt: Негативный промпт
        width, height: Размер изображения
        steps: Количество итераций
        cfg_scale: Scale CFG
        endpoint_url: URL API (опционально)
        bearer_key: Авторизационный ключ (опционально)
    
    Returns:
        Бинарные данные PNG изображения
    
    Raises:
        ValueError: Если endpoint не настроен
        Exception: При ошибках API
    """
    
    client = StableDiffusionClient(
        endpoint_url=endpoint_url,
        bearer_key=bearer_key
    )
    
    image_data = await client.txt2img_sync(prompt=prompt, width=width, height=height, steps=steps)
    
    return image_data


# ============================================================================
# EXAMPLE USAGE & DEMONSTRATION
# ============================================================================

async def main():
    """Демонстрирует работу клиента Stable Diffusion."""
    
    print("\n" + "=" * 60)
    print("STABLE DIFFUSION CLIENT - COMPONENT DEMO")
    print("=" * 60 + "\n")
    
    # Пример 1: Создание клиента с локальным endpoint (как config::ENDPOINT_SD)
    print("[EXAMPLE 1] Create client with local endpoint")
    print("-" * 40)
    
    # Локаный A1111 или ComfyUI endpoint
    client = StableDiffusionClient(
        endpoint_url="http://127.0.0.1:7860/sdapi/v1/txt2img",
        bearer_key=None  # Нет авторизации для локального endpoint
    )
    
    if not client.configured:
        print("[INFO] Client is not configured. Check your local SD server.\n")
        
        print("To use this in production:")
        print("1. Run Stable Diffusion WebUI (A1111) or ComfyUI locally")
        print("2. Update endpoint_url with your actual URL")
        print("3. Add bearer_key if remote API requires authentication\n")
        return
    
    # Пример 2: Создание запроса txt2img (как const Txt2ImgRequest& request в C++)
    print("[EXAMPLE 2] Create text-to-image request")
    print("-" * 40)
    
    request = Txt2ImgRequest(
        prompt="A beautiful sunset over mountains with vibrant colors",
        negative_prompt="blurry, low quality, distorted",
        width=512,
        height=512,
        steps=50,
        cfg_scale=2.0,
        sampler_name="DPM++ 2M",
        batch_size=1
    )
    
    print(f"Request created:")
    print(f"  Prompt: {request.prompt}")
    print(f"  Negative prompt: {request.negative_prompt}")
    print(f"  Dimensions: {request.width}x{request.height}")
    print(f"  Steps: {request.steps}, CFG Scale: {request.cfg_scale}\n")
    
    # Пример 3: Генерация изображения (если endpoint настроен)
    if client.configured:
        print("[EXAMPLE 3] Generate image from prompt")
        print("-" * 40)
        
        try:
            # Используем async для генерации (как co_await в C++)
            image_data = await client.txt2img(request)
            
            if len(image_data.images) > 0:
                print(f"Image generated successfully!")
                print(f"  Format: PNG")
                print(f"  Size: {len(image_data.images[0])} bytes ({len(image_data.images[0]) / 1024:.2f} KB)")
                
                # Сохранение в файл (как бонус)
                import os
                
                output_filename = "generated_image.png"
                with open(output_filename, "wb") as f:
                    f.write(image_data.images[0])
                
                print(f"  Saved to: {os.path.abspath(output_filename)}\n")
            
        except Exception as e:
            print(f"[ERROR] Image generation failed: {e}")
    else:
        print("[SKIPPED] Using unconfigured endpoint - no actual API call\n")


# ============================================================================
# CONFIGURATION LOADERS (для загрузки из файла или окружения)
# ============================================================================

def load_from_environment() -> tuple[str, Optional[str]]:
    """
    Загружает конфигурацию из переменных окружения.
    
    Returns:
        Tuple (endpoint_url, bearer_key)
    """
    endpoint_url = os.environ.get("SD_ENDPOINT_URL") or "http://127.0.0.1:7860/sdapi/v1/txt2img"
    bearer_key = os.environ.get("SD_BEARER_KEY") or None
    
    return endpoint_url, bearer_key


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Попытка загрузки конфигурации из переменных окружения
    endpoint_url, bearer_key = load_from_environment()
    
    print("\nAttempting to load configuration...")
    print(f"Endpoint: {endpoint_url}")
    print(f"Bearer key configured: {'Yes' if bearer_key else 'No'}\n")
    
    # Создание и демонстрация клиента
    asyncio.run(main())
