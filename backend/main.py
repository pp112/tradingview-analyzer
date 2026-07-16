import asyncio
from backend.app.application import App

if __name__ == "__main__":
    asyncio.run(App().start())