import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from telegram.constants import ParseMode
from typing import Dict, Any
from loguru import logger
from datetime import datetime

from ..config.settings import settings
from ..mt5.connection import mt5_connection
from ..strategies.signal_generator import signal_generator


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
        Handler untuk command /analisa [PAIR] atau /analisa untuk semua pair
        """
        try:
            # Parse command arguments
            args = context.args
            target_symbol = args[0].upper() if args else None
            
            # Kirim pesan loading
            if target_symbol:
                loading_message = await update.message.reply_text(f"🔄 Sedang menganalisis {target_symbol}...")
            else:
                loading_message = await update.message.reply_text("🔄 Sedang menganalisis semua pair...")
            
            # Cek koneksi MT5
            if not mt5_connection.check_connection():
                await loading_message.edit_text("❌ Koneksi MT5 tidak tersedia. Mencoba menghubungkan...")
                if not mt5_connection.connect():
                    await loading_message.edit_text("❌ Gagal terhubung ke MT5. Periksa konfigurasi!")
                    return
            
            # Generate signals
            if target_symbol:
                # Analisis untuk satu pair
                if target_symbol not in settings.symbols:
                    await loading_message.edit_text(f"❌ {target_symbol} tidak tersedia. Gunakan /pairlist untuk melihat pair yang tersedia.")
                    return
                
                signal = signal_generator.generate_signal_for_pair(target_symbol)
                
                if signal.get("status") == "ERROR":
                    await loading_message.edit_text(f"❌ Error menganalisis {target_symbol}: {signal.get('error', 'Unknown error')}")
                    return
                
                # Format dan kirim hasil analisis
                message = signal_generator.format_signal_message(signal)
                await loading_message.edit_text(message, parse_mode=ParseMode.MARKDOWN)
                
            else:
                # Analisis untuk semua pair
                signals = signal_generator.generate_signals_for_all_pairs()
                
                # Filter hanya sinyal aktif
                active_signals = [s for s in signals if s.get("direction") in ["BUY", "SELL"]]
                
                if active_signals:
                    # Kirim ringkasan
                    summary = f"""
📊 **MULTI-TIMEFRAME ANALYSIS SUMMARY**
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

🎯 **Active Signals**: {len(active_signals)} found

"""
                    for signal in active_signals[:5]:  # Limit 5 sinyal pertama
                        direction_emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
                        summary += f"{direction_emoji} **{signal['pair']}** {signal['direction']} | Entry: {signal['entry']} | R/R: 1:{signal.get('risk_reward_ratio', 0)}\n"
                    
                    if len(active_signals) > 5:
                        summary += f"\n... dan {len(active_signals) - 5} sinyal lainnya"
                    
                    summary += f"\n\n💡 Gunakan `/analisa [PAIR]` untuk detail lengkap"
                    
                    await loading_message.edit_text(summary, parse_mode=ParseMode.MARKDOWN)
                    
                    # Kirim detail untuk sinyal terkuat
                    if active_signals:
                        strongest_signal = max(active_signals, key=lambda x: abs(x.get('strength', 0)))
                        detail_message = signal_generator.format_signal_message(strongest_signal)
                        await update.message.reply_text(f"🏆 **STRONGEST SIGNAL**:\n{detail_message}", parse_mode=ParseMode.MARKDOWN)
                
                else:
                    # Tidak ada sinyal aktif
                    no_signal_text = f"""
📊 **MULTI-TIMEFRAME ANALYSIS**
⏰ {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

❌ **No Active Signals**

Analyzed {len(signals)} pairs, no valid trading signals found based on multi-timeframe rules:
• M5: MA crossover
• M15: RSI oversold/overbought
• H1: Trend confirmation
• H4: Structure confirmation

🔍 Market may be in consolidation or conditions not met.
Try again in a few minutes or use `/analisa [PAIR]` for specific analysis.
                    """
                    await loading_message.edit_text(no_signal_text, parse_mode=ParseMode.MARKDOWN)
            
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
    
    async def pairlist_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /pairlist
        """
        try:
            pairlist_message = f"""
📋 **AVAILABLE TRADING PAIRS**

**Configured Pairs** ({len(settings.symbols)}):
"""
            
            # Group pairs by type
            major_pairs = []
            minor_pairs = []
            exotic_pairs = []
            
            for symbol in settings.symbols:
                if symbol in ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD']:
                    major_pairs.append(symbol)
                elif 'USD' in symbol:
                    minor_pairs.append(symbol)
                else:
                    exotic_pairs.append(symbol)
            
            if major_pairs:
                pairlist_message += f"\n🟢 **Major Pairs:**\n"
                for pair in major_pairs:
                    pairlist_message += f"• {pair}\n"
            
            if minor_pairs:
                pairlist_message += f"\n🟡 **Minor Pairs:**\n"
                for pair in minor_pairs:
                    pairlist_message += f"• {pair}\n"
            
            if exotic_pairs:
                pairlist_message += f"\n🟠 **Other Pairs:**\n"
                for pair in exotic_pairs:
                    pairlist_message += f"• {pair}\n"
            
            pairlist_message += f"""

**Usage:**
• `/analisa` - Analyze all pairs
• `/analisa [PAIR]` - Analyze specific pair
• Example: `/analisa EURUSD`

**Multi-Timeframe Analysis:**
• M5: Entry signals (MA crossover)
• M15: RSI confirmation
• H1: Trend direction
• H4: Market structure
            """
            
            await update.message.reply_text(pairlist_message, parse_mode=ParseMode.MARKDOWN)
            
        except Exception as e:
            logger.error(f"Error in pairlist command: {e}")
            await update.message.reply_text("❌ Terjadi kesalahan saat mengambil daftar pair.")
    
    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """
        Handler untuk command /help
        """
        help_message = """
❓ **BANTUAN PENGGUNAAN BOT**

**Perintah Dasar:**
/start - Memulai bot dan menampilkan menu utama
/analisa - Analisis multi-timeframe semua pair
/analisa [PAIR] - Analisis spesifik pair (contoh: /analisa EURUSD)
/pairlist - Daftar pair yang tersedia
/status - Status koneksi dan sistem
/account - Informasi akun trading
/help - Bantuan penggunaan

**Multi-Timeframe Analysis:**
🔸 **M5**: Entry signals berdasarkan MA crossover
🔸 **M15**: Konfirmasi RSI (oversold/overbought)
🔸 **H1**: Konfirmasi trend direction
🔸 **H4**: Konfirmasi market structure

**Output Sinyal:**
• Direction: BUY/SELL
• Entry Price: Harga masuk
• Stop Loss: Level SL
• Take Profit: Level TP
• Risk/Reward Ratio
• Fibonacci levels (jika tersedia)

**Contoh Penggunaan:**
• `/analisa` → Scan semua pair
• `/analisa EURUSD` → Analisis EURUSD
• `/pairlist` → Lihat pair tersedia
• `/status` → Cek koneksi MT5

**Rules Multi-Timeframe:**
1. **M5**: EMA20 > EMA50 (BUY) atau EMA20 < EMA50 (SELL)
2. **M15**: RSI < 30 (oversold) atau RSI > 70 (overbought)
3. **H1**: Trend bullish/bearish confirmation
4. **H4**: Market structure alignment

⚠️ **Disclaimer:**
Bot ini untuk tujuan edukasi dan analisis. Bukan rekomendasi investasi.
Selalu gunakan manajemen risiko yang tepat.
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
        self.application.add_handler(CommandHandler("pairlist", self.pairlist_command))
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