#!/usr/bin/env python3
"""
lib/finfs/indices/ipca/ipca_api_fetcher.py

from datetime import datetime
"""
import datetime
import decimal
import json
from pathlib import Path
import urllib.parse
import urllib.request
import lib.datesetc.datefs as dtfs
import lib.datesetc.refmonth_fs as rmfs
import lib.finfs.indices.ipca as init  # init.get_ipca_datadir()
from lib.datesetc.refmonth_fs import make_refmonth_or_raise, make_current_refmonth
# Código da série do IPCA mensal no Banco Central
COD_SERIE_IPCA = 433
BCB_API_URL_INTERPOL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_serie}/dados?{params_enc_fmt_n_ini_fim}"
# IPCA_JSONFILE_INTERPOL = "ipca_{refmonth7chars}.json"
IPCA_JSONFILE_INTERPOL = "ipca_{year}.json"


def does_jsonfile_for_year_ipcas_exist(year: int) -> bool:
  json_filename = init.YEARLY_JSON_FILENAME_INTERPOL.format(year=year)
  ipca_dirpath = init.get_ipca_datadir()
  json_filenpath = ipca_dirpath / json_filename
  return json_filenpath.is_file()

def write_jsonresponse_within_dates_to(json_res: str, dates: tuple[datetime.date, datetime.date]) -> None:
  """
  This 'formulation' is no longer used.
  """
  inidate, findate = dates[0], dates[1]
  sinidate, sfindate = inidate.strftime("%Y-%m-%d"), findate.strftime("%Y-%m-%d")
  filename = f"ipca-{sinidate}_{sfindate}.json"
  ipca_dirpath = init.get_ipca_datadir_on_year(inidate.year)
  filepath = ipca_dirpath / filename
  with open(filepath, 'w') as outfile:
    outfile.write(json_res)
    # outfile.close()  # it closes when exiting from the with-block


def write_jsonresponse_for_year_to_cnvfile(json_res: str, p_year: int) -> Path:
  """
  Writes jsonresponse for year <year> to the "conventioned" file
  """
  year = int(p_year)
  json_filename = init.YEARLY_JSON_FILENAME_INTERPOL.format(year=year)
  print('Writing to ', json_filename)
  ipca_dirpath = init.get_ipca_datadir()
  if not ipca_dirpath.is_dir():
    scrmsg = f"Creating directory {ipca_dirpath}"
    print(scrmsg)
    ipca_dirpath.mkdir(parents=True, exist_ok=True)
  years_ipca_filepath = ipca_dirpath / json_filename
  with open(years_ipca_filepath, 'w') as outfile:
    outfile.write(json_res)
    # outfile.close()  # it closes when exiting from the with-block
  return years_ipca_filepath


def fetch_ipca_for_years(yearini=2025, yearfin=2026):
  for year in range(yearini, yearfin):
    store_monthly_ipcas_to_jsonfile_for_year(year)


def confirm_going_to_fetch_n_store_ipcas_for_year(year) -> bool:
  scrmsg = f"Accept going to fetch json content for writing {year}'s file ? (Y/n) [ENTER] means Yes"
  answer = input(scrmsg)
  if answer not in ["Y", 'y', '']:
    return False
  return True


def confirm_filewritting_jsoncontent_ipcas_for_year(year, json_content) -> bool:
  print(json_content)
  print('='*50)
  scrmsg = f"Accept writing json content above into {year}'s file ? (Y/n) [ENTER] means Yes"
  answer = input(scrmsg)
  if answer not in ["Y", 'y', '']:
    return False
  return True


