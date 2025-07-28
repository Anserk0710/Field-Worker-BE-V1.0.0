import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from .technical_analysis import technical_analysis
from ..config.settings import settings


class SignalGenerator:
    """
    Generator sinyal trading berdasarkan analisa multi-timeframe
    """
    
    def __init__(self):
        self.signal_history = []
        self.active_signals = {}
    
    def generate_signal_for_pair(self, symbol: str) -> Dict:
        """
        Generate sinyal untuk satu pair dengan multi-timeframe analysis
        """
        try:
            logger.info(f"Generating signal for {symbol}")
            
            # Lakukan analisa multi-timeframe
            mtf_analysis = technical_analysis.multi_timeframe_analysis(symbol)
            
            if "error" in mtf_analysis:
                logger.error(f"Error in MTF analysis for {symbol}: {mtf_analysis['error']}")
                return {
                    "symbol": symbol,
                    "status": "ERROR",
                    "error": mtf_analysis["error"],
                    "timestamp": datetime.now()
                }
            
            # Extract signal dari analisa
            signal_data = mtf_analysis["signal"]
            analysis_data = mtf_analysis["analysis"]
            
            # Format output sinyal
            signal_output = self.format_signal_output(symbol, signal_data, analysis_data)
            
            # Simpan ke history jika sinyal valid
            if signal_output["direction"] in ["BUY", "SELL"]:
                self.signal_history.append(signal_output)
                self.active_signals[symbol] = signal_output
                logger.info(f"Generated {signal_output['direction']} signal for {symbol}")
            
            return signal_output
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return {
                "symbol": symbol,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def format_signal_output(self, symbol: str, signal_data: Dict, analysis_data: Dict) -> Dict:
        """
        Format output sinyal sesuai requirement: Pair, Timeframe, Entry, SL, TP
        """
        try:
            # Base signal structure
            signal_output = {
                "pair": symbol,
                "direction": signal_data.get("direction", "NONE"),
                "timestamp": datetime.now(),
                "status": "ACTIVE" if signal_data.get("direction") in ["BUY", "SELL"] else "NO_SIGNAL"
            }
            
            # Add entry, SL, TP if signal is valid
            if signal_data.get("direction") in ["BUY", "SELL"]:
                signal_output.update({
                    "entry": round(signal_data.get("entry", 0), 5),
                    "stop_loss": round(signal_data.get("stop_loss", 0), 5),
                    "take_profit": round(signal_data.get("take_profit", 0), 5),
                    "strength": signal_data.get("strength", 0),
                    "reasons": signal_data.get("reason", [])
                })
                
                # Calculate risk/reward ratio
                if signal_output["direction"] == "BUY":
                    risk = signal_output["entry"] - signal_output["stop_loss"]
                    reward = signal_output["take_profit"] - signal_output["entry"]
                else:  # SELL
                    risk = signal_output["stop_loss"] - signal_output["entry"]
                    reward = signal_output["entry"] - signal_output["take_profit"]
                
                signal_output["risk_reward_ratio"] = round(reward / risk, 2) if risk > 0 else 0
            
            # Add timeframe analysis summary
            signal_output["timeframe_analysis"] = self.summarize_timeframe_analysis(analysis_data)
            
            # Add Fibonacci levels if available
            fib_data = self.extract_fibonacci_data(analysis_data)
            if fib_data:
                signal_output["fibonacci"] = fib_data
            
            return signal_output
            
        except Exception as e:
            logger.error(f"Error formatting signal output: {e}")
            return {
                "pair": symbol,
                "direction": "ERROR",
                "error": str(e),
                "timestamp": datetime.now()
            }
    
    def summarize_timeframe_analysis(self, analysis_data: Dict) -> Dict:
        """
        Ringkasan analisa per timeframe
        """
        summary = {}
        
        for timeframe, data in analysis_data.items():
            if "error" not in data:
                summary[timeframe] = {
                    "trend": data.get("trend", "UNKNOWN"),
                    "ma_signal": data.get("ma_signal", "NEUTRAL"),
                    "rsi": round(data.get("rsi", 50), 2),
                    "rsi_signal": data.get("rsi_signal", "NEUTRAL"),
                    "price": round(data.get("price", 0), 5),
                    "ema20": round(data.get("ema20", 0), 5),
                    "ema50": round(data.get("ema50", 0), 5)
                }
            else:
                summary[timeframe] = {"error": data["error"]}
        
        return summary
    
    def extract_fibonacci_data(self, analysis_data: Dict) -> Optional[Dict]:
        """
        Extract Fibonacci levels dari H1 atau H4 analysis
        """
        try:
            # Prioritas: H4 -> H1 -> H1 -> M15
            for tf in ['H4', 'H1', 'M15']:
                if tf in analysis_data and "error" not in analysis_data[tf]:
                    fib_levels = analysis_data[tf].get("fibonacci")
                    if fib_levels:
                        return {
                            "timeframe": tf,
                            "levels": {k: round(v, 5) for k, v in fib_levels.items()}
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Fibonacci data: {e}")
            return None
    
    def generate_signals_for_all_pairs(self) -> List[Dict]:
        """
        Generate sinyal untuk semua pair yang dikonfigurasi
        """
        try:
            signals = []
            
            for symbol in settings.symbols:
                signal = self.generate_signal_for_pair(symbol)
                signals.append(signal)
                
                # Small delay to avoid overwhelming MT5
                import time
                time.sleep(0.5)
            
            logger.info(f"Generated signals for {len(signals)} pairs")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals for all pairs: {e}")
            return []
    
    def get_active_signals(self) -> List[Dict]:
        """
        Mendapatkan sinyal aktif (BUY/SELL)
        """
        return [signal for signal in self.active_signals.values() 
                if signal.get("direction") in ["BUY", "SELL"]]
    
    def get_signal_history(self, limit: int = 10) -> List[Dict]:
        """
        Mendapatkan history sinyal
        """
        return self.signal_history[-limit:] if self.signal_history else []
    
    def format_signal_message(self, signal: Dict) -> str:
        """
        Format sinyal untuk dikirim via Telegram
        """
        try:
            if signal.get("direction") not in ["BUY", "SELL"]:
                return f"❌ **{signal['pair']}**: No valid signal"
            
            # Emoji untuk direction
            direction_emoji = "🟢" if signal["direction"] == "BUY" else "🔴"
            
            message = f"""
{direction_emoji} **SIGNAL: {signal['pair']}**

📊 **Direction**: {signal['direction']}
💰 **Entry**: {signal['entry']}
🛑 **Stop Loss**: {signal['stop_loss']}
🎯 **Take Profit**: {signal['take_profit']}
📈 **R/R Ratio**: 1:{signal.get('risk_reward_ratio', 0)}
⚡ **Strength**: {signal.get('strength', 0)}/4

🔍 **Multi-Timeframe Analysis**:
"""
            
            # Add timeframe analysis
            tf_analysis = signal.get("timeframe_analysis", {})
            for tf in ['H4', 'H1', 'M15', 'M5']:
                if tf in tf_analysis and "error" not in tf_analysis[tf]:
                    data = tf_analysis[tf]
                    trend_emoji = "📈" if data['trend'] == "BULLISH" else "📉" if data['trend'] == "BEARISH" else "➡️"
                    rsi_emoji = "🔴" if data['rsi'] > 70 else "🟢" if data['rsi'] < 30 else "🟡"
                    
                    message += f"• **{tf}**: {trend_emoji} {data['trend']} | RSI: {rsi_emoji} {data['rsi']}\n"
            
            # Add reasons
            if signal.get("reasons"):
                message += f"\n💡 **Reasons**:\n"
                for reason in signal["reasons"]:
                    message += f"• {reason}\n"
            
            # Add Fibonacci if available
            if signal.get("fibonacci"):
                fib_data = signal["fibonacci"]
                message += f"\n📐 **Fibonacci ({fib_data['timeframe']})**:\n"
                key_levels = ['61.8%', '50%', '38.2%']
                for level in key_levels:
                    if level in fib_data['levels']:
                        message += f"• {level}: {fib_data['levels'][level]}\n"
            
            message += f"\n⏰ **Time**: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting signal message: {e}")
            return f"❌ Error formatting signal for {signal.get('pair', 'Unknown')}"
    
    def validate_signal_rules(self, analysis_data: Dict) -> bool:
        """
        Validasi rules multi-timeframe sesuai requirement:
        - M5: MA fast > MA slow (entry)
        - M15: RSI oversold/overbought
        - H1: Trend confirmation
        - H4: Structure confirmation
        """
        try:
            # Check M5 MA signal
            if 'M5' not in analysis_data or "error" in analysis_data['M5']:
                return False
            
            m5_data = analysis_data['M5']
            if m5_data.get('ma_signal') not in ['BUY', 'SELL']:
                return False
            
            # Check M15 RSI
            if 'M15' not in analysis_data or "error" in analysis_data['M15']:
                return False
            
            m15_data = analysis_data['M15']
            if m15_data.get('rsi_signal') == 'NEUTRAL':
                return False
            
            # Check H1 trend
            if 'H1' not in analysis_data or "error" in analysis_data['H1']:
                return False
            
            h1_data = analysis_data['H1']
            if h1_data.get('trend') not in ['BULLISH', 'BEARISH']:
                return False
            
            # Check H4 structure (optional but preferred)
            if 'H4' in analysis_data and "error" not in analysis_data['H4']:
                h4_data = analysis_data['H4']
                if h4_data.get('trend') == 'UNKNOWN':
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating signal rules: {e}")
            return False


# Global instance
signal_generator = SignalGenerator()