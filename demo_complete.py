#!/usr/bin/env python3
"""
Complete demo script showing Roblox Garden Parser with Telegram integration.
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

from roblox_garden.config.settings import Settings
from roblox_garden.websocket.client import WebSocketClient
from roblox_garden.filters.item_filters import RobloxGardenFilter
from roblox_garden.utils.formatters import MessageFormatter
from roblox_garden.telegram.bot import TelegramBot


async def demo_with_telegram():
    """Demo with real Telegram integration (if configured)."""
    print("🚀 Roblox Garden Parser - Complete Demo")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize settings
    settings = Settings()
    
    # Initialize components
    websocket_client = WebSocketClient(settings)
    filter_instance = RobloxGardenFilter.create_combined_filter()
    formatter = MessageFormatter(settings)
    
    # Check if Telegram is configured
    telegram_configured = (
        settings.telegram_bot_token != "your_bot_token_here" and
        settings.telegram_updates_channel_id != "your_updates_channel_id" and
        settings.telegram_full_channel_id != "your_full_channel_id"
    )
    
    telegram_bot = None
    if telegram_configured:
        print("✅ Telegram bot configuration found")
        telegram_bot = TelegramBot(settings)
        try:
            await telegram_bot.initialize()
            print("✅ Telegram bot initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Telegram bot: {e}")
            telegram_bot = None
    else:
        print("⚠️  Telegram bot not configured - running in demo mode")
        print("   Configure .env file to enable Telegram integration")
    
    print("\n🔄 Fetching current shop data...")
    
    try:
        # Get current shop data
        shop_data = await websocket_client.fetch_shop_data()
        
        if not shop_data:
            print("❌ Failed to fetch shop data")
            return
        
        print(f"✅ Fetched shop data with {len(shop_data.items)} total items")
        
        # Apply filters
        filtered_items = shop_data.get_filtered_items(filter_instance)
        print(f"🔍 Found {len(filtered_items)} Divine+ items after filtering")
        
        if not filtered_items:
            print("   No Divine+ items found in shop")
            return
        
        # Display found items
        print("\n📋 Divine+ Items Found:")
        print("-" * 30)
        
        for item in filtered_items:
            status = "✅ В наличии" if item.in_stock else "❌ Отсутствует"
            print(f"  • {item.name} [{item.rarity}] - {item.quantity} шт. ({status})")
        
        # Format messages
        print("\n📝 Formatting messages...")
        
        # New items message (simulating some items as "new")
        new_items = filtered_items[:2] if len(filtered_items) >= 2 else filtered_items
        new_items_message = formatter.format_new_items_message(new_items)
        
        # Full report message
        full_report_message = formatter.format_full_report_message(
            filtered_items, 
            shop_data.timestamp
        )
        
        print("\n📨 Sample Messages:")
        print("-" * 20)
        print("🔥 NEW ITEMS MESSAGE:")
        print(new_items_message)
        print("\n📊 FULL REPORT MESSAGE:")
        print(full_report_message)
        
        # Send to Telegram if configured
        if telegram_bot:
            print("\n📤 Sending messages to Telegram...")
            
            # Send new items update
            updates_success = await telegram_bot.send_to_updates_channel(new_items_message)
            if updates_success:
                print("✅ New items message sent to updates channel")
            else:
                print("❌ Failed to send new items message")
            
            # Send full report
            full_success = await telegram_bot.send_to_full_channel(full_report_message)
            if full_success:
                print("✅ Full report sent to reports channel") 
            else:
                print("❌ Failed to send full report")
            
            if updates_success and full_success:
                print("\n🎉 All messages sent successfully!")
            else:
                print("\n⚠️  Some messages failed to send")
        else:
            print("\n💡 To enable Telegram integration:")
            print("   1. Copy .env.example to .env")
            print("   2. Set your TELEGRAM_BOT_TOKEN")
            print("   3. Set your channel IDs")
            print("   4. Run the script again")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        
    finally:
        # Cleanup
        await websocket_client.close()
        if telegram_bot:
            await telegram_bot.shutdown()


async def main():
    """Main demo function."""
    await demo_with_telegram()


if __name__ == "__main__":
    asyncio.run(main())
