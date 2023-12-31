from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CalculationResult(Base):
    __tablename__ = "calculation_results"

    id = Column(Integer, primary_key=True, index=True)
    expression = Column(String, index=True)
    result = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
