from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///comparisons.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Comparison(Base):
    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    url1 = Column(String, nullable=False)
    subject_title1 = Column(String, nullable=False)
    guide_url = Column(String, nullable=True)
    url2 = Column(String, nullable=False)
    subject_title2 = Column(String, nullable=True)
    similarity_score = Column(Float, nullable=True)
    components = Column(JSON, nullable=True)
    analysis = Column(JSON, nullable=True)
    explanation = Column(String, nullable=True)
    comparison_type = Column(String, nullable=False)
    detalles_origen = Column(JSON, nullable=True)
    detalles_comparada = Column(JSON, nullable=True)
    theme_similarity = Column(Float, nullable=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()