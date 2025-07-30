#!/usr/bin/env python3
"""
BeansCounter:
  art/transform/read_wks_into_pandas_then_sql.py

"""
import argparse
import pandas as pd
# from sqlalchemy import create_engine
import lib.db.sqlalchemy.make_sqlal_engine_n_session as sqlal  # .SqlAlchEngineNSessionMaker
# import lib.db.sq
parser = argparse.ArgumentParser(description="Tranform from worksheet to Sqlite")
parser.add_argument("--wksfilepath", type=str,
                    help="Path to worksheet file")
parser.add_argument("--sqlitepath", type=str, default=None,
                    help="Path to Sqlite file")
parser.add_argument("--tablename", type=str, default="tablename",
                    help="SQL tablename")
args = parser.parse_args()


class WksPandasSqlTransformer:

  default_tablename = 'tablename'

  def __init__(self, wksfilepath, sheetname=None, tablename=None):
    self.wksfilepath = wksfilepath
    self.sheetname = sheetname
    self.tablename = tablename or self.default_tablename
    self.df = None
    self._engine = None
    self._session = None

  def read_worksheet(self):
    try:
      self.df = pd.read_excel(self.wksfilepath, sheet_name=self.sheetname)
      print("DataFrame successfully loaded from Excel:")
      print(self.df.head())
    except FileNotFoundError:
      print(f"Error: Excel file not found at {self.wksfilepath}")
      exit()
    except Exception as e:
      print(f"Error reading Excel file: {e}")
      exit()

  @property
  def engine(self):
    """
    # --- 2. Write the Pandas DataFrame to a SQL database ---
    # Database connection string (replace with your database details)
    # Examples:
    # SQLite: 'sqlite:///your_database.db'
    # PostgreSQL: 'postgresql://user:password@host:port/database'
    # MySQL: 'mysql+mysqlconnector://user:password@host:port/database'
    # SQL Server: 'mssql+pyodbc://user:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server'
    """
    if self._engine is None:
      maker = sqlal.SqlAlchEngineNSessionMaker()
      self._engine = maker.engine
      self._session = maker.session
    return self._engine

  @property
  def session(self):
    if self._session is None:
      _ = self.engine
    return self._session

  def write_to_sql(self):
    """
    """
    try:
      self.df.to_sql(self.tablename, con=self.engine, if_exists='replace', index=False)
      # if_exists options: 'fail', 'replace', 'append'
      # index=False prevents Pandas from writing the DataFrame index as a column in SQL
      print(f"\nDataFrame successfully written to SQL table '{self.tablename}'.")
    except Exception as e:
      print(f"Error writing DataFrame to SQL: {e}")

  def process(self):
    self.read_worksheet()
    self.write_to_sql()


def get_args():
  wksfilepath = args.wksfilepath
  sqlitepath = args.sqlitepath
  return wksfilepath, sqlitepath


def process():
  wksfilepath, sqlitepath = get_args()
  trans = WksPandasSqlTransformer(wksfilepath, sqlitepath)
  trans.process()


if __name__ == '__main__':
  process()
