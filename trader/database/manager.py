import config
from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy import func
from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Session
from contextlib import contextmanager


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

session = Session(Engine)
test_session = Session(Test_Engine)


@as_declarative()
class BaseWrapper ():

  @declared_attr
  def __tablename__(cls):
    return cls.__name__.lower() + "s"

  __mapper_args__ = {'always_refresh': True}

  id = Column("id", Integer, primary_key=True)
  created_at = Column("created_at", DateTime, default=func.now())

  session = test_session

  def save(self):

    self.session.add(self)
    self._flush()
    return self

  def get(self, value):
    return self.session.query_property().get(value)

  def update(self, **kwargs):
    for attr, value in kwargs.items():
        setattr(self, attr, value)
    return self.save()

  def delete(self):
    self.session.delete(self)
    self._flush()

  def _flush(self):
    try:
        self.session.flush()
    except DatabaseError:
        self.session.rollback()
        raise


def get_order_from_db(id, test=False):
  return get_item_from_db(id, "*", "orders", "id", test=test)


def get_book_from_db(id, test=False):
  return get_item_from_db(id, "*", "books", "id", test=test)


def get_item_from_db(id, columns, table, search_column, test=False):
  statement = "SELECT {} FROM {} WHERE {} = %s".format(
    columns, table, search_column
  )
  if test:
    results = Test_Engine.execute(statement, id)
  else:
    results = Engine.execute(statement, id)
  return results.fetchone()



@contextmanager
def session_scope(test=False):
    """Provide a transactional scope around a series of operations."""
    if test:
      session = test_session
    try:
        yield session
        session.commit()
    except DatabaseError:
        session.rollback()
        raise
    finally:
        session.close()
