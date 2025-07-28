#!/usr/bin/env python3
"""
Test MetaTrader 5 Connection
Script untuk testing koneksi ke MT5
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from trading_bot.mt5.connection import mt5_connection
from trading_bot.config.settings import settings
from trading_bot.utils.logger import setup_logger

def test_mt5_connection():
    """
    Test koneksi ke MetaTrader 5
    """
    print("🔧 Testing MetaTrader 5 Connection...")
    print("=" * 50)
    
    try:
        # Setup logger
        setup_logger()
        
        # Print configuration
        print(f"📋 Configuration:")
        print(f"   Login: {settings.mt5_login}")
        print(f"   Server: {settings.mt5_server}")
        print(f"   Path: {settings.mt5_path}")
        print()
        
        # Test connection
        print("🔌 Attempting to connect...")
        if mt5_connection.connect():
            print("✅ Connection successful!")
            
            # Get account info
            account_info = mt5_connection.get_account_info()
            if account_info:
                print(f"\n💰 Account Information:")
                print(f"   Login: {account_info['login']}")
                print(f"   Name: {account_info['name']}")
                print(f"   Server: {account_info['server']}")
                print(f"   Company: {account_info['company']}")
                print(f"   Currency: {account_info['currency']}")
                print(f"   Balance: ${account_info['balance']:,.2f}")
                print(f"   Equity: ${account_info['equity']:,.2f}")
                print(f"   Leverage: 1:{account_info['leverage']}")
            
            # Test symbol info
            print(f"\n📊 Testing Symbol Information:")
            for symbol in settings.symbols[:3]:
                symbol_info = mt5_connection.get_symbol_info(symbol)
                if symbol_info:
                    print(f"   {symbol}: Bid={symbol_info['bid']:.5f}, Ask={symbol_info['ask']:.5f}")
                else:
                    print(f"   {symbol}: ❌ Not available")
            
            # Disconnect
            mt5_connection.disconnect()
            print(f"\n🔌 Disconnected successfully")
            
        else:
            print("❌ Connection failed!")
            print("Please check:")
            print("1. MetaTrader 5 is installed and running")
            print("2. Login credentials are correct")
            print("3. Server name is correct")
            print("4. Account has trading permissions")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_mt5_connection()
    if success:
        print("\n🎉 MT5 connection test completed successfully!")
    else:
        print("\n💥 MT5 connection test failed!")
        sys.exit(1)