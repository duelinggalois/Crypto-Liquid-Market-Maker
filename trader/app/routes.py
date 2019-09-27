from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.exceptions import abort
from werkzeug.urls import url_parse

from trader.app import app, db, operator, test_operator
from trader.app.models.user import User
from trader.app.forms import LoginForm, RegistrationForm, StrategyFormTest, \
  StrategyForm, StartStopDeleteForm
from trader.database.models.trading_terms import TradingTerms


@app.route('/')
@app.route('/index')
def index():
  form = StartStopDeleteForm()
  strategies = TradingTerms.query.all()
  op_info = {
    "operator": {
      "test": False,
      "running": operator.socket_running,
      "strategies": [
        str(s) for s in strategies if s.active and s.api_enum ==
        operator.api_enum
      ]
    },
    "test_operator": {
      "test": True,
      "running": test_operator.socket_running,
      "strategies": [
        str(s) for s in strategies if s.active and s.api_enum ==
        test_operator.api_enum
      ]
    },
    "inactive": [
      str(s) for s in strategies if not s.active
    ],
    "form": form
  }
  return render_template('index.html', title='Trader', op_info=op_info)


@app.route('/operate/<test>', methods=['POST'])
@login_required
def operate(test=None):
  if test is not None:
    form = StartStopDeleteForm()
    if form.validate_on_submit():
      if current_user.admin is not None and current_user.admin:
        # Not sure how to pass bool back

        if test == 'True':
          if form.start.data:
            test_operator.start_socket()
          if form.stop.data:
            test_operator.stop_socket()

        if test == 'False':
          if form.start.data:
            operator.start_socket()
          if form.stop.data:
            operator.stop_socket()

  return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user(username=None):
  user = User.query.filter_by(username=username).first_or_404()
  strategies = TradingTerms.query.filter_by(user_id=user.id).all()
  user_info = {
    "user": user.username,
    "info": [{
      "id": tt.id,
      "strategy": tt,
      "form": StartStopDeleteForm()
    } for tt in strategies]
  }
  return render_template('user.html', user_info=user_info)


@app.route('/strategy/<strategy_id>', methods=['POST', 'GET'])
@login_required
def strategy(strategy_id=None):
  if strategy_id is not None:
    form = StartStopDeleteForm()
    trading_terms = TradingTerms.query.filter_by(id=strategy_id).first_or_404()
    if form.validate_on_submit():
      if current_user.admin is not None and current_user.admin:

        if form.start.data:
          add_strategy_to_operator(trading_terms)

        if form.stop.data:
          remove_strategy_from_operator(trading_terms)

        if form.delete.data:
          if trading_terms.active:
            remove_strategy_from_operator(trading_terms)
          db.session.delete(trading_terms)
          db.session.commit()
          return redirect(url_for('user', username=current_user.username))

        db.session.commit()

      else:
        flash("Can not complete this action with current permissions")
    owner = User.query.filter_by(id=trading_terms.user_id).first()
    # form.id = strategy_id
    info = {
      "owner": owner.username if owner is not None else "none",
      "strategy": trading_terms,
      "form": form
    }
    return render_template("strategy.html", info=info)
  return redirect(url_for('user', username=current_user.username))


@app.route('/new_strategy', methods=['GET', 'POST'])
@login_required
def new_strategy():
  if not current_user.admin:
    return redirect(url_for('index'))
  form = StrategyForm()
  if form.is_submitted():
    if form.validate():
      form.trading_terms.user_id = current_user.id
      db.session.add(form.trading_terms)
      db.session.commit()
      flash("added terms")
      return redirect(url_for('strategy', strategy_id=form.trading_terms.id))
  return render_template('new_strategy.html', title="New Strategy",
                         form=form)


@app.route('/new_test_strategy', methods=['GET', 'POST'])
@login_required
def new_test_strategy():
  if not current_user.admin:
    return redirect(url_for('index'))
  form = StrategyFormTest()
  if form.validate_on_submit():
    form.trading_terms.user_id = current_user.id
    db.session.add(form.trading_terms)
    db.session.commit()
    flash("added terms")
    return redirect(url_for('strategy', strategy_id=form.trading_terms.id))

  return render_template('new_strategy.html', title="New Test Strategy",
                         form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = LoginForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user is None or not user.check_password(form.password.data):
      flash("Invalid username or password")
      return redirect(url_for('login'))
    login_user(user, remember=form.remember_me.data)
    next_page = request.args.get('next')
    if not next_page:
      next_page = url_for('index')
    if url_parse(next_page).netloc != '':
      return abort(400)
    return redirect(next_page)
  return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash("Registered")
    return redirect(url_for('login'))
  return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))


def remove_strategy_from_operator(trading_terms):
  if trading_terms.api_enum == operator.api_enum:
    operator.remove_strategy(trading_terms)
  if trading_terms.api_enum == test_operator.api_enum:
    test_operator.remove_strategy(trading_terms)
  trading_terms.active = False


def add_strategy_to_operator(trading_terms):
  if trading_terms.api_enum == operator.api_enum:
    operator.add_strategy(trading_terms)
  if trading_terms.api_enum == test_operator.api_enum:
    test_operator.add_strategy(trading_terms)
  trading_terms.active = True
