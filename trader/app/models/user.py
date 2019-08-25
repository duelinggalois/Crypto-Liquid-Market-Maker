from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from trader.app import db, login
from trader.database.models.base_wrapper import BaseWrapper


class User(UserMixin, BaseWrapper):
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  admin = db.Column(db.Boolean())
  terms = db.relationship('TradingTerms', backref='owner', lazy="dynamic")

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
  return User.query.get(int(id))
