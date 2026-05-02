from setuptools import setup, find_packages


def read_requirements():
    with open("requirements.txt", "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="kuni",
    version="0.0.1",
    author="Alex2772",
    description="LLM character AI that interacts with the world through Telegram",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=read_requirements(),
    extras_require={
        "dev": ["pytest>=7.4.0", "pytest-asyncio>=0.21.0", "mock>=5.0.0"]
    },
    entry_points={
        "console_scripts": [
            "kuni=kuni.main:main",
        ],
    },
)