from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """
    Konfigurasi aplikasi trading bot
    """
    
    # MetaTrader 5 Configuration
    mt5_login: int
    mt5_password: str
    mt5_server: str
    mt5_path: str = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    
    # Telegram Bot Configuration
    telegram_bot_token: str
    telegram_chat_id: str
    
    # Database Configuration
    database_url: str = "sqlite:///./trading_bot.db"
    
    # Trading Configuration
    risk_percentage: float = 2.0
    max_open_positions: int = 5
    symbol_list: str = "EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/trading_bot.log"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    @property
    def symbols(self) -> List[str]:
        """Mengubah string symbol menjadi list"""
        return [symbol.strip() for symbol in self.symbol_list.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instance global settings
settings = Settings()