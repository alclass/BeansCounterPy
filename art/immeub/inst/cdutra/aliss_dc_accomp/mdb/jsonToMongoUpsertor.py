#!/usr/bin/env python3
"""
art/bookroutes/packt/mongo/upsertors/jsonToMongoUpsertor.py
  Explanation?
    (...)

Key Points:
    MongoDB runs on mongodb://localhost:27017 by default
    Use insert_many() for multiple documents, insert_one() for single
    MongoDB automatically adds _id if not present
    For large files, use the streaming method to avoid memory issues
    Use upsert=True with update_one() to avoid duplicates

import JSON
import ijson
import types
from pathlib import Path
"""
import datetime
from pymongo import MongoClient
from art.bks.packt import DEFAULT_LOCAL_MONGO_CONN_URL
from art.bks.packt import DEFAULT_MONGO_DBNAME
from art.bks.packt import DEFAULT_MONGO_COLLNAME
import lib.datesetc.stringify_datetimes as strtdelta


class MongoUpsertor:

  def __init__(self, mongo_dbname=None, mongo_collname=None) -> None:
    self.start_time = datetime.datetime.now()
    self.end_time = None
    self.mongo_dbname = mongo_dbname or DEFAULT_MONGO_DBNAME
    self.mongo_collname = mongo_collname or DEFAULT_MONGO_COLLNAME
    self.mongo_cli_conn_url = None
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.coll_count = 0
    self.n_upserted = 0
    self.id_field = '_id'
    self.open_conn()

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.coll_count = self.mongo_coll.count_documents({})
    print(f"Total documents in collection: {self.coll_count}")

  def update(self, query_filter, updt_ops_set_data, json_record):
    """
    print(f"\tMatched documents: {result.matched_count}")
    print(f"\tModified documents: {result.modified_count}")
    """
    scrmsg = f"@upsert() {self.mongo_dbname}/{self.mongo_collname}"
    scrmsg += f"\n\t{json_record}"
    print(scrmsg)
    result = self.mongo_coll.update_one(
      query_filter,
      updt_ops_set_data,
      upsert=True,
    )
    self.n_upserted += result.modified_count
    scrmsg += f"\n\t\tmodified={result.modified_count} | n_upserted={self.n_upserted}"
    print(scrmsg)

  @property
  def duration(self):
    if self.end_time is None:
      self.end_time = datetime.datetime.now()
    if self.start_time is not None:
      try:
        _duration = self.end_time - self.start_time
        duration_str = strtdelta.stringify_timedelta(_duration)
        return duration_str
      except (AttributeError, TypeError):
        pass
    return None

  def process(self):
    pass

  def close_conn(self):
    self.end_time = datetime.datetime.now()
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()

  def __str__(self):
    duration = self.duration or 'n/a'
    outstr = f"""
      mongo_cli_conn_url = {self.mongo_cli_conn_url} 
      mongo_dbname = {self.mongo_dbname}
      mongo_collname = {self.mongo_collname}
      duration = {duration} | {self.end_time} | {self.start_time}
      coll_count = {self.coll_count}
      n_upserted = {self.n_upserted}
    """
    return outstr


# Usage examples
if __name__ == "__main__":
  # Simple usage
  pass