def fetch_n_store_ipcas_in_current_year_uptilnow() -> Path | None:
  """
  API-fetches yearly IPCA indices for the 'current year' and stores/caches them to a local JSON file.
  """
  today = datetime.date.today()
  current_year = today.year
  if not confirm_going_to_fetch_n_store_ipcas_for_year(current_year):
    return None
  current_refmonth = make_current_refmonth()
  month_minus_n = 1
  upto_refmonth = rmfs.make_refmonth_it_minus_n_or_raise(current_refmonth, month_minus_n)
  str_first_refmonth_in_year = f"{current_year}-01"
  first_refmonth_in_year = make_refmonth_or_raise(str_first_refmonth_in_year)
  json_content = bcb_api_fetch_monthly_ipcas_between(first_refmonth_in_year, upto_refmonth)
  if not confirm_filewritting_jsoncontent_ipcas_for_year(current_year, json_content):
    print('Not writing file, returning.')
    return None
  writtenfile = write_jsonresponse_for_year_to_cnvfile(json_content, current_year)
  scrmsg = f"""fetch_n_store_ipcas_in_current_year_uptilnow()
  => year {current_year} -> {first_refmonth_in_year} to {upto_refmonth}"
  in file = {writtenfile}
  """
  print(scrmsg)
  return writtenfile


def store_monthly_ipcas_to_jsonfile_for_year(year: int):
  """
  API-fetches yearly IPCA indices for a given year and stores/caches them to a local JSON file.

  inirefmonth = rmfs.make_refmonth_or_raise('2026-01')
  finrefmonth = rmfs.make_refmonth_or_raise('2026-12')
  for refmonth in rmfs.generate_monthrange(inirefmonth, finrefmonth):

  """
  inirefmonth, finrefmonth = rmfs.make_refmonthtuple_w_year_or_currentyear(year)
  jsondump = bcb_api_fetch_monthly_ipcas_between(inirefmonth, finrefmonth)
  years_ipca_filepath = write_jsonresponse_for_year_to_cnvfile(jsondump, year)
  scrmsg = f"""store_ipca_to_jsonfile_for_year()
  => year {year} - {inirefmonth} - {finrefmonth}"
  in file = {years_ipca_filepath}
  """
  print(scrmsg)


def read_ipca_fr_jsonfile_for_refmonth_via_jsonfile(refmonth: datetime.date) -> decimal.Decimal | None:
  """
  This function is not needed anymore because data was grouped by year, not refmonth
  """
  refmonth7chars = refmonth.strftime("%Y-%m")
  interpol_rm_dict = {'refmonth7chars': refmonth7chars}
  ipca_jsonfilename = IPCA_JSONFILE_INTERPOL.format(**interpol_rm_dict)
  ipca_dirpath = init.get_ipca_datadir_on_year(refmonth.year)
  ipca_jsonfile = ipca_dirpath / ipca_jsonfilename
  datadictlist = json.load(open(ipca_jsonfile))
  if len(datadictlist) > 0:
    datadict = datadictlist[0]
    value = datadict['valor']
    months_idx = decimal.Decimal(value)
    return months_idx
  return None


def get_year_monthly_ipcas_pct_via_jsonfile(year: int) -> dict[datetime.date, decimal.Decimal] | None:
  """
  lib.finfs.indices.ipca.ipca_api_fetcher.read_n_get_json_ipca_monthlyindices_via_file_for_year

  """
  ipca_jsonfilename = f"ipca-{year}.json"
  data_dirpath = init.get_ipca_datadir()
  ipca_jsonfile = data_dirpath / ipca_jsonfilename
  if not ipca_jsonfile.is_file():
    return None
  try:
    datadictlist = json.load(open(ipca_jsonfile))
    ret_dict = {}
    for datadict in datadictlist:
      strdate = datadict['data']
      pdate = dtfs.transform_strdate_ddmmyyyy_to_date_sep_by(strdate, '/')
      if pdate is None:
        errmsg = f"Error: pdate [{pdate}] not found in file [{ipca_jsonfilename}]"
        raise ValueError(errmsg)
      ipca_idx = datadict['valor']
      months_idx = decimal.Decimal(ipca_idx)
      ret_dict[pdate] = months_idx
    return ret_dict
  except OSError:
    return None
  # return {}


