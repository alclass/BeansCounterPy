#!/usr/bin/env python3
"""
app/routes/immeubroutes.py

@see app/fastapi_main.py for how to 'spawn' the FastAPI server
immeub_router = APIRouter(prefix="/imov/{refmonth}", tags=["Immeub id Context"])
"""
from fastapi import APIRouter
from app.routes.immeubroutes import cobrancaroutes
# Note: this will be appended to the id_router path
immeubrouter = APIRouter(prefix="")
immeubrouter.include_router(cobrancaroutes.cobrancarouter, prefix="/mes")
immeub_all_router = APIRouter(prefix="/all")
immeub_sig_router = APIRouter(prefix="/sigla")
# immeubrouter.include_router(immeub_sig_router, prefix="/{immeub_id}", tags=["Immeub id Context"])
# immeubrouter.include_router(immeub_all_router, prefix="/all", tags=["Immeub All Context"])
immeub_dictlist = [
    {"iid": 1, "sigla": "CDout", "endr": ["Rua Camel Doutor, 67 apt 101", "99.999-999 - Barra Central"]},
    {"iid": 2, "sigla": "Jacum", "endr": ["Rua James Jacum, 11 apt 201", "99.999-999 - Barra Central"]},
    {"iid": 3, "sigla": "SanFar", "endr": ["Rua San Farm, 1 cas A", "99.999-999 - Barra Leste"]},
]


@immeub_all_router.get("/all")
async def get_all_immeubs():
    """
    URL-path => /imovs
    all the available immeubs
    """
    return immeub_dictlist


@immeubrouter.get("/")
async def get_immeub_by_id(iid: int):
  """
  It is getting by http://127.0.0.1:8000/imovs/imov/1/?iid=1
  But it should be getting by http://127.0.0.1:8000/imov/imov/1
  return {
    "message": "Accessed compound route",
    "id": id,
    "date": date
  }
  """
  foundlist = list(filter(lambda x: x['iid'] == iid, immeub_dictlist))
  if len(foundlist) > 0:
    immeub_dict_found = foundlist[0]  # the first found, immeub_id should not repeat
    return immeub_dict_found
  return {"msg": "unknown immeubroutes"}


@immeub_sig_router.get("/sigla")
async def get_immeub_by_sigla(sigla: str):
  """
  """
  sigla = sigla.lower()
  foundlist = list(filter(lambda x: x['sigla'].lower() == sigla, immeub_dictlist))
  if len(foundlist) > 0:
    immeub_dict_found = foundlist[0]  # the first found, immeub_sigla (or nickname) should not repeat
    return immeub_dict_found
  return {"msg": "unknown immeubroutes"}
