#!/usr/bin/env python3
"""
art/books/packt/mongo/removeDuplicates.py
  Removes duplicates in the bookmeta MongoDB collection

  Originally:
    a) this script came up because records were duplicating
    b) isbn13, if unique, should have avoided that
    c) the uniqueness for isbn13 will be treated, so this script is a kind of 'only-one-run script'

from art.books.packt import BookModel
"""
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError
from collections import defaultdict
from art.books.packt import DEFAULT_LOCAL_MONGO_CONN_URL
from art.books.packt import DEFAULT_MONGO_DBNAME
from art.books.packt import DEFAULT_MONGO_COLLNAME
import logging
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MongoDocDuplicateRemover:

  def __init__(self, mongo_dbname=None, mongo_collname=None):
    self.bk_count = 0
    self.total_before = 0
    self.total_after = 0
    self.total_deleted = 0
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

  def deduplicate_books_by_isbn13(self, keep='first'):
    """
    Remove duplicate books based on isbn13 field.

    Args:
      keep: Which duplicate to keep - 'first', 'last', or custom logic
    """
    logger.info(f"Starting deduplication on {self.mongo_dbname}.{self.mongo_collname}")
    # Get total count before deduplication
    self.total_before = self.mongo_coll.count_documents({})
    logger.info(f"Total documents before deduplication: {self.total_before}")

    # Find all unique ISBN13 values that have duplicates
    pipeline = [
      {"$group": {
        "_id": "$isbn13",
        "count": {"$sum": 1},
        "ids": {"$push": "$_id"}
      }},
      {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(self.mongo_coll.aggregate(pipeline))
    if not duplicates:
      logger.info("No duplicates found!")
      return self.total_deleted
    logger.info(f"Found {len(duplicates)} ISBN13 values with duplicates")
    # Track deletions
    self.total_deleted = 0
    deleted_by_isbn = {}
    for dup in duplicates:
      isbn13 = dup['_id']
      doc_ids = dup['ids']
      _ = dup['count']  # count
      # Decide which ID to keep
      if keep == 'first':
        # Keep the first document (by natural order, or you can sort by another field)
        _ = doc_ids[0]  # to_keep
        to_delete = doc_ids[1:]
      elif keep == 'last':
        _ = doc_ids[-1]  # to_keep
        to_delete = doc_ids[:-1]
      else:
        # Custom logic: e.g., keep the one with most fields populated
        # Fetch all documents for this ISBN
        docs = list(self.mongo_coll.find({"_id": {"$in": doc_ids}}))
        # Sort by number of non-null fields (descending)
        docs.sort(key=lambda x: sum(1 for v in x.values() if v is not None), reverse=True)
        _ = docs[0]['_id']  # to_keep
        to_delete = [doc['_id'] for doc in docs[1:]]
      # Delete duplicates
      if to_delete:
        result = self.mongo_coll.delete_many({"_id": {"$in": to_delete}})
        self.total_deleted += result.deleted_count
        deleted_by_isbn[isbn13] = len(to_delete)
        logger.info(f"ISBN13 '{isbn13}': Kept 1, deleted {len(to_delete)} duplicates")
    # Verify results
    total_after = self.mongo_coll.count_documents({})
    unique_isbn_count = len(self.mongo_coll.distinct("isbn13"))
    logger.info(f"\n=== Deduplication Complete ===")
    logger.info(f"Total documents after: {total_after}")
    logger.info(f"Unique ISBN13 values: {unique_isbn_count}")
    logger.info(f"Total documents deleted: {self.total_deleted}")
    if self.total_before - self.total_deleted == self.total_after:
      logger.info("✅ Deduplication successful!")
    else:
      logger.warning("⚠️ Count mismatch - please verify results")
    return self.total_deleted

  def find_duplicate_isbn13(self):
    """
    Helper function to find and report duplicates without deleting
    client = MongoClient(connection_string)
    db = client[database_name]
    collection = db[collection_name]
    """
    pipeline = [
      {"$group": {
        "_id": "$isbn13",
        "count": {"$sum": 1},
        "sample_ids": {"$push": "$_id"}
      }},
      {"$match": {"count": {"$gt": 1}}},
      {"$sort": {"count": -1}}
    ]
    duplicates = list(self.mongo_coll.aggregate(pipeline))
    if duplicates:
      logger.info(f"Found {len(duplicates)} ISBN13 values with duplicates:")
      for dup in duplicates[:10]:  # Show top 10
        logger.info(f"  ISBN13: {dup['_id']} - appears {dup['count']} times")
      if len(duplicates) > 10:
        logger.info(f"  ... and {len(duplicates) - 10} more")
    else:
      logger.info("No duplicates found!")
    return duplicates

  def process(self):
    # First, review duplicates
    print("Step 1: Finding duplicates...")
    duplicates = self.find_duplicate_isbn13()
    if duplicates:
      print("\nStep 2: Removing duplicates...")
      response = input("Proceed with deduplication? (yes/no): ")
      if response.lower() == 'yes':
        # Choose strategy: 'first', 'last', or 'custom'
        deleted = self.deduplicate_books_by_isbn13(
          keep='first'  # Change to 'last' or 'custom' as needed
        )
        print(f"\nDeleted {deleted} duplicate documents")
    else:
      print("No duplicates to clean up!")
    # self.close_conn()

  def close_conn(self):
    if self.mongo_cli_conn is not None:
      self.mongo_cli_conn.close()

  def __str__(self):
    outstr = f"""
      mongo_cli_conn_url = {self.mongo_cli_conn_url} 
      mongo_dbname = {self.mongo_dbname}
      mongo_collname = {self.mongo_collname}
      self.total_deleted = {self.total_deleted}
      self.total_after = {self.total_after}
      self.total_before = {self.total_before}
    """
    return outstr



def process():
  """
  CONNECTION_STRING = "mongodb://localhost:27017/"  # Update this
  DATABASE_NAME = "your_database"  # Update this
  COLLECTION_NAME = "books"  # Update this
  """
  remover = MongoDocDuplicateRemover()
  remover.process()


if __name__ == "__main__":
  process()
