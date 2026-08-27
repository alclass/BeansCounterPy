import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.Person
import art.immeub.rent.pdntcmdls.immeub_pydant as immeub  # pers.Person
import art.immeub.tribs.onproperties.embedded_taxes_on_immeuble_pydant as embed  # embed.EmbeddedImmeubleTax
from art.immeub.rent.create_adhoc_objects.persons_createdata import address1
import art.immeub.rent.pdntcmdls.address_pydant as addr  # addr.PydtcAddress
import lib.dbfs.mngdb.mongo_gen_fetcher as mngfetch


def make_immeuble_ex1():
  owner = pers.fetch_person_by_cpf('12345678143')
  if owner is None:
    errmsg = 'Error: owner not found.'
    raise ValueError(errmsg)
  tenant1 = pers.fetch_person_by_cpf('12345678224')
  tenant2 = pers.fetch_person_by_cpf('12345678496')
  if tenant1 is None or tenant2 is None:
    errmsg = 'Error: tenant(s) not found.'
    raise ValueError(errmsg)
  tenants = [tenant1, tenant2]
  if None in tenants:
    errmsg = 'Error: tenants not found.'
    raise ValueError(errmsg)
  guarantor = pers.fetch_person_by_cpf('12345678305')
  if guarantor is None:
    errmsg = 'Error: guarantor not found.'
    raise ValueError(errmsg)
  tributos = []
  iptu = embed.make_example_iptu_1()
  tributos.append(iptu)
  funesbom = embed.make_example_funesbom_1()
  tributos.append(funesbom)
  address = addr.make_example_address_for_immeub1()
  immeuble = immeub.PydtcImmeuble(
    imm_nickname="CDouto",
    inscr_txincend="1234",
    inscr_munic="12345",
    address=address,
    owners=[owner],
    tributos=tributos,
  )
  print(immeuble)
  return immeuble


def ahdocinstantiate_immeuble_fr_jsondump_example():
  jsondump = """{
    "imm_nickname": "CDouto",
    "inscr_munic": "12345",
    "inscr_txincend": "1234",
    "cartorio_inscr": null,
    "address": {
      "street": "Rio street",
      "number":"67",
      "complement": "apt 101",
      "zipcode": "20222111",
      "neighborhood": "Barra Central"
    },
    "phys_description": "",
    "other_characts": "",
    "tributos": [
      {
        "sigla": "IPTU",
        "descr": "Imposto predial",
        "govlevel": "municipal",
        "payment_year": 2026,
        "yearvalue": "1500",
        "refmonth_beginning": "2026-02-01",
        "opted_monthly": true,
        "n_parcels_if_opt_mon": 10,
        "monthvalue": "160"
      },
      {
        "sigla": "Funesbom",
        "descr": "Taxa de incêndio",
        "govlevel": "estadual",
        "payment_year": 2026,
        "yearvalue": "300",
        "refmonth_beginning": "2026-03-01",
        "opted_monthly": false,
        "n_parcels_if_opt_mon": 1,
        "monthvalue": null
      }
    ],
    "owners_cpfs": [
      "12345678909"
    ]
  }"""
  print('immeub.instantiate_immeuble_fr_jsondump(jsondump)')
  immeuble1 = immeub.PydtcImmeuble.instantiate_from_json_str(jsondump)
  print(immeuble1)
  return immeuble1


def adhoctest1():
  """
  """
  loc1 = make_immeuble_ex1()
  print(loc1)
  model_dumped = loc1.as_json_str()
  print('make_immeuble_ex1() json =>', model_dumped)
  immeuble1 = ahdocinstantiate_immeuble_fr_jsondump_example()
  print(immeuble1.to_json())


def adhoctest2():
  location = make_immeuble_ex1()
  json_str = location.to_json()
  print('json_str', json_str)


def adhoctest3():
  """
  read from localhost MongoDB
  """
  dbname, collname = 'immeub_db', 'immeubles'
  fetcher = mngfetch.GenMongoDBFetcher(dbname=dbname, collname=collname)
  imm_nickname = 'CDouto'
  querydict = {'imm_nickname': imm_nickname}
  print('querydict', querydict)
  docdict = fetcher.find_one_w_querydict_n_collname_as_dict(querydict)
  print('docdict', docdict)
  location = immeub.PydtcImmeuble.instantiate_fr_jsondict(docdict)
  print('location', location)
  jsondump = location.to_json(indent=2)
  print('jsondump location', jsondump)


def adhoctest4():
  immeuble = make_immeuble_ex1()
  print(immeuble)
  json_str = immeuble.to_json(is_for_db=True)
  print('json_str', json_str)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  adhoctest1()
  adhoctest2()
  process()
  """
  adhoctest4()
