"""
art/bookroutes/packt/__init__.py
  This package contains package definitions
  (config) for (local/selected) packt bookroutes.
"""
FALLBACK_LOCAL_BOOKS_ROOTFOLDER = "/home/dados/Books/epub Books"
DEFAULT_LOCAL_MONGO_CONN_URL = "mongodb://localhost:27017"
DEFAULT_MONGO_DBNAME = 'packt_books_db'
DEFAULT_MONGO_COLLNAME = "packt_books_coll"
DEFAULT_PACKT_JSON_FILENAME = 'packt_books_on_folders.json'
URL_BEFORE_KA = "https://subscription.packtpub.com/book"
PACKT_URL_TO_INTERPOL = URL_BEFORE_KA + "/{packts_midurl_ka}/{isbn13}"
