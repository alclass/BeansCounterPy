"""
lib/dbfs/mngdb/mongo_gen_fetcher.py
  Fetches docs in MongoDB collections.

Info on the triple parameter set:
  a) CONNECT_URL:
       may be sent in (as a parameter),
       maybe be found in .env (as a default)
       maybe be found in __init__ (as a default if not in .env)
  b) DBNAME:
     the same as above
  c) COLLNAME:
     the same as above
     and it may also be changed upon method calls.

  Though COLLNAME may change across methods,
    as an idea, the client caller may as well instantiate other 'fetchers'.
"""
import re
from bson.json_util import dumps
from pymongo import MongoClient, collation
import lib.dbfs.mngdb as mdbinit
DEFAULT_MONGODB_URI_CON_STR = mdbinit.MONGODB_URI_CON_STR
DEFAULT_MONGODB_DBNAME = mdbinit.MONGODB_DBNAME


def batch_set_runonce_colations_to_mongodb_collections():
  fetcher = GenMongoDBFetcher(
    uri_con_str=DEFAULT_MONGODB_URI_CON_STR,
    dbname="immeub_db",
    collname='billingcards'
  )
  # create the index once (strength 2 ignores case and accents)
  # 1 contrnumber in billingcards
  fetcher.mongodb_coll.create_index(
      [("contrnumber", 1)],
      collation=collation.Collation(locale="pt", strength=2)
  )
  # 2 nomecompleto in persons
  fetcher.reset_collname('persons')
  fetcher.mongodb_coll.create_index(
      [("nomecompleto", 1)],
      collation=collation.Collation(locale="pt", strength=2)
  )


class GenMongoDBFetcher:
  """
  The client_connection and dbname are related to package/module.
  The collection names are parameterized, and the ones in the 'db'.
  """

  def __init__(
      self, uri_con_str: str | None = None,
      dbname: str | None = None,
      collname: str | None = None,
    ):
    self.uri_con_str = uri_con_str
    self.dbname = dbname
    self.collname = collname  # maybe None
    self.collcount = None
    self.mng_cli_con = None
    self.mongodb_db = None
    self.mongodb_coll = None
    self.set_defaults_if_needed()
    # raise an exception in case defaults failed
    self.raise_if_either_constr_or_dbname_is_none()
    self.set_n_open_1clientconnection_2db_3collection()

  def set_defaults_if_needed(self):
    if self.uri_con_str is None:
      self.uri_con_str = DEFAULT_MONGODB_URI_CON_STR
    if self.dbname is None:
      self.dbname = DEFAULT_MONGODB_DBNAME

  def raise_if_either_constr_or_dbname_is_none(self):
    """
    This is a kind of 'last resort method' if defaults failed before.
    """
    uri, dbname = self.uri_con_str, self.dbname
    error_msglines = []
    if uri is None:
      errmsg = f"Error: connection string uri_con_str (={uri} is None."
      error_msglines.append(errmsg)
    if dbname is None:
      errmsg = f"Error: dbname is None."
      error_msglines.append(errmsg)
    errmsg = '\n'.join(error_msglines)
    if len(error_msglines) > 0:
      raise ValueError(errmsg)

  def set_n_open_1clientconnection_2db_3collection(self):
    """
    Sets and opens MongoDB connection.
    It also sets 'db' and 'collection' if any.

    """
    self.mng_cli_con = MongoClient(self.uri_con_str)
    self.mongodb_db = self.mng_cli_con[self.dbname]
    self.set_or_change_collname(self.collname)

  def set_collection_inner(self, collname: str):
    """
    Sets collname and initializes self.mongodb_coll.
    Consider this method private.
    Only to be called from within this class.
    (And only from set_or_change_collname() and reset_collname().)
    """
    self.collname = collname
    self.mongodb_coll = self.mongodb_db[self.collname]
    if self.mongodb_coll is None:
      errmsg = f"Error: MongoDB collection (mongodb_coll) is None."
      raise ValueError(errmsg)
    # count documents in collection
    self.collcount = self.mongodb_coll.count_documents({})
    pass

  def reset_collname(self, collname: str):
    self.set_collection_inner(collname)

  def set_or_change_collname(self, collname: str | None):
    """
    Sets or changes (resets) collname.
    If collname is not None, self.mongodb_coll should be (re)initialized.
    This method verifies all hypotheses (@see also method's code).
    """
    if collname is None:
      if self.mongodb_coll is not None:
        # notice that collname will be None most of the time
        # when coming from the find methods
        # having it been previously init'ed at construction time
        return
      if self.collname is not None:
        # though self.mongodb_coll is None, self.collname is not
        # then try to initialize self.mongodb_coll with self.collname
        self.set_collection_inner(self.collname)
        return
      # at this point: collname, self.mongodb_coll and self.collname
      # are all None: raise ValueError
      errmsg = f"Error: collection name is None."
      raise ValueError(errmsg)
    # at this point collname is not None:
    if collname == self.collname:
      # they are the same, it's still necessary to check mongodb_coll
      # because the constructor calls it using self.collname as parameter
      if self.mongodb_coll is None:
        # call set_inner because name was set, but not the collection proper
        self.set_collection_inner(collname)
      # at this point, self.mongodb_coll is not None
      # so it's okay to return
      return
    # at this point, collname != self.collname, so (re)set it
    self.set_collection_inner(collname)
    return

  def remove_this_set_or_change_collname(self, collname: str | None):
    self.set_or_change_collname(collname)
    if self.mongodb_coll is None:
      errmsg = f"Error: mongodb_coll could not be initialized."
      raise ValueError(errmsg)

  def find_as_cursor_by_coll_n_query(self, query: dict, collname: str | None = None):
    self.set_or_change_collname(collname)
    if collname is not None:
      self.set_or_change_collname(collname)
    cursordocs = self.mongodb_coll.find(query)
    return cursordocs

  def find_by_coll_n_query(
      self, query: dict, collname: str | None = None
    ) -> list[str]:
    docs = []
    cursordocs = self.find_as_cursor_by_coll_n_query(
      query=query, collname=collname
    )
    # Convert cursor to a list of dicts, then serialize to JSON string
    json_str_list = list(map(lambda j: dumps(j), cursordocs))
    return json_str_list

  def find_w_1coll_2fieldname_3list(
      self, fieldname: str, valuelist: list, collname: str | None = None
    ) -> list[str]:
    """
    Finds by fieldname, a value list and optional collection_name.
    It encapsulates to find_by_coll_n_query() above.
    """
    if collname is not None:
      self.set_or_change_collname(collname)
    query = {fieldname: {"$in": valuelist}}
    if valuelist is None or len(valuelist) > 0:
      docs = self.fetch_all(collname=collname)
    else:
      docs = self.find_by_coll_n_query(
        query=query, collname=collname
      )
    return docs

  def fetch_all(self, collname: str | None = None) -> list[str]:
    """
    Encapsulates find_by_coll_n_query() sending an empty {}.
    """
    return self.find_by_coll_n_query(
      query={}, collname=collname
    )

  def rename_fieldname_fr_to(
      self, from_fieldname: str, to_fieldname: str, collname: str | None = None,
    ):
    """
    result = collection.update_many({}, rename_operation)
    print(f"Matched documents: {result.matched_count}")
    print(f"Modified documents: {result.modified_count}")
    """
    self.set_or_change_collname(collname)
    rename_operation = {
      "$rename": {
        f"{from_fieldname}": f"{to_fieldname}"
      }
    }
    result = self.mongodb_coll.update_many({}, rename_operation)
    matched_docs = result.matched_count
    modified_docs = result.modified_count
    return matched_docs, modified_docs

  def close_conn(self):
    if self.mng_cli_con is not None:
      self.mng_cli_con.close()


