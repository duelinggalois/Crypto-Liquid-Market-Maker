import config
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy import func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker


def _db_connection_string(test):
  db_name = config.db['test_name'] if test else config.db['name']
  return 'mysql+pymysql://{}:{}@{}/{}'.format(
    config.db['user'],
    config.db['password'],
    config.db['host'],
    db_name
  )


Engine = create_engine(_db_connection_string(False))
Test_Engine = create_engine(_db_connection_string(True))

test_session_factory = sessionmaker(bind=Test_Engine)
session_factory = sessionmaker(bind=Engine)
Test_Session = scoped_session(test_session_factory)
Session = scoped_session(session_factory)


@as_declarative()
class BaseWrapper:

  @declared_attr
  def __tablename__(cls):
    return cls.__name__.lower() + "s"

  __mapper_args__ = {'always_refresh': True}

  id = Column("id", Integer, primary_key=True)
  created_at = Column("created_at", DateTime, default=func.now())

  session = Test_Session()
