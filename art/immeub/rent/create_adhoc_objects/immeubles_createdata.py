import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.Person
import art.immeub.rent.pdntcmdls.immeub_pydant as immeub  # pers.Person
import art.immeub.tribs.onproperties.embedded_taxes_on_immeuble as embed  # embed.EmbeddedImmeubleTax
from art.immeub.rent.create_adhoc_objects.persons_createdata import address1
import art.immeub.rent.pdntcmdls.address_pydantic as addr  # addr.PydtcAddress


def make_immeuble_ex1():
  persons = pers.get_persons_by_cpfs([])
  tributos = []
  iptu = embed.make_example_iptu_1()
  tributos.append(iptu)
  funesbom = embed.make_example_funesbom_1()
  tributos.append(funesbom)
  address = addr.make_example_address_1()
  immeuble = immeub.PydtcImmeuble(
    imm_nickname="CDouto",
    inscr_txincend="1234",
    inscr_munic="12345",
    address=address,
    owners=persons,
    tributos=tributos,
  )
  print(immeuble)
  return immeuble


def instantiate_immeuble_fr_jsondump():
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
  immeuble1 = immeub.PydtcImmeuble.instantiate_from_jsondict(jsondump)
  print(immeuble1)
  return immeuble1


def adhoctest1():
  """
  """
  loc1 = make_immeuble_ex1()
  print(loc1)
  model_dumped = loc1.asdict()
  print('make_immeuble_ex1() json =>', model_dumped)


def adhoctest2():
  print('instantiate_immeuble_fr_jsondump')
  immeuble1 = instantiate_immeuble_fr_jsondump()
  print(immeuble1.asdict())


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest2()
  adhoctest1()