def get_jdocs_by_1fieldname_2valuelist_3collname_4dbname(
    fieldname: str, valuelist: list[str], collname: str, dbname: str | None = None
  ) -> list[str]:
  # dbname, collname = 'immeub_db', 'persons'
  retriever = GenMongoDBFetcher(
    dbname=dbname,
    collname=collname,
  )
  jsondocs = retriever.find_w_1coll_2fieldname_3list(
    fieldname=fieldname, valuelist=valuelist
  )
  retriever.close_conn()
  return jsondocs


def get_persons_by_cpfs(cpfs: list[str]) -> list:
  dbname, collname = 'immeub_db', 'persons'
  fieldname, valuelist = 'cpf', cpfs
  jsondocs = get_jdocs_by_1fieldname_2valuelist_3collname_4dbname(
    fieldname=fieldname, valuelist=valuelist, collname=collname, dbname=dbname
  )
  return jsondocs


def get_immeubles_by_nicknames(nicknames: list[str]) -> list:
  dbname, collname = 'immeub_db', 'immeubles'
  fieldname, valuelist = 'imm_nickname', nicknames
  jsondocs = get_jdocs_by_1fieldname_2valuelist_3collname_4dbname(
    fieldname=fieldname, valuelist=valuelist, collname=collname, dbname=dbname
  )
  return jsondocs


def get_billingcards_by_contrnumbers(contrnumbers: list[str]) -> list:
  dbname, collname = 'immeub_db', 'billingcards'
  fieldname, valuelist = 'contrnumber', contrnumbers
  jsondocs = get_jdocs_by_1fieldname_2valuelist_3collname_4dbname(
    fieldname=fieldname, valuelist=valuelist, collname=collname, dbname=dbname
  )
  return jsondocs


def adhoctest1():
  # persons
  cpfs = ['12345678909']
  print('cpfs', cpfs)
  persons = get_persons_by_cpfs(cpfs)
  # persons = json.dumps(persons, indent=2)
  print('persons', persons)
  # immeubles
  imm_nicknames = ['cdouto']
  print('imm_nicknames', imm_nicknames)
  locations = get_immeubles_by_nicknames(imm_nicknames)
  print('locations', locations)
  # billingcards
  contrnumbers = ['CDouto202401']
  print('contrnumbers', contrnumbers)
  billingcards = get_billingcards_by_contrnumbers(contrnumbers)
  print('billingcards', billingcards)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  batch_set_runonce_colations_to_mongodb_collections()
  """
  adhoctest1()
