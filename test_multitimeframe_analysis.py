#!/usr/bin/env python3
"""
Test Multi-Timeframe Analysis
Script untuk testing analisa multi-timeframe dan signal generation
"""

import sys
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from trading_bot.config.settings import settings
from trading_bot.utils.logger import setup_logger
from trading_bot.mt5.connection import mt5_connection
from trading_bot.strategies.technical_analysis import technical_analysis
from trading_bot.strategies.signal_generator import signal_generator


def test_single_timeframe_analysis():
    """
    Test analisa single timeframe
    """
    print("🔧 Testing Single Timeframe Analysis...")
    print("=" * 50)
    
    test_symbol = "EURUSD"
    timeframes = ['M5', 'M15', 'H1', 'H4']
    
    for tf in timeframes:
        print(f"\n📊 Testing {test_symbol} {tf}:")
        
        analysis = technical_analysis.analyze_single_timeframe(test_symbol, tf)
        
        if "error" in analysis:
            print(f"   ❌ Error: {analysis['error']}")
            continue
        
        print(f"   💰 Price: {analysis['price']:.5f}")
        print(f"   📈 EMA20: {analysis['ema20']:.5f}")
        print(f"   📈 EMA50: {analysis['ema50']:.5f}")
        print(f"   📊 RSI: {analysis['rsi']:.2f}")
        print(f"   🎯 Trend: {analysis['trend']}")
        print(f"   🔄 MA Signal: {analysis['ma_signal']}")
        print(f"   ⚡ RSI Signal: {analysis['rsi_signal']}")
        
        if analysis.get('fibonacci'):
            print(f"   📐 Fibonacci available: Yes")
        else:
            print(f"   📐 Fibonacci available: No")


def test_multi_timeframe_analysis():
    """
    Test analisa multi-timeframe
    """
    print("\n\n🔧 Testing Multi-Timeframe Analysis...")
    print("=" * 50)
    
    test_symbols = settings.symbols[:3]  # Test 3 symbols
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}:")
        
        mtf_analysis = technical_analysis.multi_timeframe_analysis(symbol)
        
        if "error" in mtf_analysis:
            print(f"   ❌ Error: {mtf_analysis['error']}")
            continue
        
        signal = mtf_analysis['signal']
        analysis = mtf_analysis['analysis']
        
        print(f"   🎯 Signal Direction: {signal['direction']}")
        print(f"   ⚡ Signal Strength: {signal['strength']}")
        
        if signal['direction'] in ['BUY', 'SELL']:
            print(f"   💰 Entry: {signal['entry']:.5f}")
            print(f"   🛑 Stop Loss: {signal['stop_loss']:.5f}")
            print(f"   🎯 Take Profit: {signal['take_profit']:.5f}")
        
        print(f"   💡 Reasons: {', '.join(signal.get('reason', []))}")
        
        # Show timeframe summary
        print(f"   📊 Timeframe Summary:")
        for tf in ['H4', 'H1', 'M15', 'M5']:
            if tf in analysis and "error" not in analysis[tf]:
                data = analysis[tf]
                print(f"      • {tf}: {data['trend']} | RSI: {data['rsi']:.1f} | MA: {data['ma_signal']}")


def test_signal_generation():
    """
    Test signal generation dan formatting
    """
    print("\n\n🔧 Testing Signal Generation...")
    print("=" * 50)
    
    test_symbol = "EURUSD"
    
    print(f"\n📊 Generating signal for {test_symbol}:")
    
    signal = signal_generator.generate_signal_for_pair(test_symbol)
    
    if signal.get("status") == "ERROR":
        print(f"   ❌ Error: {signal.get('error')}")
        return
    
    print(f"   🎯 Direction: {signal.get('direction', 'NONE')}")
    print(f"   ⚡ Status: {signal.get('status', 'UNKNOWN')}")
    
    if signal.get('direction') in ['BUY', 'SELL']:
        print(f"   💰 Entry: {signal['entry']}")
        print(f"   🛑 Stop Loss: {signal['stop_loss']}")
        print(f"   🎯 Take Profit: {signal['take_profit']}")
        print(f"   📈 R/R Ratio: 1:{signal.get('risk_reward_ratio', 0)}")
        print(f"   ⚡ Strength: {signal.get('strength', 0)}")
    
    # Test message formatting
    print(f"\n📱 Formatted Telegram Message:")
    print("-" * 30)
    message = signal_generator.format_signal_message(signal)
    print(message)


