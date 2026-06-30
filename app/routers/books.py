# app/routers/immeub_billings.py
import art.books.packt.mongo.retrievers.retrievesBooksMetaFromMongo as retr  # .MongoDBCollectionRetriever
from fastapi import APIRouter
router = APIRouter()


@router.get("/")
async def get_all_books():
  mfetcher = retr.MongoDBCollectionRetriever()
  jsonlist = mfetcher.retrieve_all_as_json()
  return jsonlist


@router.get("/{isbn13}")
async def get_immeub(isbn13: str):
  mfetcher = retr.MongoDBCollectionRetriever()
  bookmeta = mfetcher.find_by_isbn13(isbn13)
  return bookmeta
