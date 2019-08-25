from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import AppConfig, test_socket, socket_url
from trader.database.models.base_wrapper import BaseWrapper
from trader.exchange.api_enum import ApiEnum
from trader.operations.operator import Operator

app = Flask(__name__)
app.config.from_object(AppConfig)
db = SQLAlchemy(app, model_class=BaseWrapper)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
# Trading operators
operator = Operator(url=socket_url)
test_operator = Operator(url=test_socket, api_enum=ApiEnum.CoinbaseProTest)

from trader.app import routes
# Load metadata tables into app
from trader.app.models.user import User
from trader.database.models.book import Book
from trader.database.models.order import Order
from trader.database.models.trading_terms import TradingTerms

