#!/usr/bin/env python3
"""
BeansCounter:
  lib/db/sqlalchemy/make_sqlal_engine_n_session.py

"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings as sett


class SqlAlchEngineNSessionMaker:

  def __init__(self, sqlitepath=None):
    self.sqlitepath = sqlitepath
    if self.sqlitepath is None:
      self.sqlitepath = sett.get_app_sqlite_filepath()
    self._engine = None
    self._session = None

  @property
  def engine(self):
    if self._engine is None:
      db_conn_str = f"sqlite://{self.sqlitepath}"
      self._engine = create_engine(db_conn_str)
    return self._engine

  def make_session(self):
    sessionmolder = sessionmaker(bind=self.engine)
    session = sessionmolder()
    return session

  @property
  def session(self):
    if self._session is None:
      self._session = self.make_session()
    return self._session

  def __str__(self):
    outstr = f"""{self.__class__.__name__}
    sqlitepath = {self.sqlitepath}
    engine = {self.engine}
    session = {self.session}
    """
    return outstr


def process():
  maker = SqlAlchEngineNSessionMaker()
  print(maker)


if __name__ == '__main__':
  process()
