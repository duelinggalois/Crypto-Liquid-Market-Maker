from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import config
# TODO Combine manager and db into one file
from trader.database.manager import BaseWrapper

Base = declarative_base()


class DataAccessLayer:
  def __init__(self):
      self.engine = None
      self.conn_string = None

  def connect(self, test=True):
    if not self.conn_string:
      self.set_connection_string(test)
    self.engine = create_engine(self.conn_string, echo_pool=True,
                                pool_pre_ping=True)
    BaseWrapper.metadata.create_all(self.engine)
    self.Session_Factory = sessionmaker(bind=self.engine)
    self.Session = scoped_session(self.Session_Factory)

  def set_connection_string(self, test=True):
    self.conn_string = _db_connection_string(test)

dal = DataAccessLayer()


def _db_connection_string(test):
  db_name = config.db['test_name'] if test else config.db['name']
  return 'mysql+pymysql://{}:{}@{}/{}'.format(
    config.db['user'],
    config.db['password'],
    config.db['host'],
    db_name
  )
