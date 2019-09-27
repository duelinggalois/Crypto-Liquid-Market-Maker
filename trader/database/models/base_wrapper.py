from sqlalchemy import Column, Integer, DateTime, func, TIMESTAMP
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class BaseWrapper:

  @declared_attr
  def __tablename__(cls):
    """Convert CamelCase to snake_case and make plural"""
    name = "".join(
      char if char.lower() == char else "_" + char.lower()
      for char in  cls.__name__
    )[1:]
    if name[-1] == "s":
      return name
    else:
      return name + "s"

  __mapper_args__ = {'always_refresh': True}

  id = Column("id", Integer, primary_key=True)
  created_at = Column("created_at", DateTime, default=func.now())
  updated_at = Column(TIMESTAMP, nullable=False)
