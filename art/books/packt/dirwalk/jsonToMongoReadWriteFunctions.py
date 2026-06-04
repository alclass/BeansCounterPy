#!/usr/bin/env python3
"""
art/books/packt/dirwalk/jsonToMongoReadWriteFunctions.py
  Explanation?
    (...)

Key Points:
    MongoDB runs on mongodb://localhost:27017 by default
    Use insert_many() for multiple documents, insert_one() for single
    MongoDB automatically adds _id if not present
    For large files, use the streaming method to avoid memory issues
    Use upsert=True with update_one() to avoid duplicates

"""
import json
import ijson
from pathlib import Path
from pymongo import MongoClient


# Method 1: Insert entire JSON file into MongoDB
def json_to_mongodb_simple(
    json_file_path,
    database_name,
    collection_name
):
  # Connect to MongoDB (default: localhost:27017)
  client = MongoClient('mongodb://localhost:27017/')

  # Select database and collection
  db = client[database_name]
  collection = db[collection_name]

  # Read JSON file
  with open(json_file_path, 'r') as file:
    data = json.load(file)

  # Insert data
  if isinstance(data, list):
    # If JSON contains an array of documents
    result = collection.insert_many(data)
    print(f"Inserted {len(result.inserted_ids)} documents")
  else:
    # If JSON contains a single document
    result = collection.insert_one(data)
    print(f"Inserted document with ID: {result.inserted_id}")

  # Close connection
  client.close()


def verify_jsonfile_exists(json_file_path):
  errmsg = f"Json file {json_file_path} does not exist"
  if json_file_path is None:
    raise OSError(errmsg)
  try:
    json_file_path = Path(json_file_path)
  except TypeError:
    raise OSError(errmsg)
  if not json_file_path.is_file():
    raise OSError(errmsg)


# Method 2: More robust with error handling and upsert options
def json_to_mongodb_advanced(
    json_file_path,
    db_name,
    coll_name,
    replace_existing=False,
    id_field='_id'
):
  # no return needed, if json does not exist, raise OSError
  verify_jsonfile_exists(json_file_path)
  client = None
  try:
    # Connect to MongoDB
    scrmsg = f"Opening mongoDB connection: {db_name}/{coll_name}"
    print(scrmsg)
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[coll_name]
    # Read JSON file
    with open(json_file_path, 'r') as file:
      data = json.load(file)
    # Convert single document to list for uniform processing
    if not isinstance(data, list):
      data = [data]
    if replace_existing:
      # Clear existing collection
      collection.drop()
    # Insert documents
    for document in data:
      # Use specified field as _id if available
      if id_field in document and id_field != '_id':
        document['_id'] = document.pop(id_field)
      # Upsert: update if exists, insert if not
      if '_id' in document:
        collection.update_one(
          {'_id': document['_id']},
          {'$set': document},
          upsert=True
        )
      else:
        collection.insert_one(document)
    print(f"Successfully processed {len(data)} documents")

  except Exception as e:
    print(f"Error: {e}")
  finally:
    if client is not None:
      client.close()


# Method 3: For large files using streaming
def json_to_mongodb_streaming(
    json_file_path,
    database_name,
    collection_name,
    batch_size=100
):
  client = MongoClient('mongodb://localhost:27017/')
  db = client[database_name]
  collection = db[collection_name]
  batch = []
  count = 0
  with open(json_file_path, 'rb') as file:
    # Parse array items one by one
    parser = ijson.items(file, 'item')

    for item in parser:
      batch.append(item)
      count += 1

      # Insert in batches
      if len(batch) >= batch_size:
        collection.insert_many(batch)
        print(f"Inserted {count} documents so far...")
        batch = []

    # Insert remaining documents
    if batch:
      collection.insert_many(batch)
      print(f"Total inserted: {count} documents")
  client.close()


def main():
  json_to_mongodb_simple('data.json', 'my_database', 'my_collection')

  # Advanced usage with options
  json_to_mongodb_advanced(
    'data.json',
    'my_database',
    'my_collection',
    replace_existing=True,
    id_field='id'  # Use 'id' field from JSON as MongoDB _id
  )

  # For large files (requires: pip install ijson)
  # JSON_to_mongodb_streaming('large_data.json', 'my_database', 'my_collection')


# Usage examples
if __name__ == "__main__":
  # Simple usage
  pass
