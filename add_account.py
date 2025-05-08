import asyncio
from db.database import async_session
from db.models import Account

async def add_account(login, password, appium_url):
    async with async_session() as session:
        acc = Account(login=login, password=password, appium_url=appium_url)
        session.add(acc)
        await session.commit()
        print(f"✅ Аккаунт {login} добавлен с Appium {appium_url}")

if __name__ == "__main__":
    asyncio.run(add_account(
        login="test1",
        password="pass",
        appium_url="http://appium1:4723"
    ))
