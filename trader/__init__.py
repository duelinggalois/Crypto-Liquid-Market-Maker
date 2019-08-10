from sqlalchemy import create_engine
from trader.database.manager import _db_connection_string
from sqlalchemy.orm import scoped_session, sessionmaker

Engine = create_engine(_db_connection_string(False))
Test_Engine = create_engine(_db_connection_string(True))

Test_Session_Factory = sessionmaker(bind=Test_Engine)
Session_Factory = sessionmaker(bind=Engine)
Test_Session = scoped_session(Test_Session_Factory)
Session = scoped_session(Session_Factory)
