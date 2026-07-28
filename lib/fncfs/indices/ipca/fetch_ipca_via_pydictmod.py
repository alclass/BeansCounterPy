

def find_ipca_corrmonet_for_month_via_pyfile(refmonth, idxname):
  if idxname == IPCA:
    return get_ipca_for_refmonth_via_pyfile(refmonth)
  return None


def get_ipca_for_refmonth_via_pyfile(refmonth):
  """
  A série histórico pode ser baixada xls-zipada de:
    https://ftp.ibge.gov.br/Precos_Indices_de_Precos_ao_Consumidor/IPCA/Serie_Historica/ipca_SerieHist.zip
  """
  year = refmonth.year
  month = refmonth.month
  monthly_indices = ipca.data_2019_2026[year]
  idx = monthly_indices[month-1]
  # idx is represented as %, so it's needed to divide it by 100
  idx = idx / 100
  return idx
