# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка подключения к базе данных
DATABASE_URL = "sqlite:///gym_bot.db"  # Используем SQLite
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создание сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Модель клиента
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, index=True)  # Убираем unique=True
    first_name = Column(String)
    last_name = Column(String)
    subscription_type = Column(String)
    balance = Column(Float)
    is_wholesale = Column(Boolean)

# Создание таблиц в базе данных
def init_db():
    Base.metadata.create_all(bind=engine)

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()