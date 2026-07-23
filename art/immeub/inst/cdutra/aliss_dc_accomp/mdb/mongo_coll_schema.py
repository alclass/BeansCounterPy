"""
art/immeub/inst/cdutra/aliss_dc_accomp/mdb/mongo_coll_schema.py
"""
import datetime
import lib.datesetc.datefs as dtfs



def adhoctest1():
  """
  d = Decimal(1/3)
  # d.remainder_near()
  print(d)
  """
  today = datetime.date.today()
  strdate = today.strftime("%Y-%m-%d")
  print(strdate)
  pdate = dtfs.make_date_or_raise('2026-3-2')
  # strdate = dtfs.datetostr(pdate)
  strdate = pdate.strftime("%Y-%m-%d")
  print(strdate)



def process():
  """
  """
  get_months_closings_w_dictdata()


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
