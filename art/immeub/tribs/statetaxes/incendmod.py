"""

"""
import pymongo
MONGODB_CON_STR = "mongodb://localhost:27017/"
MONGO_DBNAME = "immeub_db"
MONGO_COLLNAME = "fnsbm_trfs"


class MongoRetriever:

  def __init__(self):
    self.mongo_cli_conn = None
    self.mongo_db = None
    self.mongo_coll = None
    self.mongo_dbname = MONGO_DBNAME
    self.mongo_collname = MONGO_COLLNAME

  def open_mongo_conn(self):
    """
      self.mongo_db = self.mongo_cli_conn[self.mongo_dbname]
      self.mongo_coll = self.mongo_db[self.mongo_collname]
      # Count documents
      self.mongo_count = self.mongo_coll.count_documents({})
    """
    self.mongo_cli_conn = pymongo.MongoClient(MONGODB_CON_STR)
    self.mongo_db = self.mongo_cli_conn["immeub"]
    self.mongo_coll = self.mongo_db[self.mongo_collname]

  def get_incendtarif_fo_location_if_available(self, imovel_apelido):
    """

    """
    query = {
      '$getField': ['imm_nickname', 'incendtarif', 'has_been_issued'],
    }
    self.open_mongo_conn()
    mongo_doc = self.mongo_coll.find_one(query)
    if mongo_doc is not None:
      imovel_apelido = mongo_doc['imm_nickname']
      incendtarif = mongo_doc['incendtarif']
      has_been_issued = mongo_doc['has_been_issued']
      if imovel_apelido is not None:
        if incendtarif is not None:
          if has_been_issued is False:
            return incendtarif
    return None


def get_incendtarif_fo_location_if_available(imovel_apelido):
  """
  Look up MongoDB to verify if an incendtarif is available.
  """
  retriever = MongoRetriever()
  return retriever.get_incendtarif_fo_location_if_available(imovel_apelido)


def adhoctest1():
  """
  refmonths_reader_fr_db()
  """
  imovel_apelido = 'cdouto'
  result = get_incendtarif_fo_location_if_available(imovel_apelido)
  scrmsg = f""" -> get_incendtarif_fo_location_if_available({imovel_apelido})
  -> {result}"""
  print(scrmsg)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()