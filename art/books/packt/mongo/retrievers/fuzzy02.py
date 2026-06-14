#!/usr/bin/env python3
"""
art/books/packt/mongo/fuzzy02.py
  Fuzzy-searches the Packt book Mongo collection in the
    use case when the search-text has misspelling or typos.

"/home/dados/Books/epub Books"
"""
# from rapidfuzz import process, fuzz
# import rapidfuzz as rapfuz
from art.books.packt import DEFAULT_MONGO_DBNAME
from art.books.packt import DEFAULT_MONGO_COLLNAME
from art.books.packt import DEFAULT_LOCAL_MONGO_CONN_URL
from rapidfuzz import fuzz  # , process
from pymongo import MongoClient
import sys


def search_collection_fuzzy(
    collection, search_text, fields, threshold=70, limit=20
):
  """
  Fuzzy search across multiple fields in MongoDB collection

  Args:
      collection: MongoDB collection object
      search_text: string to search for
      fields: list of field names to search (e.g., ['title', 'authors'])
      threshold: minimum similarity score (0-100, default 70)
      limit: maximum number of results to return

  Returns:
      list of matched documents with similarity scores
  """

  # Fetch all documents (for small to medium collections)
  # For large collections, consider preprocessing (see optimization notes)
  all_docs = list(collection.find({}, {field: 1 for field in fields}))

  results = []

  for doc in all_docs:
    best_score = 0
    matched_field = None

    # Combine text from all searchable fields
    for field in fields:
      field_value = doc.get(field, '')
      if field_value:
        # Handle both string and list fields (like authors array)
        if isinstance(field_value, list):
          # Join list items for comparison
          field_value = ' '.join(str(item) for item in field_value)

        # Calculate similarity score
        score = fuzz.partial_ratio(search_text.lower(), field_value.lower())

        if score > best_score:
          best_score = score
          matched_field = field

    # Only keep results above threshold
    if best_score >= threshold:
      results.append({
        'document': doc,
        'similarity_score': best_score,
        'matched_field': matched_field
      })

  # Sort by score (highest first) and limit results
  results.sort(key=lambda x: x['similarity_score'], reverse=True)
  return results[:limit]


def modulesprocess():
  """
  """
  # Connect to MongoDB (adjust connection string as needed)
  client = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
  db = client[DEFAULT_MONGO_DBNAME]
  collection = db[DEFAULT_MONGO_COLLNAME]

  # Get search text from command line
  # if len(sys.argv) < 2:
  #   print("Usage: python script.py 'search text'")
  #   sys.exit(1)
  # search_text = ' '.join(sys.argv[1:])

  search_text = 'mastering python'
  scrmsg = f"search_text: {search_text}"
  print(scrmsg)


  # CASE 1: Search only in 'title' field
  print(f"\n=== Case 1: Searching for '{search_text}' in titles ===")
  case1_results = search_collection_fuzzy(collection, search_text, ['title', 'author', 'year', 'isbn13'], threshold=60)

  if case1_results:
    for i, result in enumerate(case1_results[:10], 1):
      print(f"{i}. Title: {result['document']}")  # .get() 'title', 'N/'
      print(f"   Similarity: {result['similarity_score']}%")
      print(f"   Authors: {result['document'].get('authors', 'N/A')}\n")
  else:
    print("No matches found.\n")

  # CASE 2: Search in both 'title' and 'authors' fields
  print(f"\n=== Case 2: Searching for '{search_text}' in titles AND authors ===")
  case2_results = search_collection_fuzzy(collection, search_text, ['title', 'authors', 'year'], threshold=60)

  if case2_results:
    for i, result in enumerate(case2_results[:10], 1):
      print(f"{i}. Title: {result['document'].get('title', 'N/A')}")
      print(f"   Authors: {result['document'].get('authors', 'N/A')}")
      print(f"   Similarity: {result['similarity_score']}% (matched in: {result['matched_field']})\n")
  else:
    print("No matches found.\n")


if __name__ == "__main__":
  modulesprocess()
