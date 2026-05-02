
import asyncio
import sys
from pathlib import Path


async def main():
    """Main entry point"""
    print("Kuni: AI Character Bot")
    
    # Check for debug mode
    if len(sys.argv) > 1 and "--debug" in sys.argv:
        print("--debug mode enabled; service is not running")
        return
    
    # Initialize components
    from telegram.TelegramClient import TelegramClient
    from AppBase import AppBase
    
    telegram = TelegramClient()
    
    app = AppBase("data")
    
    # Connect to Telegram login signal
    telegram.on_login.connect(lambda: print("Logged in"))
    
    # Start Telegram client
    await telegram.connect()
    
    if not telegram.is_connected:
        print("Failed to connect to Telegram. Exiting...")
        return
    
    print(f"Connected to Telegram API: {telegram.base_url}")
    
    # Process notifications
    while True:
        if telegram.is_connected:
            notification = await app.pass_notification_to_ai(
                "Processing new message..."
            )
            
            # Process notification through AI
            await app.process_notification(notification)
        
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())