from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
  SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from trader.app.models.user import User
from trader.exchange.api_enum import ApiEnum
from trader.database.models.trading_terms import TradingTerms


class LoginForm(FlaskForm):
  username = StringField("Username", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  remember_me = BooleanField("Remember Me")
  submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
  username = StringField("Username", validators=[DataRequired()])
  email = StringField("Email", validators=[DataRequired(), Email()])
  password = PasswordField("Password", validators=[DataRequired()])
  password2 = PasswordField("Repeat Password", validators=[DataRequired(),
                                                           EqualTo('password')])
  submit = SubmitField("Register")

  def validate_username(self, username):
    user = User.query.filter_by(username=username.data).first()
    if user is not None:
      raise ValidationError("Please use a different username")

  def validate_email(self, email):
    user = User.query.filter_by(email=email.data).first()
    if user is not None:
      raise ValidationError("Please use a different email")


class StrategyFormBase(FlaskForm):

  def validate_pair(self, pair):
    try:
      self.trading_terms.pair = pair.data
    except ValueError as e:
      raise ValidationError(e.args[0])

  def validate_budget(self, budget):
    try:
      self.trading_terms.budget = budget.data
    except ValueError as e:
      raise ValidationError(e.args[0])

  def validate_min_size(self, min_size):
    try:
     self.trading_terms.min_size = min_size.data
    except ValueError as e:
      raise ValidationError(e.args[0])

  def validate_size_change(self, size_change):
    try:
      self.trading_terms.size_change = size_change.data
    except ValueError as e:
      raise ValidationError(e.args[0])

  def validate_low_price(self, low_price):
    try:
      self.trading_terms.low_price = low_price.data
    except ValueError as e:
      raise ValidationError(e.args[0])

  def validate_high_price(self, high_price):
    try:
      self.trading_terms.high_price = high_price.data
    except ValueError as e:
      raise ValidationError(e.args[0])


class StrategyForm(StrategyFormBase, FlaskForm):
  trading_terms = TradingTerms(api_enum=ApiEnum.CoinbasePro)
  pair = SelectField(
    "Pair", [],
    choices=[(a, a) for a in trading_terms.supported_pairs]
  )
  budget = StringField("Budget", validators=[DataRequired()])
  min_size = StringField("Minimum trade size", validators=[DataRequired()])
  size_change = StringField("Trade size increase", validators=[DataRequired()])
  low_price = StringField("Lowest trade price", validators=[DataRequired()])
  high_price = StringField("Highest trade price", validators=[DataRequired()])

  submit = SubmitField("Create")


class StrategyFormTest(StrategyFormBase):
  trading_terms = TradingTerms(api_enum=ApiEnum.CoinbaseProTest)
  pair = SelectField(
    "Pair", [],
    choices=[(a, a) for a in trading_terms.supported_pairs]
  )
  budget = StringField("Budget", validators=[DataRequired()])
  min_size = StringField("Minimum trade size", validators=[DataRequired()])
  size_change = StringField("Trade size increase", validators=[DataRequired()])
  low_price = StringField("Lowest trade price", validators=[DataRequired()])
  high_price = StringField("Highest trade price", validators=[DataRequired()])

  submit = SubmitField("Create")


class StartStopDeleteForm(FlaskForm):
  start = SubmitField("Start")
  stop = SubmitField("Stop")
  delete = SubmitField("Delete")
