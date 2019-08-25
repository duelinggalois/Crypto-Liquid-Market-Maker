from flask_testing import TestCase
from testing import mysqld

from config import BaseConfiguration
from trader.app import app, db


class BaseFlaskTestCase(TestCase):

  def create_app(self):
    app.config.from_object(self.base_config)
    return app

  @classmethod
  def setUpClass(cls):
    cls.MYSQLD_FACTORY = mysqld.MysqldFactory(cache_initialize_db=True,
                                              port=7531)

    cls.mem_db = cls.MYSQLD_FACTORY()
    cls.mem_db.start()
    cls.base_config = BaseConfiguration()
    cls.base_config.TESTING = True
    cls.base_config.WTF_CSRF_ENABLED = False
    cls.base_config.SQLALCHEMY_DATABASE_URI = cls.mem_db.url()

  def setUp(self):
    db.create_all()

  def tearDown(self):
    db.session.remove()
    db.drop_all()

  @classmethod
  def tearDownClass(cls):
    cls.mem_db.stop()
    cls.MYSQLD_FACTORY.clear_cache()
