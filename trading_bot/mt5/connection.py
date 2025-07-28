import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from loguru import logger
from ..config.settings import settings


class MT5Connection:
    """
    Kelas untuk mengelola koneksi ke MetaTrader 5
    """
    
    def __init__(self):
        self.is_connected = False
        self.account_info = None
    
    def initialize(self) -> bool:
        """
        Inisialisasi koneksi ke MT5
        """
        try:
            # Initialize MT5 connection
            if not mt5.initialize(path=settings.mt5_path):
                logger.error(f"initialize() failed, error code = {mt5.last_error()}")
                return False
            
            logger.info("MT5 initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing MT5: {e}")
            return False
    
    def login(self) -> bool:
        """
        Login ke akun MT5
        """
        try:
            # Login to MT5 account
            authorized = mt5.login(
                login=settings.mt5_login,
                password=settings.mt5_password,
                server=settings.mt5_server
            )
            
            if not authorized:
                logger.error(f"Login failed, error code = {mt5.last_error()}")
                return False
            
            # Get account info
            self.account_info = mt5.account_info()
            if self.account_info is None:
                logger.error("Failed to get account info")
                return False
            
            self.is_connected = True
            logger.info(f"Connected to account #{self.account_info.login}")
            logger.info(f"Account balance: {self.account_info.balance}")
            logger.info(f"Account equity: {self.account_info.equity}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
    
    def connect(self) -> bool:
        """
        Koneksi lengkap ke MT5 (initialize + login)
        """
        if self.initialize() and self.login():
            return True
        return False
    
    def disconnect(self):
        """
        Tutup koneksi MT5
        """
        try:
            mt5.shutdown()
            self.is_connected = False
            logger.info("MT5 connection closed")
        except Exception as e:
            logger.error(f"Error closing MT5 connection: {e}")
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Mendapatkan informasi symbol
        """
        try:
            if not self.is_connected:
                logger.warning("MT5 not connected")
                return None
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return None
            
            return {
                'symbol': symbol_info.name,
                'bid': symbol_info.bid,
                'ask': symbol_info.ask,
                'spread': symbol_info.spread,
                'digits': symbol_info.digits,
                'point': symbol_info.point,
                'trade_contract_size': symbol_info.trade_contract_size,
                'trade_tick_value': symbol_info.trade_tick_value,
                'trade_tick_size': symbol_info.trade_tick_size,
                'margin_initial': symbol_info.margin_initial
            }
            
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def get_rates(self, symbol: str, timeframe: int, count: int = 100) -> Optional[pd.DataFrame]:
        """
        Mendapatkan data harga historical
        """
        try:
            if not self.is_connected:
                logger.warning("MT5 not connected")
                return None
            
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                logger.error(f"Failed to get rates for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting rates for {symbol}: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Mendapatkan informasi akun
        """
        try:
            if not self.is_connected:
                logger.warning("MT5 not connected")
                return None
            
            account_info = mt5.account_info()
            if account_info is None:
                return None
            
            return {
                'login': account_info.login,
                'trade_mode': account_info.trade_mode,
                'leverage': account_info.leverage,
                'limit_orders': account_info.limit_orders,
                'margin_so_mode': account_info.margin_so_mode,
                'trade_allowed': account_info.trade_allowed,
                'trade_expert': account_info.trade_expert,
                'margin_mode': account_info.margin_mode,
                'currency_digits': account_info.currency_digits,
                'balance': account_info.balance,
                'credit': account_info.credit,
                'profit': account_info.profit,
                'equity': account_info.equity,
                'margin': account_info.margin,
                'margin_free': account_info.margin_free,
                'margin_level': account_info.margin_level,
                'name': account_info.name,
                'server': account_info.server,
                'currency': account_info.currency,
                'company': account_info.company
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def check_connection(self) -> bool:
        """
        Cek status koneksi
        """
        try:
            if not self.is_connected:
                return False
            
            # Test connection dengan mengambil account info
            account_info = mt5.account_info()
            return account_info is not None
            
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False


# Instance global MT5 connection
mt5_connection = MT5Connection()