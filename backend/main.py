import asyncio
from pathlib import Path
from dotenv import load_dotenv
from backend.app.application import App


if __name__ == "__main__":
    load_dotenv(Path(__file__).resolve().parent / ".env")

    asyncio.run(App().start())