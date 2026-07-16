#!/usr/bin/env python3
"""
app/fastapi_main.py


command line for spawning the FastAPI server
    (directly with FastAPI) fastapi run app/fastapi_main.py
    (directly with uvicorn) uvicorn app:fastapi_main --host 0.0.0.0 --port 80

For reolading the app when it's changed:
    $ fastapi dev app/fastapi_main.py
    $ uvicorn main:app.fastapi_main --reload

@id_router.get("/")
async def get_by_id(id: int):
    return {"message": "Accessed base route for ID", "id": id}
"""
from fastapi import FastAPI
import art.bks.fastapi.bookroutes as bkrts  # bkrts.get_all_books
from app.routes.immeubroutes import immeubroutes  # cobrancaroutes is placed in immeubroutes
app = FastAPI(title="My Scalable API")
# Mount the cobranca_router into the id_router to achieve the compound URL
# immeubroutes.immeubrouter.include_router(cobrancaroutes.router)
app.include_router(
  immeubroutes.immeubrouter,
  prefix="/imov"
)
app.include_router(
  bkrts.router,
  prefix="/bks",
  tags=["Books Operations"]
)


@app.get("/")
async def root():
    return {"message": "Welcome to the central API"}
