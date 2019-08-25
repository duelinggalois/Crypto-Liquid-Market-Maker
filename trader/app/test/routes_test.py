import unittest
from decimal import Decimal

from flask import url_for

from trader.app import User, db
from trader.app.test.test_base import BaseFlaskTestCase
from trader.database.models.trading_terms import TradingTerms

USERNAME = 'non_admin_user'
USER_PASSWORD = 'secret'
ADMIN = 'admin_user'
ADMIN_PASSWORD = 'admin_secret'


class RoutesTest(BaseFlaskTestCase):

  def setUp(self):
    super().setUp()
    user = User(username=USERNAME, email="a@b.c")
    user.set_password(USER_PASSWORD)
    db.session.add(user)
    admin = User(username=ADMIN, email="d@e.f")
    admin.set_password("admin_secret")
    admin.admin = True
    tt = TradingTerms()
    tt2 = TradingTerms()
    tt.owner = admin
    tt2.owner = admin
    tt2.active = True
    self.tt = tt
    self.tt2 = tt2
    db.session.add(tt)
    db.session.add(tt2)
    db.session.add(admin)

    db.session.commit()

  def test_user_login(self):
    r = self._user_login(USERNAME, USER_PASSWORD)
    self.assertRedirects(r, url_for('index'))

  def test_index(self):
    with self.client:
      self._user_login(USERNAME, USER_PASSWORD)
      r = self.client.get('/')
      self.assert200(r)
      r = self.client.get('/index')
      self.assert200(r)

#TODO delete or change route to login_required
  @unittest.skip('login not required for index')
  def test_index_reject(self):
    r = self.client.get('/')
    self.assertRedirects(r, url_for('login', next='/'))
    r = self.client.get('/index')
    self.assertRedirects(r, url_for('login', next='/index'))

  def test_login_redirect_user(self):
    with self.client:
      r = self.client.get(url_for('user', username=USERNAME))
      self.assertRedirects(r, url_for('login', next='/user/' + USERNAME))
      redirect_location = r.location
      r = self.client.get(redirect_location)
      self.assert200(r)
      r = self._user_login(USERNAME, USER_PASSWORD, url=redirect_location)
      self.assertRedirects(r, url_for('user', username=USERNAME))

  def test_user(self):
    with self.client:
      self._user_login(USERNAME, USER_PASSWORD)
      r = self.client.get(url_for('user', username=USERNAME))
      self.assert200(r)

  def test_strategy(self):

    with self.client:
      self._user_login(ADMIN, ADMIN_PASSWORD)
      r = self.client.get(url_for('strategy', strategy_id=self.tt.id))
      self.assert200(r)

  def test_new_strategy(self):
    self.new_strategy_tezting('new_strategy')

  def test_new_test_strategy(self):
    self.new_strategy_tezting('new_test_strategy')

  def new_strategy_tezting(self, name):
    with self.client:
      self._user_login(ADMIN, ADMIN_PASSWORD)
      r = self.client.get(url_for(name))
      self.assert200(r)

  def test_new_strategy_post(self):
    self.new_strategy_post_tezting('new_strategy')

  def test_new_test_strategy_post(self):
    self.new_strategy_post_tezting('new_test_strategy')

  def new_strategy_post_tezting(self, name):
    tts = TradingTerms.query.all()
    count = len(tts)
    with self.client:
      self._user_login(ADMIN, ADMIN_PASSWORD)
      r = self.client.post(url_for(name),
                           data={
                             "pair": "BTC-USD",
                             "budget": "10000",
                             "min_size": ".01",
                             "size_change": "0.001",
                             "low_price": "100",
                             "high_price": "50000"
                           })
    self.assertRedirects(r, url_for('strategy', strategy_id=count + 1))
    tts = TradingTerms.query.filter(TradingTerms.id == count + 1).all()
    self.assertEqual(len(tts), 1)
    tt = tts[0]
    self.assertEqual(tt.pair, "BTC-USD")
    self.assertEqual(tt.budget, Decimal("10000"))
    self.assertEqual(tt.min_size, Decimal("0.01"))
    self.assertEqual(tt.size_change, Decimal("0.001"))
    self.assertEqual(tt.low_price, Decimal("100"))
    self.assertEqual(tt.high_price, Decimal("50000"))

  def test_start_post(self):
    with self.client:
      self._user_login(ADMIN, ADMIN_PASSWORD)
      r = self.client.post(url_for('strategy', strategy_id=self.tt.id),
                           data={"start": True})
      self.assert200(r)
      self.assertTrue(self.tt.active)

  def test_stop_post(self):
    with self.client:
      self._user_login(ADMIN, ADMIN_PASSWORD)
      r = self.client.post(url_for('strategy', strategy_id=self.tt2.id),
                           data={'stop': True})
      self.assert200(r)
      self.assertFalse(self.tt2.active)

  def test_delete_post(self):
    with self.client:
      self._user_login(ADMIN, ADMIN_PASSWORD)
      r = self.client.post(url_for('strategy', strategy_id=self.tt.id),
                           data={'delete': True})
      self.assertRedirects(r, url_for('user', username=ADMIN))
      self.assertIsNone(TradingTerms.query.filter(
        TradingTerms.id == self.tt.id).first()
      )

  def test_start_post_reject_anonymous(self):
    r = self.client.post(url_for('strategy', strategy_id=self.tt.id),
                         data={"start": True})
    self.assertRedirects(r, url_for('login', next='/strategy/1'))
    self.assertFalse(self.tt.active)

  def test_stop_post_reject_non_admin(self):
    with self.client:
      self._user_login(USERNAME, USER_PASSWORD)
      r = self.client.post(url_for('strategy', strategy_id=self.tt.id),
                           data={"start": True})
      self.assert200(r)
      self.assertFalse(self.tt.active)

  def _user_login(self, user, password, url=None):
    data ={'username': user, 'password': password}
    if url is not None:
      return self.client.post(url, data=data)
    return self.client.post(url_for('login'), data=data)

