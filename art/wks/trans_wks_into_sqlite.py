#!/usr/bin/env python3
"""
BeansCounter:
  art/wks/trans_wks_into_sqlite.py

This module contains functionality to introspect a worksheet file
  and load its data to a Sqlite table

The main class in this module is WksToSqliteTransformer.
  Its process-chain, with a pandas df, is the following:
      # 1 read the working into a pandas's dataframe
      self.df = read_spreadsheet(self.wksfilepath)
      # 2 infer the "main" table bounds
      self.df = infer_table_bounds(self.df)
      if self.df.empty:
        errmsg = "Spreadsheet appears empty or unreadable."
        raise ValueError(errmsg)
      # 3 take care of fieldnames using the main table's column names
      self.normalize_colnames_to_fieldnames()
      # 4 write the result transformed table to a Sqlite file
      self.write_to_sqlite()
"""
import argparse
import pandas as pd
import sqlite3
import os
import re
import settings as sett
from pathlib import Path
parser = argparse.ArgumentParser(description="Tranform from worksheet to Sqlite")
parser.add_argument("--wksfp", type=str,
                    help="Filepath to worksheet file")
parser.add_argument("--sqlfp", type=str, default=None,
                    help="Filepath to Sqlite file")
parser.add_argument("--tablename", type=str, default="tablename",
                    help="SQL tablename")
args = parser.parse_args()


class WksToSqliteTransformer:

  default_tablename = 'goods_prices'

  def __init__(
      self,
      wksfilepath=None,
      sqlitepath=None,
      tablename=None,
    ):
    self.fieldname = None
    self.colname = None
    self.tablename = tablename
    self.df = None
    self.wksfilepath, self.sqlitepath = wksfilepath, sqlitepath
    self.treat_attrs()

  def treat_attrs(self):
    if self.tablename is None:
      self.tablename = self.default_tablename
    if self.wksfilepath is None or not os.path.isfile(self.wksfilepath):
      self.wksfilepath = os.path.join(sett.APP_ROOTFOLDER, 'example.xlsx')
      if not os.path.isfile(self.wksfilepath):
        errmsg = 'Worksheet file does not exist. Please, reenter it and retry.'
        raise OSError(errmsg)
    if self.sqlitepath is None or not os.path.isfile(self.wksfilepath):
      self.sqlitepath = sett.get_app_sqlite_filepath()
      # if not os.path.isfile(self.sqlitepath):
      #   errmsg = 'Worksheet file does not exist. Please, reenter it and retry.'
      #   raise OSError(errmsg)

  def normalize_colnames_to_fieldnames(self):
    self.fieldname = normalize_colnames_to_fieldnames(self.colname)
    # Convert datetime columns to string format
    for col in self.df.select_dtypes(include=['datetime.date']).columns:
      self.df[col] = self.df[col].dt.strftime('%Y-%m-%d')
    for col in self.df.select_dtypes(include=['datetime', 'datetime64[ns]']).columns:
      self.df[col] = self.df[col].dt.strftime('%Y-%m-%d %H:%M:%S')

  def infer_table_bounds(self):
    infer_table_bounds(self.df)

  def read_spreadsheet(self):
    read_spreadsheet(self)

  def write_to_sqlite(self):
    try:
      write_to_sqlite(
        df=self.df,
        db_path=self.sqlitepath,
        table_name=self.tablename
      )
      print(f"✅ Data loaded into '{self.sqlitepath}' successfully.")
    except Exception as e:
      errmsg = f"⚠️ Error writing to Sqlite: {e}"
      print(errmsg)

  def process(self):
    try:
      self.df = read_spreadsheet(self.wksfilepath)
      self.df = infer_table_bounds(self.df)
      if self.df.empty:
        errmsg = "Spreadsheet appears empty or unreadable."
        raise ValueError(errmsg)
      self.normalize_colnames_to_fieldnames()
      self.write_to_sqlite()
    except Exception as e:
      errmsg = f"⚠️ Error in the tranform process from worksheet to dbtable: {e}"
      print(errmsg)


def normalize_colnames_to_fieldnames(name):
    """Normalize column names to valid SQLite field names."""
    name = str(name).strip().lower()
    name = re.sub(r'\W+', '_', name)
    if not name or not name[0].isalpha():
      name = 'col_' + name
    return name


def read_spreadsheet(filepath):
    """Reads supported spreadsheet types into a DataFrame."""
    ext = Path(filepath).suffix.lower()
    if ext == '.csv':
      return pd.read_csv(filepath, skip_blank_lines=True)
    elif ext == '.xlsx':
      return pd.read_excel(filepath, engine='openpyxl')
    elif ext == '.ods':
      return pd.read_excel(filepath, engine='odf')
    else:
      raise ValueError(f"Unsupported worksheet file extension: {ext}")


def infer_table_bounds(df):
    """Drop completely empty rows and columns."""
    df.dropna(axis=0, how='all', inplace=True)
    df.dropna(axis=1, how='all', inplace=True)
    return df


def write_to_sqlite(df, db_path, table_name='imported_table'):
    """Writes DataFrame into SQLite database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
    conn = sqlite3.connect(db_path)
    # Normalize column names
    original_columns = list(df.columns)
    normalized_columns = [normalize_colnames_to_fieldnames(col) for col in original_columns]
    if len(set(normalized_columns)) != len(normalized_columns):
      raise ValueError("Normalized column names are not unique.")
    df.columns = normalized_columns
    try:
      df.to_sql(table_name, conn, if_exists='replace', index=False)
    except Exception as e:
      raise RuntimeError(f"Failed to write to SQLite: {e}")
    finally:
      conn.close()


def get_args():
  wksfilepath = args.wksfp
  sqlitepath = args.sqlfp
  return wksfilepath, sqlitepath


def process():
  wksfilepath, sqlitepath = get_args()
  scrmsg = f"""Arguments:
  wksfilepath = [{wksfilepath}]
  sqlitepath = [{sqlitepath}]
  """
  print(scrmsg)
  transformer = WksToSqliteTransformer(
    wksfilepath=wksfilepath,
    sqlitepath=sqlitepath
  )
  transformer.process()


if __name__ == '__main__':
    process()
