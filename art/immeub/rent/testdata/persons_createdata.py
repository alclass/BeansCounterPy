"""
art/immeub/rent/testdata/persons_createdata.py

"""
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.PydtcPerson(...)
import lib.datesetc.refmonth_fs as rmfs
address_1 = [
  "Rio street s/n",
  "22333111 - Barra Central",
]


def make_person_example_1():
  mkrm = rmfs.make_refmonth_or_raise
  person = pers.PydtcPerson(
    nomecompleto="John Doe",
    cpf="12345678909",
    city="Rio de Janeiro",
    birthcity="Niterói",
    birthdate=mkrm("1970-01-01"),
    phonenumbers=["99991111"],
    emails=["johndoe@example.com"],
    marital_st="S",
    docum_id="1234567",
    address=address_1,
  )
  return person


def adhoctest1():
  """
  """
  person = make_person_example_1()
  print(person)
  jsondump = person.model_dump_json(indent=2)
  print(jsondump)


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
