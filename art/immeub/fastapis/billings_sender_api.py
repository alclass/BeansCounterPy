#!/usr/bin/env python3
"""
art/immeub/fastapis/billings_sender_api.py

uvicorn art/immeub/fastapis/billings_sender_api:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import art.immeub.fastapis.dummy_adhoc_dict as dum  # dum.BILLING_DATA
BILLING_DATA = dum.BILLING_DATA


def process():
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  """
  process()


app = FastAPI()
# Allow requests from your Node.js frontend (default port 3000)
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_methods=["GET"],
)


@app.get("/api/billing")
async def get_billing():
    return BILLING_DATA
