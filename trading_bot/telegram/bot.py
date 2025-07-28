import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from telegram.constants import ParseMode
from typing import Dict, Any
from loguru import logger
from datetime import datetime

from ..config.settings import settings
from ..mt5.connection import mt5_connection


class TradingBot:
    """
    Kelas untuk mengelola bot Telegram trading
    """
    
    def __init__(self):
        self.application = None
        self.is_running = False
    
    async def start_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /start
        """
        try:
            user = update.effective_user
            welcome_message = f"""
🤖 **Selamat Datang di Trading Bot!**

Halo {user.first_name}! 👋

Bot ini akan membantu Anda dalam:
• 📊 Analisis teknikal real-time
• 💹 Monitoring posisi trading
• 📈 Sinyal trading otomatis
• 💰 Manajemen risiko

**Perintah yang tersedia:**
/start - Menampilkan pesan selamat datang
/analisa - Melakukan analisis teknikal
/status - Cek status koneksi MT5
/account - Info akun trading
/help - Bantuan penggunaan bot

Gunakan /help untuk informasi lebih detail! 🚀
            """
            
            # Keyboard inline untuk navigasi cepat
            keyboard = [
                [
                    InlineKeyboardButton("📊 Analisa", callback_data="analisa"),
                    InlineKeyboardButton("📈 Status", callback_data="status")
                ],
                [
                    InlineKeyboardButton("💰 Account Info", callback_data="account"),
                    InlineKeyboardButton("❓ Help", callback_data="help")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                welcome_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            logger.info(f"User {user.username} ({user.id}) started the bot")
            
        except Exception as e:
            logger.error(f"Error in start command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan. Silakan coba lagi.")
    
    async def analisa_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /analisa
        """
        try:
            # Kirim pesan loading
            loading_message = await update.message.reply_text("🔄 Sedang melakukan analisis...")
            
            # Cek koneksi MT5
            if not mt5_connection.check_connection():
                await loading_message.edit_text("❌ Koneksi MT5 tidak tersedia. Mencoba menghubungkan...")
                if not mt5_connection.connect():
                    await loading_message.edit_text("❌ Gagal terhubung ke MT5. Periksa konfigurasi!")
                    return
            
            # Ambil data untuk analisis
            analysis_results = []
            
            for symbol in settings.symbols[:3]:  # Analisis 3 symbol pertama
                symbol_info = mt5_connection.get_symbol_info(symbol)
                if symbol_info:
                    # Analisis sederhana berdasarkan bid/ask
                    spread = symbol_info['ask'] - symbol_info['bid']
                    spread_pips = spread / symbol_info['point']
                    
                    status = "🟢 BAIK" if spread_pips < 5 else "🟡 NORMAL" if spread_pips < 10 else "🔴 TINGGI"
                    
                    analysis_results.append(f"""
**{symbol}**
💰 Bid: {symbol_info['bid']:.5f}
💰 Ask: {symbol_info['ask']:.5f}
📊 Spread: {spread_pips:.1f} pips {status}
                    """)
            
            if analysis_results:
                analysis_text = f"""
📊 **ANALISIS TEKNIKAL**
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{''.join(analysis_results)}

🔍 **Rekomendasi:**
• Monitor pergerakan harga secara real-time
• Perhatikan level support/resistance
• Gunakan manajemen risiko yang tepat

*Analisis ini bersifat informatif dan bukan rekomendasi investasi*
                """
            else:
                analysis_text = "❌ Tidak dapat mengambil data untuk analisis. Periksa koneksi MT5."
            
            await loading_message.edit_text(analysis_text, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in analisa command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat melakukan analisis.")
    
    async def status_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /status
        """
        try:
            # Cek status koneksi
            mt5_status = "🟢 Terhubung" if mt5_connection.check_connection() else "🔴 Terputus"
            
            status_message = f"""
🔍 **STATUS SISTEM**

📡 **Koneksi MT5:** {mt5_status}
🤖 **Bot Telegram:** 🟢 Aktif
⏰ **Waktu:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📊 **Konfigurasi:**
• Risk: {settings.risk_percentage}%
• Max Positions: {settings.max_open_positions}
• Symbols: {len(settings.symbols)} pairs

🔧 **Server:** {settings.mt5_server if hasattr(settings, 'mt5_server') else 'N/A'}
            """
            
            await update.message.reply_text(status_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengecek status.")
    
    async def account_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /account
        """
        try:
            if not mt5_connection.check_connection():
                await update.message.reply_text("❌ MT5 tidak terhubung. Gunakan /status untuk info lebih lanjut.")
                return
            
            account_info = mt5_connection.get_account_info()
            if not account_info:
                await update.message.reply_text("❌ Tidak dapat mengambil informasi akun.")
                return
            
            account_message = f"""
💰 **INFORMASI AKUN**

🏦 **Broker:** {account_info.get('company', 'N/A')}
🔢 **Login:** {account_info.get('login', 'N/A')}
🌐 **Server:** {account_info.get('server', 'N/A')}
💱 **Currency:** {account_info.get('currency', 'N/A')}

💵 **Balance:** ${account_info.get('balance', 0):,.2f}
💎 **Equity:** ${account_info.get('equity', 0):,.2f}
📊 **Margin:** ${account_info.get('margin', 0):,.2f}
🆓 **Free Margin:** ${account_info.get('margin_free', 0):,.2f}
📈 **Margin Level:** {account_info.get('margin_level', 0):,.2f}%

⚡ **Leverage:** 1:{account_info.get('leverage', 0)}
✅ **Trading Allowed:** {'Ya' if account_info.get('trade_allowed') else 'Tidak'}
            """
            
            await update.message.reply_text(account_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in account command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengambil info akun.")
    
    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /help
        """
        help_message = """
❓ **BANTUAN PENGGUNAAN BOT**

**Perintah Dasar:**
/start - Memulai bot dan menampilkan menu utama
/analisa - Melakukan analisis teknikal real-time
/status - Mengecek status koneksi dan sistem
/account - Menampilkan informasi akun trading
/help - Menampilkan bantuan ini

**Fitur Bot:**
🔸 Analisis teknikal otomatis
🔸 Monitoring spread real-time  
🔸 Informasi akun dan balance
🔸 Status koneksi MT5
🔸 Notifikasi trading (coming soon)

**Tips Penggunaan:**
• Pastikan MT5 sudah berjalan dan login
• Periksa koneksi internet yang stabil
• Gunakan /status untuk cek sistem
• Bot akan memberikan analisis informatif

**Support:**
Jika mengalami masalah, periksa:
1. Koneksi MT5 (/status)
2. Konfigurasi bot (.env file)
3. Log sistem untuk error detail

*Bot ini untuk tujuan edukasi dan informasi*
        """
        
        await update.message.reply_text(help_message, parse_mode=ParseMode.MARKDOWN)
    
    async def unknown_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk perintah yang tidak dikenal
        """
        await update.message.reply_text(
            "❓ Perintah tidak dikenal. Gunakan /help untuk melihat daftar perintah yang tersedia."
        )
    
    def setup_handlers(self):
        """
        Setup semua command handlers
        """
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("analisa", self.analisa_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("account", self.account_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Handler untuk pesan yang tidak dikenal
        self.application.add_handler(MessageHandler(filters.COMMAND, self.unknown_command))
        
        logger.info("All command handlers setup completed")
    
    async def start_bot(self):
        """
        Memulai bot Telegram
        """
        try:
            # Buat aplikasi bot
            self.application = Application.builder().token(settings.telegram_bot_token).build()
            
            # Setup handlers
            self.setup_handlers()
            
            # Start bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.is_running = True
            logger.info("Telegram bot started successfully")
            
            # Keep running
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop_bot(self):
        """
        Menghentikan bot
        """
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
            self.is_running = False
            logger.info("Telegram bot stopped")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")


# Instance global bot
trading_bot = TradingBot()