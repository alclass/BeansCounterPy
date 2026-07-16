"""
lib/finfs/indices/indices_fetch_n_fs.py

import lib.finfs.indices.indices_fetch_n_fs as ipfs  # ipfs.ipca_for_refmonth
"""
import lib.finfs.indices.ipca_data as ipca
import lib.finfs.indices as init
IPCA = init.IPCA


def get_ir_incrfactor_for_mora_w_iridx_n_expo(ir_idx, exponent):
  """
  Returns the multiplier for the (mora) Interest Rate (ir) calculation
    based on an index (ir_idx) and an exponent
    (this is independent on the duration time or cycle, which might be anyone in the caller)
  """
  intermediate = (1 + ir_idx) ** exponent
  multiplier = intermediate - 1
  return multiplier


def find_corrmonet_for_month(refmonth, idxname):
  if idxname == IPCA:
    return ipca_for_refmonth(refmonth)
  return None


def ipca_for_refmonth(refmonth):
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
