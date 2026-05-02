from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration"""
    
    # Model settings
    model: str = "qwen3.5:9b"
    temperature: float = 0.2
    
    # Diary settings
    diary_token_count_trigger: int = 20000
    diary_average_entry_size: int = 1000
    diary_injection_max_length: int = 1000
    diary_plagiarism_threshold: float = 0.97
    
    # Chat settings
    chat_min_chars_length: int = 500
    chat_max_chars_length: int = 5000
    
    # Repeat yourself detection
    repeat_yourself_trigger_avg: float = 0.83
    repeat_yourself_trigger_max: float = 0.79
    repeat_yourself_max_history: int = 32
    
    # Request timeout
    request_timeout: int = 600
    
    # Sleep settings
    sleep_max_time: int = 21600  # 6 hours in seconds
    
    # Lockdown mode
    lockdown_mode: bool = False
    papik_chat_id: int = 625207005


# Configuration instance
config = Config()