#!/usr/bin/env python3
"""
art/bks/fastapi/bookroutes.py
  Defines the FastAPI route endpoints for the 'book app'.


import art.bks.fastapi.bookroutes as bkrts  # bkrts.get_all_books
"""
import art.bks.packt.mongo.retrievers.retrievesBooksMetaFromMongo as rMongo  # .MongoDBCollectionRetriever
from fastapi import APIRouter
router = APIRouter()


@router.get("/")
async def get_all_books():
  mfetcher = rMongo.MongoDBCollectionRetriever()
  jsonlist = mfetcher.retrieve_all_as_json()
  return jsonlist


@router.get("/{isbn13}")
async def get_immeub(isbn13: str):
  mfetcher = rMongo.MongoDBCollectionRetriever()
  bookmeta = mfetcher.find_by_isbn13(isbn13)
  return bookmeta
