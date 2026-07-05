import asyncio
import os
from telethon import TelegramClient

api_id = os.environ.get('TELEGRAM_API_ID')
api_hash = os.environ.get('TELEGRAM_API_HASH')

if not api_id or not api_hash:
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ[k.strip()] = v.strip()
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')

async def main():
    client = TelegramClient('telegram_session', int(api_id), api_hash)
    await client.start()
    
    print("Available Dialogs/Groups:")
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(f"ID: {dialog.id} | Name: {dialog.name}")

if __name__ == '__main__':
    asyncio.run(main())
