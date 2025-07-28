#!/usr/bin/env python3
"""
Trading Bot Setup Script
Script untuk memudahkan setup awal trading bot
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 60)
    print("🤖 TRADING BOT - SETUP SCRIPT")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required!")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Upgrade pip first
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ Dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        "trading_bot/logs",
        "trading_bot/data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ Directories created successfully!")

def setup_env_file():
    """Setup environment file"""
    print("\n⚙️ Setting up environment file...")
    
    if os.path.exists(".env"):
        response = input("   .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("   ⏭️ Skipping .env setup")
            return True
    
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("   ✅ .env file created from template")
        print("   📝 Please edit .env file with your configuration!")
        return True
    else:
        print("   ❌ .env.example not found!")
        return False

def check_mt5_installation():
    """Check if MetaTrader 5 might be installed"""
    print("\n🔍 Checking MetaTrader 5...")
    
    # Common MT5 installation paths
    mt5_paths = [
        "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
        "C:\\Program Files (x86)\\MetaTrader 5\\terminal64.exe",
        os.path.expanduser("~/Applications/MetaTrader 5.app"),  # macOS
        "/opt/mt5/terminal64.exe"  # Linux with Wine
    ]
    
    found = False
    for path in mt5_paths:
        if os.path.exists(path):
            print(f"   ✅ Found MT5 at: {path}")
            found = True
            break
    
    if not found:
        print("   ⚠️ MetaTrader 5 not found in common locations")
        print("   📝 Please install MT5 and update MT5_PATH in .env")
    
    return True

def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        print("   Testing imports...")
        import MetaTrader5
        import pandas
        import telegram
        print("   ✅ All imports successful")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False

def print_next_steps():
    """Print next steps for user"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED!")
    print("=" * 60)
    print()
    print("📋 NEXT STEPS:")
    print()
    print("1. 📝 Edit .env file with your configuration:")
    print("   - MT5 login credentials")
    print("   - Telegram bot token")
    print("   - Chat ID")
    print()
    print("2. 🔧 Install and configure MetaTrader 5:")
    print("   - Download from https://www.metatrader5.com/")
    print("   - Enable algorithmic trading")
    print("   - Login to your account")
    print()
    print("3. 🤖 Create Telegram bot:")
    print("   - Chat with @BotFather")
    print("   - Create new bot with /newbot")
    print("   - Get your bot token")
    print()
    print("4. 🧪 Test the setup:")
    print("   python test_mt5_connection.py")
    print()
    print("5. 🚀 Run the bot:")
    print("   python run_bot.py")
    print()
    print("📖 For detailed instructions, see TRADING_BOT_README.md")
    print()

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup .env file
    if not setup_env_file():
        print("\n❌ Setup failed during .env configuration")
        sys.exit(1)
    
    # Check MT5
    check_mt5_installation()
    
    # Run tests
    if not run_tests():
        print("\n⚠️ Some tests failed, but setup can continue")
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)