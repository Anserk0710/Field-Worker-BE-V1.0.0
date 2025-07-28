import asyncio
import signal
import sys
from loguru import logger

from .config.settings import settings
from .utils.logger import setup_logger
from .mt5.connection import mt5_connection
from .telegram.bot import trading_bot


class TradingBotApp:
    """
    Aplikasi utama Trading Bot
    """
    
    def __init__(self):
        self.is_running = False
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """
        Setup signal handlers untuk graceful shutdown
        """
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """
        Handler untuk signal shutdown
        """
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False
    
    async def startup(self):
        """
        Startup sequence untuk aplikasi
        """
        try:
            logger.info("🚀 Starting Trading Bot Application...")
            
            # 1. Setup logger
            setup_logger()
            logger.info("✅ Logger initialized")
            
            # 2. Validasi konfigurasi
            self._validate_config()
            logger.info("✅ Configuration validated")
            
            # 3. Koneksi ke MT5
            logger.info("🔌 Connecting to MetaTrader 5...")
            if not mt5_connection.connect():
                raise Exception("Failed to connect to MetaTrader 5")
            logger.info("✅ MetaTrader 5 connected successfully")
            
            # 4. Test koneksi Telegram (optional)
            logger.info("📱 Testing Telegram bot configuration...")
            # Telegram connection akan ditest saat bot dimulai
            
            logger.info("🎉 All systems ready!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            return False
    
    def _validate_config(self):
        """
        Validasi konfigurasi yang diperlukan
        """
        required_configs = [
            ('mt5_login', 'MetaTrader 5 login'),
            ('mt5_password', 'MetaTrader 5 password'),
            ('mt5_server', 'MetaTrader 5 server'),
            ('telegram_bot_token', 'Telegram bot token'),
        ]
        
        missing_configs = []
        for config_key, config_name in required_configs:
            try:
                value = getattr(settings, config_key)
                if not value or (isinstance(value, str) and value.startswith('your_')):
                    missing_configs.append(config_name)
            except AttributeError:
                missing_configs.append(config_name)
        
        if missing_configs:
            raise Exception(f"Missing required configurations: {', '.join(missing_configs)}")
    
    async def shutdown(self):
        """
        Shutdown sequence untuk aplikasi
        """
        try:
            logger.info("🔄 Shutting down Trading Bot Application...")
            
            # 1. Stop Telegram bot
            if trading_bot.is_running:
                logger.info("📱 Stopping Telegram bot...")
                await trading_bot.stop_bot()
                logger.info("✅ Telegram bot stopped")
            
            # 2. Disconnect MT5
            if mt5_connection.is_connected:
                logger.info("🔌 Disconnecting from MetaTrader 5...")
                mt5_connection.disconnect()
                logger.info("✅ MetaTrader 5 disconnected")
            
            logger.info("👋 Trading Bot Application shutdown complete")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    async def run(self):
        """
        Menjalankan aplikasi utama
        """
        try:
            # Startup
            if not await self.startup():
                logger.error("❌ Failed to start application")
                return False
            
            self.is_running = True
            
            # Start Telegram bot
            logger.info("📱 Starting Telegram bot...")
            bot_task = asyncio.create_task(trading_bot.start_bot())
            
            # Main loop
            logger.info("🔄 Trading Bot is running...")
            while self.is_running:
                try:
                    # Health check
                    if not mt5_connection.check_connection():
                        logger.warning("⚠️ MT5 connection lost, attempting to reconnect...")
                        if mt5_connection.connect():
                            logger.info("✅ MT5 reconnected successfully")
                        else:
                            logger.error("❌ Failed to reconnect MT5")
                    
                    # Sleep untuk menghindari busy waiting
                    await asyncio.sleep(30)  # Check setiap 30 detik
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"❌ Error in main loop: {e}")
                    await asyncio.sleep(5)
            
            # Cancel bot task
            if bot_task and not bot_task.done():
                bot_task.cancel()
                try:
                    await bot_task
                except asyncio.CancelledError:
                    pass
            
            return True
            
        except KeyboardInterrupt:
            logger.info("⌨️ Keyboard interrupt received")
            return True
        except Exception as e:
            logger.error(f"❌ Application error: {e}")
            return False
        finally:
            await self.shutdown()


async def main():
    """
    Entry point utama aplikasi
    """
    app = TradingBotApp()
    success = await app.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)