"""
art/immeub/rent/mdb/objs_finder_from_mongocollections.py
  Contains fetching functions for the 'rent' data models.
  These are: Person, Immeuble (or Location), RentContract, and BillingCard.
  Intermediate fetchers to avoid circular imports between the models and the 'createdate' modules.

To import this:
  import art.immeub.rent.mdb.objs_finders_from_mongocollections as fndr  # fndr.dbfetch_billingcard_dictdoc_w_refmonth_n_contrnumber
"""
import datetime
import lib.datesetc.refmonth_fs as rmfs
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch


def mongoquery_w_querydict_n_dbfetcher_asdict(querydict: dict, dbfetcher: mngfetch.GenMongoDBFetcher) -> dict:
  docdict = dbfetcher.find_one_w_querydict_n_collname_as_dict(querydict)
  return docdict


def dbfetch_billingcard_docdict_w_refmonth_n_contrnumber_asdict(
    contrnumber: str, refmonth: datetime.date,
  ) -> dict:
  dbname, collname = 'immeub_db', 'billingcards'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"contrnumber": contrnumber, "refmonth": refmonth.strftime("%Y-%m-%d")}
  return mongoquery_w_querydict_n_dbfetcher_asdict(querydict, dbfetcher)


def dbfetch_rentcontract_docdict_w_contrnumber_asdict(contrnumber: str) -> dict:
  dbname, collname = 'immeub_db', 'rentcontracts'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"contrnumber": contrnumber}
  return mongoquery_w_querydict_n_dbfetcher_asdict(querydict, dbfetcher)


def dbfetch_immeuble_docdict_w_contrnumber_asdict(imm_nickname: str) -> dict:
  dbname, collname = 'immeub_db', 'immeubles'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"imm_nickname": imm_nickname}
  return mongoquery_w_querydict_n_dbfetcher_asdict(querydict, dbfetcher)


def dbfetch_person_docdict_w_cpf_asdict(cpf: str) -> dict:
  dbname, collname = 'immeub_db', 'persons'
  dbfetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  querydict = {"cpf": cpf}
  return mongoquery_w_querydict_n_dbfetcher_asdict(querydict, dbfetcher)


def adhoctest1():
  # person
  cpf = '12345678143'
  person = dbfetch_person_docdict_w_cpf_asdict(cpf)
  print('person', person)
  # =================
  # immeuble (or location)
  imm_nickname = 'CDouto'
  immeuble_asdict = dbfetch_immeuble_docdict_w_contrnumber_asdict(imm_nickname)
  print('immeuble_asdict', immeuble_asdict)
  # =================
  # rentcontract
  contrnumber = 'CDouto202401'
  rentcontract_asdict = dbfetch_rentcontract_docdict_w_contrnumber_asdict(contrnumber)
  print('rentcontract_asdict', rentcontract_asdict)
  # =================
  # billingcard
  refmonthstr = '2026-4'
  refmonth = rmfs.make_refmonth_or_raise(refmonthstr)
  contrnumber = 'CDouto202401'
  billingcard = dbfetch_billingcard_docdict_w_refmonth_n_contrnumber_asdict(
    contrnumber=contrnumber, refmonth=refmonth
  )
  print('billingcard', billingcard)



def process():
  pass


if __name__ == "__main__":
  """
  process()
  """
  adhoctest1()
