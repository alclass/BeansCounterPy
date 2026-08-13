"""
art/immeub/rent/mdb/mongocollections_finder.py

"""
import datetime
import art.immeub.rent.mdb.mongo_rent_retriever as mreader  # .MongoDBCollectionRetriever
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.PydtcPerson
import art.immeub.rent.pdntcmdls.immeub_pydant as immeub
import art.immeub.rent.pdntcmdls.billingcard_pydantic as bcard  #
PERSON_COLL = 'persons'


def get_persons_by_cpfs(cpfs: list[str]) -> list[pers.PydtcPerson]:
  persons = []
  retriever = mreader.MongoDBCollectionRetriever()
  docs = retriever.fetch_w_1coll_2fieldname_3list(
    collname=PERSON_COLL,
    fieldname='cpf',
    valuelist=cpfs,
  )
  for doc in docs:
    del doc['_id']
    doc['nomecompleto'] = doc['name']
    del doc['name']
    # del doc['cpf']
    person = pers.PydtcPerson.instantiate_from_jsondict(doc)
    persons.append(person)
  return persons


def get_immeubles_by_nicknames(nicknames: list[str]) -> list[immeub.PydtcImmeuble]:
  locations = []
  retriever = mreader.MongoDBCollectionRetriever()
  query = {'imm_nickname': nicknames}
  collname = 'immeubles'
  docs = retriever.find_by_coll_n_query(collname, query)
  for doc in docs:
    location = immeub.PydtcImmeuble.instantiate_from_jsondict(**doc)
    locations.append(location)
  return locations


def get_billingcards_by_nn_n_refmonth(nn_n_refmonths: list[tuple[str, datetime.date]]) -> list[immeub.PydtcImmeuble]:
  locations = []
  contrnumbers = [f"{s.lower()}{dt.strftime('%y%m')}" for s, dt in nn_n_refmonths]
  retriever = mreader.MongoDBCollectionRetriever()
  query = {'contrnumber': contrnumbers}
  collname = 'billingcards'
  docs = retriever.find_by_coll_n_query(collname, query)
  for doc in docs:
    location = bcard.PydtcBillingCard.instantiate_from_json(**doc)
    locations.append(location)
  return locations


def adhoctest1():
  persons = get_persons_by_cpfs(['12345678909'])
  print('persons', persons)


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
