"""
art/immeub/rent/testdata/persons_createdata.py

"""
import typing
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


def make_example_person_w_name_cpfd9_email_pix(
  nomecompleto: str, cpf_d9: str,
  email: str, chavepix: typing.Optional[str],
  ) -> pers.PydtcPerson:
  _, cpf, _ = ccpf.calc_cpf_ret_dv_cpf_cpffmt_via_reduce_w_d9(cpf_d9)
  person = pers.PydtcPerson(
    nomecompleto=nomecompleto,
    cpf=cpf,
    emails=[email],
    chavepix=chavepix,
  )
  return person


def make_example_owner_123456781() -> pers.PydtcPerson:
  cpf_d9 = '123456781'
  fullname = "Luiz Lewis"
  email = 'livrosetc@yahoo.com.br'
  chavepix = email
  return make_example_person_w_name_cpfd9_email_pix(
    nomecompleto=fullname, cpf_d9=cpf_d9, email=email, chavepix=chavepix
  )


def make_example_tenant1_w_cpf_123456782():
  cpf_d9 = '123456782'
  fullname = "John Doe"
  email = 'john.doe@gmail.com'
  chavepix = email
  person = make_example_person_w_name_cpfd9_email_pix(
    nomecompleto=fullname, cpf_d9=cpf_d9, email=email, chavepix=chavepix
  )
  address = addr.make_example_address_1()
  person.address = address
  person.birthcity = "Niterói - RJ"
  person.birthdate = mkrm("1970-01-01")
  person.phonenumbers = ["99992222"]
  return person


def make_example_guarantor_w_cpf_123456783() -> pers.PydtcPerson:
  cpf_d9 = '123456783'
  fullname = "Stephan Warrants"
  email = 'stephan.warrants@gmail.com'
  chavepix = email
  person = make_example_person_w_name_cpfd9_email_pix(
    nomecompleto=fullname, cpf_d9=cpf_d9, email=email, chavepix=chavepix
  )
  address = addr.make_example_address_1()
  person.address = address
  person.birthcity = "Saquarema - RJ"
  person.birthdate = mkrm("1975-01-01")
  person.phonenumbers = ["99994444"]
  return person


def make_example_tentant2_w_cpf_123456784() -> pers.PydtcPerson:
  address = addr.make_example_address_1()
  cpf_d9 = '123456784'
  _, cpf, _ = ccpf.calc_cpf_ret_dv_cpf_cpffmt_via_reduce_w_d9(cpf_d9)
  person = pers.PydtcPerson(
    nomecompleto="Mary Mariah",
    cpf=cpf,
    address=address,
    birthcity="Niterói - RJ",
    birthdate=mkrm("1980-01-01"),
    phonenumbers=["99991111"],
    emails=["marymariah@example.com"],
    marital_st="C",
    docum_id="1234567",
  )
  return person


def adhoctest1():
  """
  """
  person = make_example_tentant2_w_cpf_123456784()
  print(person)
  person_jsondump = person.to_json(indent=2)
  print('to json str =>', person_jsondump)
  obj = pers.PydtcPerson.instantiate_fr_jsonstr(person_jsondump)
  print('back from json str =>', obj)


def adhoctest2():
  persons_as_json = []
  # owner
  person = make_example_owner_123456781()
  json_str = person.to_json(indent=2, is_for_db=True)
  persons_as_json.append(json_str)
  print('ower to json str =>', json_str)
  # tenant 1
  person = make_example_tenant1_w_cpf_123456782()
  json_str = person.to_json(indent=2, is_for_db=True)
  persons_as_json.append(json_str)
  print('tenant to json str =>', json_str)
  # guarantor 1
  person = make_example_guarantor_w_cpf_123456783()
  json_str = person.to_json(indent=2, is_for_db=True)
  persons_as_json.append(json_str)
  print('guarantor to json str =>', json_str)
  # tenant 2
  person = make_example_tentant2_w_cpf_123456784()
  json_str = person.to_json(indent=2, is_for_db=True)
  persons_as_json.append(json_str)
  print('tenant 2 to json str =>', json_str)
  str_rule = '=' * 55
  print(str_rule)
  print(str_rule)
  jsontext = ', '.join(persons_as_json)
  jsontext = f"[{jsontext}]"
  print(jsontext)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  adhoctest1()
  process()
  """
  adhoctest2()
