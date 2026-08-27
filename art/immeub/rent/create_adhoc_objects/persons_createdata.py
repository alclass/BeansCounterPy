"""
art/immeub/rent/testdata/persons_createdata.py

"""
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.PydtcPerson(...)
import lib.datesetc.refmonth_fs as rmfs
import art.immeub.rent.pdntcmdls.address_pydant as addr  # addr.PydtcAddress
import lib.numberfs.cpf_verifica as ccpf  # ccpf.calc_cpf_ret_dv_cpf_cpffmt_via_reduce_w_d9
mkrm = rmfs.make_refmonth_or_raise
address1 = addr.PydtcAddress(
  street="Rio street s/n",
  number="s/n",
  zipcode="22333111",
  neighborhood="Barra Central",
)


def make_person_example_1():
  address = addr.make_example_address_1()
  cpf1_d9 = '123456789'
  _, cpf, _ = ccpf.calc_cpf_ret_dv_cpf_cpffmt_via_reduce_w_d9(cpf1_d9)
  person = pers.PydtcPerson(
    nomecompleto="John Doe",
    cpf=cpf,
    address=address,
    birthcity="Niterói",
    birthdate=mkrm("1970-01-01"),
    phonenumbers=["99991111"],
    emails=["johndoe@example.com"],
    marital_st="S",
    docum_id="1234567",
  )
  return person


def adhoctest1():
  """
  """
  person = make_person_example_1()
  print(person)
  person_jsondump = person.to_json(indent=2)
  print('to json str =>', person_jsondump)
  obj = pers.PydtcPerson.instantiate_fr_jsonstr(person_jsondump)
  print('back from json str =>', obj)


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