def bcb_api_fetch_monthly_ipcas_between(inidate, findate) -> str:
  """Busca o IPCA mensal no site do Banco Central por intervalo de datas.

  IMPORTANT ('ipca percent' versus 'ipca decimal'):
    i1 - the API-fetched values are percent ones, so they must be divided by 100 'downstream'
    i2 - at the current version, the fetched values are 'cached' in local JSON files
    i3 - when then fetched from the local JSON files, for use,
         this system uses ipca 'decimal' instead of 'percented'

  URL Exemplo:
    (para obter índices IPCA entre 1/4/2026 e 30/6/2026) (escrito em 2026-07-25)
    https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?
      formato=json&dataInicial=01%2F04%2F2026&dataFinal=30%2F06%2F2026

  JSON Response:
     [
      {"data":"01/04/2026","valor":"0.67"},
      {"data":"01/05/2026","valor":"0.58"},
      {"data":"01/06/2026","valor":"0.16"}
      ]

  Quando visto por navegador, o retorno-JSON de quando se pede um mês-índice ainda não apurado é:
    {
      "erro":
        {
          "statusCode":404,
          "detail":"br.gov.bcb.pec.sgs.comum.excecoes.SGSNegocioException: Value(s) not found"
        }
    }
  Quando visto programaticamente (por aqui), o retorno-JSON de quando se pede um mês-índice ainda não apurado é:
    {"erro": "Falha na conex\u00e3o: HTTP Error 404: Not Found"}

  De uma forma ou de outra, obtém-se o "erro 404 Not Found".

  Args (to this enclosing function):
    inidate (datetime.date): Data inicial
    findate (datetime.datestr): Data final

  Args (to the API):
    data_inicio (str): Data inicial no formato 'DD/MM/AAAA'
    data_fim (str): Data final no formato 'DD/MM/AAAA'

  Returns:
    str: String JSON com os valores encontrados
  """
  data_inicio, data_fim = inidate.strftime("%d/%m/%Y"), findate.strftime("%d/%m/%Y")
  # Sanitização e encoding dos parâmetros de data para a URL
  params_enc_fmt_n_ini_fim = urllib.parse.urlencode(
      {
        "formato": "json",
        "dataInicial": data_inicio,
        "dataFinal": data_fim,
      }
  )
  # Código da série do IPCA mensal no Banco Central
  codigo_serie = COD_SERIE_IPCA
  paramsdict = {'codigo_serie': codigo_serie, 'params_enc_fmt_n_ini_fim': params_enc_fmt_n_ini_fim}
  url = BCB_API_URL_INTERPOL.format(**paramsdict)
  scrmsg = f"Calling BCB (IPCA) API's url: {url}"
  print(scrmsg)
  try:
    # Executa a requisição HTTP GET
    with urllib.request.urlopen(url) as response:
      if response.status == 200:
        json_res = response.read().decode("utf-8")
        # Converte para objeto Python e reordena/formata se necessário
        dados_json = json.loads(json_res)
        # Retorna como string JSON formatada (pretty print)
        return json.dumps(dados_json, indent=2, ensure_ascii=False)
      else:
        return json.dumps(
          {"erro": f"Erro na API. Status: {response.status}"}
        )
  except Exception as e:
    return json.dumps({"erro": f"Falha na conexão: {str(e)}"})


def adhoctest1():
  """
  inicio = "01/04/2026"
  fim = "30/06/2026"

  # --- Exemplo de Uso ---
  # Define o período desejado
  bra_dt_fmt = "%d/%m/%Y"
  """
  mkdt_fn = dtfs.make_date_or_raise
  inidate, findate = '2026-7-1', '2026-7-23'
  inidate, findate = mkdt_fn(inidate), mkdt_fn(findate)
  print(f"Buscando IPCA de {inicio} até {fim}...\n")
  resultado_json = bcb_api_fetch_monthly_ipcas_between(inidate, findate)
  # resultado_json  = 'resultado_json'
  print(resultado_json)


def adhoctest2():
  """
  fetch_ipca_for_years()
  fetch_ipca_curyear_uptilnow()
  """
  pass


def process():
  """
  Calls the function that updates the monthly IPCA's for the current year.
    The user should accept/confer/confirm the screen-display
      to check that the year's JSON content may be file-written or not.
    It's an easy check because when an error returns,
      it's easily identified and the user should not confirm it if it either contains an error or is empty.

  TODO this checking might be automated in the future.
  """
  fetch_n_store_ipcas_in_current_year_uptilnow()


if __name__ == '__main__':
  """
  adhoctest1()
  adhoctest2()
  """
  process()
  adhoctest1()
