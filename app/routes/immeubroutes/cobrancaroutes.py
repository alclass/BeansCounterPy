#!/usr/bin/env python3
"""
app/routes/immeubroutes/co branca_routes.py

"""
from fastapi import APIRouter
import art.immeub.rent.models.json_fatura_maker as jfat  # jfat.make_one
cobrancarouter = APIRouter(prefix="/mes", tags=["Month's Cobrança Context"])
router = APIRouter()


@cobrancarouter.get("/")
async def get_cobranca_by_immeub_sigla_n_refmonth(sigla: str, refmonth: str):
  """
  URL-path-part => /imov/<immeubroutes>/mes/<refmonth>

  It's getting by http://127.0.0.1:8000/imov/mes/mes/?sigla=cdutra&refmonth=any
  It should be getting by http://127.0.0.1:8000/imov/<imov>/mes/<mes>

    Example:
      http://www.domain.ext/immeub/{immeub_nick}/mes/{refmonthdate}
      http://127.0.0.1:8000/immeub/any/mes/any_refmonth

    return {"immeub_nick": immeub_nick, "refmonthdate": refmonthdate}
    An Example JSON fatura_card:
      @module: art.immeubroutes.rent.models.json_fatura_maker
        function: make_one
  """
  _, _ = sigla, refmonth
  return jfat.make_one()
