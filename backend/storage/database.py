from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///data/db/cryptoscope.db"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)


def init_db():
    """
    Создаёт все таблицы в БД, если они ещё не существуют.
    Вызывается один раз при старте приложения.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session