#!/usr/bin/env python3
"""
art/immeubroutes/rent/models/json_fatura_maker.py

fatura fields

header:
  name
  address:
    address 1
    address 2
  email
  telephone

fatura_card:
  current:
    aluguel
    condominium
    property tribute
  mora_if_any:
    tipo | aluguel-ou-encargos-em-mora | ref r1 | fator de base | valor
    tipo | aluguel-ou-encargos-em-mora | ref r2 | fator de base | valor
    tipo | aluguel-ou-encargos-em-mora | ref rN | fator de base | valor

import calendar
import copy
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonths_mod as refmonth_fs.py  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
import lib.finfs.indices.indices_fetch_n_fs as cmfs  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
from dateutil import relativedelta
"""
import datetime
import json
from dinero import Dinero
from dinero.currencies import BRL
from dataclasses import asdict  # , dataclass, field   # , field
import art.immeub.rent.bill as init  # refmonth_fs.py.fillin_refmonths_fr_ndayslist
import lib.datesetc.refmonth_fs as rmfs
import lib.datesetc.datefs as dtfs
import art.immeub.rent.models.fatura_etal_models as fatfs  # fatfs.FaturaCard
DEFAULT_FIX_IR_PCT = init.DEFAULT_FIX_IR_PCT  # this is percentual
DEFAULT_FIX_IR_DEC = DEFAULT_FIX_IR_PCT / 100  # this is decimal


def json_date_serial(obj):
    """JSON serializer for objects not serializable by default JSON code"""
    if isinstance(obj, datetime.date):
        return dtfs.date_to_str_4y_dash_2m_dash_2d(obj)
    if isinstance(obj, Dinero):
      strval = f"{obj.raw_amount:.2f}"
      return strval
    raise TypeError(f"Type {type(obj)} not serializable")


class Mounter:
  pass


def make_one():
  """
  art.immeubroutes.rent.models.json_fatura_maker.make_one
  """
  today = datetime.date.today()
  immeub_address = ["Rua Camel Doutor, 67 apt 101", "Barra Central 20999-999"]
  refmonth = rmfs.calc_refmonth_minus_n(today, 1)
  proptrib = fatfs.PropTrib(
    munic_inscr='AAAAA',
    cityname="Rio de Janeiro",
    immeub_address=immeub_address,
    monthlypay=Dinero("250", BRL),
    refmonth=refmonth,
  )
  thisyear = today.year
  incendtarif_refyear = thisyear - 1
  incendtax = fatfs.IncendTax(
    immeub_address=immeub_address,
    incend_inscr='1m2aa-54b',
    uf_statesigla='RJ',
    yearly_value=Dinero("50", BRL),
    refyear=incendtarif_refyear,
  )
  condtarif = fatfs.CondTarif(
    condname='Edifício Douto',
    immeub_address=immeub_address,
    refmonth=refmonth,
    tarifvalue=Dinero("150", BRL),
    # espelho_pdf_url: str = None
  )
  faturalines = []
  # 1st aluguel
  faturaline = fatfs.FaturaLine(
    tipo="AE",
    description="aluguel",
    refmonth=refmonth,
    explain="no prazo",
    cred_or_debt="D",
    value=Dinero(str(1000), BRL)
  )
  faturalines.append(faturaline)
  # 2nd prop trib
  faturaline = proptrib.generate_faturaline()
  faturalines.append(faturaline)
  # 3rd incend tax
  faturaline = incendtax.generate_faturaline()
  faturalines.append(faturaline)
  # 4th condominium
  faturaline = condtarif.generate_faturaline()
  faturalines.append(faturaline)
  # =======================
  faturacard = fatfs.FaturaCard(
    payor_name="John Doe",
    immeub_nn="CDoutor",
    address=immeub_address,
    email="john@email.test",
    telephone="9999-1111",
    fat_launchdate=today,
    refmonth=refmonth,
    endr_pix_a_pagar="pix_receiver@email.test",
    items=faturalines
  )
  faturacard.calculate()
  pdict = asdict(faturacard)
  json_string = json.dumps(pdict, default=json_date_serial)
  print(json.dumps(json_string, indent=2))
  return json_string


def adhoctest1():
  make_one()


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest1()
