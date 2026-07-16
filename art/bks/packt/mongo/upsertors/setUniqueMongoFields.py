#!/usr/bin/env python3
"""
art/bookroutes/packt/mongo/upsertors/setUniqueMongoFields.py
  Removes duplicates in the bookmeta MongoDB collection

  Originally:
    a) this script came up because records were duplicating
    b) isbn13, if unique, should have avoided that
    c) the uniqueness for isbn13 will be treated, so this script is a kind of 'only-one-run script'

from art.bookroutes.packt import BookModel
from pymongo.errors import DuplicateKeyError
"""
from pymongo import MongoClient, ASCENDING
from art.bks.packt import DEFAULT_LOCAL_MONGO_CONN_URL
from art.bks.packt import DEFAULT_MONGO_DBNAME
from art.bks.packt import DEFAULT_MONGO_COLLNAME
import logging
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class UniqueFieldSetter:

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.bk_count = 0
    self.mongo_count = 0
    self.books = []
    self.mongo_dbname = mongo_dbname or DEFAULT_MONGO_DBNAME
    self.mongo_collname = mongo_collname or DEFAULT_MONGO_COLLNAME
    self.mongo_cli_conn_url = None
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.open_conn()

  def open_conn(self):
    self.mongo_cli_conn = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
    self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
    self.mongo_coll = self.mongo_db[self.mongo_collname]
    # Count documents
    self.mongo_count = self.mongo_coll.count_documents({})
    print(f"Total documents in collection: {self.mongo_count}")

  def create_unique_isbn_index(self):
    """Create a unique index on the isbn13 field"""
    try:
      # Create unique index
      result = self.mongo_coll.create_index(
        [("isbn13", ASCENDING)],
        unique=True,
        name="unique_isbn13_idx",
        background=True  # Creates index in background without blocking
      )
      logger.info(f"✅ Created unique index: {result}")
    except Exception as e:
      logger.error(f"Failed to create unique index: {e}")
      logger.info("Make sure no duplicates exist before creating unique index!")
    finally:
      pass  # client.close()

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()

  def process(self):
    # First, review duplicates
    print("Step 1: create_unique_isbn_index...")
    self.create_unique_isbn_index()
    print("Step 2: closing mongodb connection")
    self.close_conn()


  def __str__(self):
    outstr = f"""
      mongo_cli_conn_url = {self.mongo_cli_conn_url} 
      mongo_dbname = {self.mongo_dbname}
      mongo_collname = {self.mongo_collname}
    """
    return outstr


def process():
  """
  CONNECTION_STRING = "mongodb://localhost:27017/"  # Update this
  DATABASE_NAME = "your_database"  # Update this
  COLLECTION_NAME = "bookroutes"  # Update this
  """
  uniq_setter = UniqueFieldSetter()
  uniq_setter.process()


if __name__ == "__main__":
  process()
