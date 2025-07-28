#!/usr/bin/env python3
"""
Trading Bot Runner
Menjalankan aplikasi trading bot
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from trading_bot.main import main
import asyncio

if __name__ == "__main__":
    print("🤖 Starting Trading Bot...")
    print("📝 Make sure you have configured your .env file!")
    print("⚡ Press Ctrl+C to stop the bot\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)