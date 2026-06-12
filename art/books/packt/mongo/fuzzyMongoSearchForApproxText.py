#!/usr/bin/env python3
"""
art/books/packt/mongo/fuzzyMongoSearchForApproxText.py
  Fuzzy-searches the Packt book Mongo collection in the
    use case when the search-text has misspelling or typos.

"/home/dados/Books/epub Books"
"""
from pymongo import MongoClient
from rapidfuzz import process, fuzz
from art.books.packt import DEFAULT_MONGO_DBNAME
from art.books.packt import DEFAULT_MONGO_COLLNAME
from art.books.packt import DEFAULT_LOCAL_MONGO_CONN_URL


class FuzzySearch:

  def __init__(self):
    self.search_words = None
    self.n_found = 0
    self.cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.open_conn()

  def open_conn(self):
    # 1. Connect to your MongoDB
    # Replace with your actual connection string, database, and collection names
    self.cli_conn = MongoClient(DEFAULT_LOCAL_MONGO_CONN_URL)
    self.mongo_db = self.cli_conn[DEFAULT_MONGO_DBNAME]
    self.mongo_coll = self.mongo_db[DEFAULT_MONGO_COLLNAME]

  def fuzzy_search_books(
      self, user_input, threshold=60
  ):
    """
    Searches for book titles using a mix of MongoDB regex and RapidFuzz for typos.

    :param user_input: The potentially misspelled search string from the user.
    :param threshold: The minimum match score (0-100) to consider a result valid.
    """
    # Step A: Broad Match via MongoDB
    # We take the first few characters or words to do a quick, case-insensitive partial match.
    # This prevents loading the entire database into Python.
    search_words = user_input.split()
    if search_words:
      # Create a regex pattern that looks for any of the words as a starting point
      regex_pattern = "|".join(search_words)
      query = {"title": {"$regex": regex_pattern, "$options": "i"}}
    else:
      query = {}
    # Fetch candidates from Mongo (projecting only the fields we need)
    candidates = list(self.mongo_coll.find(query, {"_id": 1, "title": 1, "author": 1}))
    if not candidates:
      return []
    # Step B: Fuzzy Matching with RapidFuzz
    # Extract just the titles for the library to compare against
    titles = [doc["title"] for doc in candidates]
    # process.extract returns a list of tuples: (matched_string, score, index)
    # WRATIO is great for short texts like titles because it handles case and minor order changes well.
    fuzzy_results = process.extract(
      query=user_input,
      scorer_kwargs=titles,
      scorer=fuzz.WRatio,
      score_cutoff=threshold
    )
    # Step C: Rebuild the final sorted list of documents
    final_results = []
    for matched_title, score, index in fuzzy_results:
      original_doc = candidates[index]
      # Append the match score so you can display it or debug
      original_doc["match_score"] = round(score, 2)
      final_results.append(original_doc)

    return final_results

  def insert_dummy_data(self):
    """
    # Let's insert some dummy data for demonstration
    """
    self.mongo_coll.delete_many({})  # Clear old data
    self.mongo_coll.insert_many([
      {"title": "Mastering Python", "author": "Samir Madhavan"},
    ])

  def do_search(self):
    # Simulate a user typo
    user_search = "Mastering Python"
    print(f"Searching for: '{user_search}'...\n")
    # fuzzer = FuzzySearch()
    results = self.fuzzy_search_books(user_search, threshold=50)

  def process(self):
    self.insert_dummy_data()
    print(self)

  def __str__(self):
    outstr = f"""{self.__class__.__name__}:
    search_words = {self.search_words}
    n_found = {self.n_found}
    """
    return outstr


def process():
  """
    {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
    {"title": "Harry Potter and the Sorcerer's Stone", "author": "J.K. Rowling"},
    {"title": "The Hobbit", "author": "J.R.R. Tolkien"},
    {"title": "To Kill a Mockingbird", "author": "Harper Lee"}
  # --- EXAMPLE USAGE ---
  """
  fuzzer = FuzzySearch()
  fuzzer.process()
  user_search = "Mastering Python"
  results = fuzzer.fuzzy_search_books(user_search, threshold=50)
  for book in results:
    print(f"Found: {book['title']} by {book['author']}")
    print(f"Confidence Score: {book['match_score']}%\n")


if __name__ == "__main__":
  """
  """
  process()
