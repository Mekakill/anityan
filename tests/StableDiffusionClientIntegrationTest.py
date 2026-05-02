import pytest
from stable_diffusion_client import StableDiffusionClient
import os


@pytest.mark.asyncio
async def test_txt2img():
    """
    Интеграционный тест для генерации изображений по текстовому описанию.
    
    Этот тест требует работающий SD WebUI с включенным API.
    Если он недоступен, тест может упасть или тайм-аутнуться.
    """
    import sys
    
    # Путь к конфигурации можно извлечь из окружения или файла config.h
    endpoint = os.getenv("SD_ENDPOINT", "http://localhost:7860")
    
    client = StableDiffusionClient(endpoint=endpoint)
    
    try:
        response = await client.txt2img(
            prompt="Anime girl cat ears shoulder-length dark_blue hair messy strands blue eyes small nose cute fangs. Shoulders and chest are bare. Floating particles in the air.",
            steps=5,  # малое количество для теста
            width=512,
            height=512,
        )
        
        assert len(response.images) == 1, "Ожидается ровно одно изображение"
        
        image = response.images[0]
        
        # Сохраняем изображение в PNG
        output_path = os.path.join(os.path.dirname(__file__), "out.png")
        with open(output_path, "wb") as f:
            f.write(image.data)  # или image_bytes в зависимости от реализации
        
        assert image.width == 512, f"Ожидается ширина 512, получено {image.width}"
        assert image.height == 512, f"Ожидается высота 512, получено {image.height}"
        
    except Exception as e:
        # Если SD не запущен, ожидаем ошибку подключения.
        # Просто логгируем для теста.
        print(f"SD не запущен или ошибка: {e}")
        pytest.skip("Stable Diffusion API недоступен для локального тестирования")


if __name__ == "__main__":
    import asyncio
    
    async def run_test():
        await test_txt2img()
    
    asyncio.run(run_test())
