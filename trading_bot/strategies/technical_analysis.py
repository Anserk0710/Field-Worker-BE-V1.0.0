import pandas as pd
import numpy as np
import MetaTrader5 as mt5
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from loguru import logger

from ..mt5.connection import mt5_connection
from ..config.settings import settings


class TechnicalAnalysis:
    """
    Kelas untuk analisa teknikal multi-timeframe
    """
    
    # Timeframe constants
    TIMEFRAMES = {
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1
    }
    
    def __init__(self):
        self.data_cache = {}
        self.cache_timeout = 300  # 5 minutes cache
    
    def get_ohlc_data(self, symbol: str, timeframe: str, count: int = 500) -> Optional[pd.DataFrame]:
        """
        Mengambil data OHLC untuk symbol dan timeframe tertentu
        """
        try:
            if not mt5_connection.check_connection():
                logger.warning("MT5 not connected, attempting to reconnect...")
                if not mt5_connection.connect():
                    logger.error("Failed to reconnect to MT5")
                    return None
            
            cache_key = f"{symbol}_{timeframe}_{count}"
            current_time = datetime.now()
            
            # Check cache
            if cache_key in self.data_cache:
                cached_data, cache_time = self.data_cache[cache_key]
                if (current_time - cache_time).seconds < self.cache_timeout:
                    return cached_data
            
            # Get data from MT5
            mt5_timeframe = self.TIMEFRAMES.get(timeframe)
            if not mt5_timeframe:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            rates = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            if rates is None:
                logger.error(f"Failed to get rates for {symbol} {timeframe}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            # Cache the data
            self.data_cache[cache_key] = (df, current_time)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting OHLC data for {symbol} {timeframe}: {e}")
            return None
    
    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        """
        Menghitung Exponential Moving Average
        """
        return data.ewm(span=period).mean()
    
    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        """
        Menghitung Simple Moving Average
        """
        return data.rolling(window=period).mean()
    
    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """
        Menghitung Relative Strength Index
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def find_swing_points(self, df: pd.DataFrame, window: int = 5) -> Tuple[List, List]:
        """
        Mencari swing high dan swing low untuk Fibonacci
        """
        highs = []
        lows = []
        
        for i in range(window, len(df) - window):
            # Check for swing high
            if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
                highs.append((df.index[i], df['high'].iloc[i]))
            
            # Check for swing low
            if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
                lows.append((df.index[i], df['low'].iloc[i]))
        
        return highs, lows
    
    def calculate_fibonacci_levels(self, high_price: float, low_price: float) -> Dict[str, float]:
        """
        Menghitung level Fibonacci retracement
        """
        diff = high_price - low_price
        
        levels = {
            '0%': high_price,
            '23.6%': high_price - (diff * 0.236),
            '38.2%': high_price - (diff * 0.382),
            '50%': high_price - (diff * 0.5),
            '61.8%': high_price - (diff * 0.618),
            '78.6%': high_price - (diff * 0.786),
            '100%': low_price
        }
        
        return levels
    
    def get_trend_direction(self, df: pd.DataFrame) -> str:
        """
        Menentukan arah trend berdasarkan EMA
        """
        if len(df) < 50:
            return "UNKNOWN"
        
        ema20 = self.calculate_ema(df['close'], 20)
        ema50 = self.calculate_ema(df['close'], 50)
        
        current_ema20 = ema20.iloc[-1]
        current_ema50 = ema50.iloc[-1]
        
        if current_ema20 > current_ema50:
            return "BULLISH"
        elif current_ema20 < current_ema50:
            return "BEARISH"
        else:
            return "SIDEWAYS"
    
    def analyze_single_timeframe(self, symbol: str, timeframe: str) -> Dict:
        """
        Analisa teknikal untuk satu timeframe
        """
        try:
            df = self.get_ohlc_data(symbol, timeframe)
            if df is None or len(df) < 100:
                return {"error": f"Insufficient data for {symbol} {timeframe}"}
            
            # Calculate indicators
            ema20 = self.calculate_ema(df['close'], 20)
            ema50 = self.calculate_ema(df['close'], 50)
            rsi = self.calculate_rsi(df['close'], 14)
            
            # Get current values
            current_price = df['close'].iloc[-1]
            current_ema20 = ema20.iloc[-1]
            current_ema50 = ema50.iloc[-1]
            current_rsi = rsi.iloc[-1]
            
            # Determine trend
            trend = self.get_trend_direction(df)
            
            # MA signal
            ma_signal = "BUY" if current_ema20 > current_ema50 else "SELL"
            
            # RSI signal
            rsi_signal = "OVERSOLD" if current_rsi < 30 else "OVERBOUGHT" if current_rsi > 70 else "NEUTRAL"
            
            # Find swing points for Fibonacci
            highs, lows = self.find_swing_points(df)
            
            fib_levels = None
            if len(highs) > 0 and len(lows) > 0:
                recent_high = max(highs, key=lambda x: x[0])
                recent_low = min(lows, key=lambda x: x[0])
                fib_levels = self.calculate_fibonacci_levels(recent_high[1], recent_low[1])
            
            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": datetime.now(),
                "price": current_price,
                "ema20": current_ema20,
                "ema50": current_ema50,
                "rsi": current_rsi,
                "trend": trend,
                "ma_signal": ma_signal,
                "rsi_signal": rsi_signal,
                "fibonacci": fib_levels,
                "swing_highs": highs[-5:] if len(highs) > 5 else highs,  # Last 5 swing points
                "swing_lows": lows[-5:] if len(lows) > 5 else lows
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol} {timeframe}: {e}")
            return {"error": str(e)}
    
    def multi_timeframe_analysis(self, symbol: str) -> Dict:
        """
        Analisa multi-timeframe untuk satu symbol
        """
        try:
            timeframes = ['M5', 'M15', 'H1', 'H4']
            analysis = {}
            
            for tf in timeframes:
                analysis[tf] = self.analyze_single_timeframe(symbol, tf)
            
            # Generate multi-timeframe signal
            signal = self.generate_mtf_signal(analysis)
            
            return {
                "symbol": symbol,
                "timestamp": datetime.now(),
                "analysis": analysis,
                "signal": signal
            }
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis for {symbol}: {e}")
            return {"error": str(e)}
    
    def generate_mtf_signal(self, analysis: Dict) -> Dict:
        """
        Generate trading signal berdasarkan multi-timeframe analysis
        
        Rules:
        - M5: MA fast > MA slow (entry)
        - M15: RSI oversold/overbought
        - H1: Trend confirmation
        - H4: Structure confirmation
        """
        try:
            signal = {
                "direction": "NONE",
                "strength": 0,
                "entry": None,
                "stop_loss": None,
                "take_profit": None,
                "reason": []
            }
            
            # Check if all timeframes have valid data
            valid_tfs = {tf: data for tf, data in analysis.items() if "error" not in data}
            if len(valid_tfs) < 3:
                signal["reason"].append("Insufficient timeframe data")
                return signal
            
            # Get current price from M5
            if 'M5' in valid_tfs:
                current_price = valid_tfs['M5']['price']
                signal["entry"] = current_price
            
            # Rule 1: M5 MA Signal
            m5_signal = None
            if 'M5' in valid_tfs:
                m5_signal = valid_tfs['M5']['ma_signal']
                if m5_signal == "BUY":
                    signal["strength"] += 1
                    signal["reason"].append("M5: EMA20 > EMA50")
                elif m5_signal == "SELL":
                    signal["strength"] -= 1
                    signal["reason"].append("M5: EMA20 < EMA50")
            
            # Rule 2: M15 RSI
            if 'M15' in valid_tfs:
                rsi_signal = valid_tfs['M15']['rsi_signal']
                if rsi_signal == "OVERSOLD" and m5_signal == "BUY":
                    signal["strength"] += 1
                    signal["reason"].append("M15: RSI Oversold")
                elif rsi_signal == "OVERBOUGHT" and m5_signal == "SELL":
                    signal["strength"] += 1
                    signal["reason"].append("M15: RSI Overbought")
            
            # Rule 3: H1 Trend
            if 'H1' in valid_tfs:
                h1_trend = valid_tfs['H1']['trend']
                if h1_trend == "BULLISH" and m5_signal == "BUY":
                    signal["strength"] += 1
                    signal["reason"].append("H1: Bullish Trend")
                elif h1_trend == "BEARISH" and m5_signal == "SELL":
                    signal["strength"] += 1
                    signal["reason"].append("H1: Bearish Trend")
            
            # Rule 4: H4 Structure
            if 'H4' in valid_tfs:
                h4_trend = valid_tfs['H4']['trend']
                if h4_trend == "BULLISH" and signal["strength"] > 0:
                    signal["strength"] += 1
                    signal["reason"].append("H4: Bullish Structure")
                elif h4_trend == "BEARISH" and signal["strength"] < 0:
                    signal["strength"] += 1
                    signal["reason"].append("H4: Bearish Structure")
            
            # Determine final signal
            if signal["strength"] >= 3:
                signal["direction"] = "BUY"
                # Calculate SL and TP for BUY
                if signal["entry"]:
                    atr = self.calculate_atr(analysis)
                    signal["stop_loss"] = signal["entry"] - (atr * 1.5)
                    signal["take_profit"] = signal["entry"] + (atr * 2.0)
                    
            elif signal["strength"] <= -3:
                signal["direction"] = "SELL"
                # Calculate SL and TP for SELL
                if signal["entry"]:
                    atr = self.calculate_atr(analysis)
                    signal["stop_loss"] = signal["entry"] + (atr * 1.5)
                    signal["take_profit"] = signal["entry"] - (atr * 2.0)
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating MTF signal: {e}")
            return {"direction": "ERROR", "reason": [str(e)]}
    
    def calculate_atr(self, analysis: Dict, period: int = 14) -> float:
        """
        Calculate Average True Range for SL/TP calculation
        """
        try:
            # Use H1 data for ATR calculation
            if 'H1' not in analysis or 'error' in analysis['H1']:
                return 0.001  # Default ATR
            
            symbol = analysis['H1']['symbol']
            df = self.get_ohlc_data(symbol, 'H1', 100)
            
            if df is None or len(df) < period:
                return 0.001
            
            # Calculate True Range
            df['tr1'] = df['high'] - df['low']
            df['tr2'] = abs(df['high'] - df['close'].shift(1))
            df['tr3'] = abs(df['low'] - df['close'].shift(1))
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # Calculate ATR
            atr = df['tr'].rolling(window=period).mean().iloc[-1]
            
            return atr if not pd.isna(atr) else 0.001
            
        except Exception as e:
            logger.error(f"Error calculating ATR: {e}")
            return 0.001


# Global instance
technical_analysis = TechnicalAnalysis()