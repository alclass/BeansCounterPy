"""
lib/datesetc/adhoctests/adhoc_calc_months_elapsed_inbetween_dates.py
  adhoc-inputs for testing adhoc_calc_months_elapsed_inbetween_dates
"""
import lib.datesetc.rmfs as rmfs  # refmonth_fs.py.months_inbetween_ret_int_n_float


def adhoctest1():
  """
  Contains 7 input sets:
    is1: inidate, findate = "2026-01-01", "2026-01-31"
    is2: inidate, findate = "2026-01-01", "2026-02-01"
  """
  # is1: inidate, findate = "2026-01-01", "2026-01-31"
  inidate, findate = "2026-01-01", "2026-01-31"
  retval = rmfs.months_inbetween_return_int_n_float(inidate, findate)
  # the returned typle should be (1, 0) i.e., one month and no fractions
  inputset = 1
  prefix = f"inputset-{inputset}"
  print(prefix, inidate, findate, retval)
  # is2: inidate, findate = "2026-01-01", "2026-02-01"
  # ======================
  inidate, findate = "2026-01-01", "2026-02-01"
  retval = rmfs.months_inbetween_return_int_n_float(inidate, findate)
  # the returned typle should be (2, 0) i.e., two months and no fractions
  inputset += 1
  prefix = f"inputset-{inputset}"
  print(prefix, inidate, findate, retval)
  # is3: inidate, findate = "2026-01-01", "2026-04-15"
  # ======================
  inidate, findate = "2026-04-01", "2026-04-15"
  retval = rmfs.months_inbetween_return_int_n_float(inidate, findate)
  # the returned typle should be (0, 0.5) i.e., no months and a fraction as 1/2
  inputset += 1
  prefix = f"inputset-{inputset}"
  print(prefix, inidate, findate, retval)
  # is4: inidate, findate = "2026-04-10", "2026-04-20"
  # ======================
  inidate, findate = "2026-04-10", "2026-04-20"
  retval = rmfs.months_inbetween_return_int_n_float(inidate, findate)
  # the returned typle should be (3, 0.5) i.e., no months and a fraction as 1/2
  inputset += 1
  prefix = f"inputset-{inputset}"
  print(prefix, inidate, findate, retval)
  # is5: inidate, findate = "2025-01-01", "2025-05-20"
  # ======================
  inidate, findate = "2025-01-01", "2025-12-31"
  retval = rmfs.months_inbetween_return_int_n_float(inidate, findate)
  # the returned typle should be (12, 0) i.e., no months and a fraction as 1/2
  inputset += 1
  prefix = f"inputset-{inputset}"
  print(prefix, inidate, findate, retval)
  # is6: inidate, findate = "2027-03-10", "2027-04-09"
  # ======================
  inidate, findate = "2027-03-10", "2027-04-10"
  retval = rmfs.months_inbetween_return_int_n_float(inidate, findate)
  # the returned typle should be (3, 1/3) i.e., no months and a fraction as 1/2
  inputset += 1
  prefix = f"inputset-{inputset}"
  print(prefix, inidate, findate, retval)


def adhoctest2():
  """
  Example:
    input:
      inidate = "2026-01-10"
      findate = "2026-04-07"
  """
  inidate = "2026-01-10"
  findate = "2026-04-07"
  print(inidate, findate)
  ndayslist = rmfs.partition_monthlydays_wi_monthrange(inidate, findate)
  print(ndayslist)
  refmonths = rmfs.find_dateborders_fr_ndayslist_n_refmonths(ndayslist, inidate, findate)
  print(refmonths)
  tuplelist = rmfs.mount_ndays_n_refmonth_tuplelist(inidate, findate)
  for tupl in tuplelist:
    print(tupl)


def process():
  """

  """
  pass


if __name__ == "__main__":
  """
  process()
  adhoctest1()
  """
  adhoctest2()