def test_all_pairs_analysis():
    """
    Test analisa untuk semua pair
    """
    print("\n\n🔧 Testing All Pairs Analysis...")
    print("=" * 50)
    
    print(f"📊 Analyzing {len(settings.symbols)} pairs...")
    
    signals = signal_generator.generate_signals_for_all_pairs()
    
    print(f"✅ Generated {len(signals)} signals")
    
    # Count signals by type
    buy_signals = [s for s in signals if s.get('direction') == 'BUY']
    sell_signals = [s for s in signals if s.get('direction') == 'SELL']
    no_signals = [s for s in signals if s.get('direction') == 'NONE']
    error_signals = [s for s in signals if s.get('status') == 'ERROR']
    
    print(f"🟢 BUY Signals: {len(buy_signals)}")
    print(f"🔴 SELL Signals: {len(sell_signals)}")
    print(f"⚪ No Signals: {len(no_signals)}")
    print(f"❌ Errors: {len(error_signals)}")
    
    # Show active signals
    active_signals = buy_signals + sell_signals
    if active_signals:
        print(f"\n🎯 Active Signals:")
        for signal in active_signals:
            rr_ratio = signal.get('risk_reward_ratio', 0)
            print(f"   • {signal['pair']}: {signal['direction']} | Entry: {signal['entry']} | R/R: 1:{rr_ratio}")
    
    # Show errors if any
    if error_signals:
        print(f"\n❌ Errors:")
        for signal in error_signals:
            print(f"   • {signal.get('symbol', 'Unknown')}: {signal.get('error', 'Unknown error')}")


def test_rules_validation():
    """
    Test validasi rules multi-timeframe
    """
    print("\n\n🔧 Testing Rules Validation...")
    print("=" * 50)
    
    test_symbol = "EURUSD"
    
    # Get analysis data
    mtf_analysis = technical_analysis.multi_timeframe_analysis(test_symbol)
    
    if "error" in mtf_analysis:
        print(f"❌ Cannot test rules validation: {mtf_analysis['error']}")
        return
    
    analysis_data = mtf_analysis['analysis']
    
    # Test rules validation
    is_valid = signal_generator.validate_signal_rules(analysis_data)
    
    print(f"📊 Rules Validation for {test_symbol}:")
    print(f"   ✅ Valid Signal: {is_valid}")
    
    # Show rule details
    print(f"\n📋 Rule Details:")
    
    # M5 MA Rule
    if 'M5' in analysis_data and "error" not in analysis_data['M5']:
        ma_signal = analysis_data['M5']['ma_signal']
        print(f"   • M5 MA Signal: {ma_signal} {'✅' if ma_signal in ['BUY', 'SELL'] else '❌'}")
    else:
        print(f"   • M5 MA Signal: ❌ No data")
    
    # M15 RSI Rule
    if 'M15' in analysis_data and "error" not in analysis_data['M15']:
        rsi_signal = analysis_data['M15']['rsi_signal']
        rsi_value = analysis_data['M15']['rsi']
        print(f"   • M15 RSI: {rsi_value:.1f} ({rsi_signal}) {'✅' if rsi_signal != 'NEUTRAL' else '❌'}")
    else:
        print(f"   • M15 RSI: ❌ No data")
    
    # H1 Trend Rule
    if 'H1' in analysis_data and "error" not in analysis_data['H1']:
        trend = analysis_data['H1']['trend']
        print(f"   • H1 Trend: {trend} {'✅' if trend in ['BULLISH', 'BEARISH'] else '❌'}")
    else:
        print(f"   • H1 Trend: ❌ No data")
    
    # H4 Structure Rule
    if 'H4' in analysis_data and "error" not in analysis_data['H4']:
        trend = analysis_data['H4']['trend']
        print(f"   • H4 Structure: {trend} {'✅' if trend != 'UNKNOWN' else '❌'}")
    else:
        print(f"   • H4 Structure: ❌ No data")


def main():
    """
    Main test function
    """
    print("🚀 Multi-Timeframe Analysis Test Suite")
    print("=" * 60)
    
    try:
        # Setup logger
        setup_logger()
        
        # Connect to MT5
        print("🔌 Connecting to MetaTrader 5...")
        if not mt5_connection.connect():
            print("❌ Failed to connect to MT5. Please check your configuration.")
            return False
        
        print("✅ Connected to MT5 successfully!")
        print(f"📊 Testing with {len(settings.symbols)} configured pairs")
        
        # Run tests
        test_single_timeframe_analysis()
        test_multi_timeframe_analysis()
        test_signal_generation()
        test_all_pairs_analysis()
        test_rules_validation()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Disconnect MT5
        if mt5_connection.is_connected:
            mt5_connection.disconnect()
            print("🔌 Disconnected from MT5")


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Multi-timeframe analysis is working correctly!")
    else:
        print("\n❌ Multi-timeframe analysis test failed!")
        sys.exit(1)