#!/usr/bin/env python3
"""
art/immeub/rent/data/contract01_datadict.py

import art.immeub.rent.data.contract01_datadict.py
art.immeub.rent.models.contract_molder.Person
import copy
"""
import art.immeub.rent.models.contract_molder as mold  # mold.Person
import datetime
from dinero import Dinero
from dinero.currencies import BRL
from __init__ import DEFAULT_NMONTHS_DURATION
import lib.numberfs.cpf_verifica as cpfv  # cpfv.calcula_cpf_via_reduce
_, cpf1, _ = cpfv.calcula_triple_cpf_via_reduce('123456789')
_, cpf2, _ = cpfv.calcula_triple_cpf_via_reduce('987654321')
cdouto_address = ['Av Avenue s/n', 'Botágua  - 99.888-777']
fiador_address = ['Av Fiança s/n', 'Copa  - 22.333-444']


tenant1 = mold.Person(
  fullname='João Johannes',
  cpf=cpf1,
  phonenumber='blah',
  email='blah',
  email_alt='blah',
  phonenumber_alt='blah',
  docid='blah',
  docid_alt='blah',
  profession='blah',
  birth_date=datetime.date(year=1980, month=1, day=1),
  address=cdouto_address,
  obs=['observação 1'],
)
fiador = mold.Person(
  fullname='Maria Mariah',
  cpf=cpf2,
  phonenumber='blah',
  email='blah',
  email_alt='blah',
  phonenumber_alt='blah',
  docid='blah',
  docid_alt='blah',
  profession='blah',
  birth_date=datetime.date(year=1980, month=1, day=1),
  address=fiador_address,
  obs=['observação 1'],
)


immeub = mold.Immeub(
  imm_nickname='CDouto',
  inscr_munic='12345',
  inscr_txincend='54321',
  address=cdouto_address,
  phys_description="3 quartos, sala, cozinha, 120m2",
  other_characts="perto da praça e das estações metrô A e B",
)

rcontract = mold.RentContract(
  imm_nickname='CDouto',  # may attach obj mold.Immeub by this 'key'
  inidate=datetime.date(year=2026, month=1, day=1),
  cur_rentvalue=Dinero("1100", BRL),
  ori_rentvalue=Dinero("1000", BRL),
  nmonths_duration=DEFAULT_NMONTHS_DURATION,
  has_proptax=True,
  has_incendtarif=True,
  has_condtarif=True,
  tenants=[tenant1],
  fiadores=[fiador],
)


def adhoctest1():
  print(rcontract)


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
