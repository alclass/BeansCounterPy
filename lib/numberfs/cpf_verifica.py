#!/usr/bin/env python3
"""
lib/numberfs/cpf_verifica.py
  Calcula ou checa osfs 2 dígitos verificadores do CPF brasileiro
  (sob o "algoritmo módulo 11")

Algoritmo Módulo 11
  É o algoritmo para o cálculo dos 2 dígitos verificadores do CPF
=========

Em duas etapas:

1ª etapa:
=========
1) soma-se a multiplicação de cada um dos 9 primeiros dígitos
por cada um (chamado peso) da sequência decrescente (10 a 2) (*)
  (*) pesos para a 1ª etapa: 10, 9, 8, 7, 6, 5, 4, 3, 2

2) encontra-se o resto na divisão por 11 da soma na 1ª etapa, ou seja:

  resto = soma_etapa1 % 11
    - se o resto for menor que 2, o dígito é 0.
    - caso contrário, subtrai-se o resto de 11 (ou seja, 11 - resto)

2ª etapa:
========

1) anexa-se o resto encontrado na 1ª etapa aos 9 dígitos originais,
   formando agora uma sequência com 10 dígitos;

2) repetem-se osfs passos 1 e 2 da 1ª etapa
   sendo que osfs pesos decrescentes agora começam com 11
  (*) pesos para a 2ª etapa: 11, 10, 9, 8, 7, 6, 5, 4, 3, 2

  ------------------------
  (ver também as funções deste módulo abaixo)
  ------------------------

------------------------
Informações Adicionais:
------------------------

O documento emitido pela Receita Federal possui
   sempre 11 dígitos numéricos, entre osfs quais:

   osfs 8 primeiros: formam a base de cadastro sequencial.
   1 dígito (o nono): indica a Região Fiscal onde o documento foi emitido.
   2 dígitos finais: são osfs dígitos verificadores calculados
     para garantir a segurança e validade do documento.

import copy
"""
import random
from functools import reduce
pesos_passo1 = list(range(10, 1, -1))  # [10, 9, 8, 7, 6, 5, 4, 3, 2]
pesos_passo2 = list(range(11, 1, -1))  # [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
# Reduce step: Sum all squared numberfs -> 1 + 4 + 9 + 16 = 30


def trns_str_elems_to_int_lst(digits):
  """
  May raise TypeError or ValueError that should be 'caught' in the caller
  """
  return list(map(lambda n: int(n), digits))


def raise_if_inconsistent_pre_cpf(p_pre_cpf: str):
  """
  pre-CPF is a 9-digit number that will 'receive' the 2 veriefier-digits
  """
  do_raise = False
  try:
    if len(p_pre_cpf) != 9:
      do_raise = True
    # the next call may raise TypeError or ValueError
    _ = trns_str_elems_to_int_lst(p_pre_cpf)
  except (TypeError, ValueError):
    do_raise = True
  if do_raise:
    errmsg = f"Error: pre-CPF [{p_pre_cpf}] should have 9 numberfs."
    raise ValueError(errmsg)


def raise_if_nonnumbers_in_list_or_str(digits: str):
  """
  Consider this function private,
    i.e., only to be called from within this module

  Obs:
    a) only non-formatted digits should be passed in here;
    b) a formatted (and correct) CPF will 'defeat' this checking here!
    c) in that sense this function should be considered 'private'
  """
  try:
    # the list() executes the map() which may, as it's checked for, raise ValueError
    # without list(), the map() is formed but not executed (intended for checking ValueError)
    _ = list(map(lambda n: int(n), digits))
  except (TypeError, ValueError):
    errmsg = f"Erro: o CPF '{digits}' possui dígitos não-numéricos"
    raise ValueError(errmsg)


def format_cpf(cpf: str, adds_dots=False) -> str:
  """
  Example:
    67289288203 / 672892882-03 or 672.892.882-03
  """
  # TODO pass it to a regex that checks if it's already well-formed
  try:
    cpf = str(cpf)
    if len(cpf) > 11:
      if '-' in cpf or '.' in cpf:
        cpf = cpf.replace('-', '')
        cpf = cpf.replace('.', '')
  except (TypeError, ValueError) as e:
    errmsg = f"Error: cpf {cpf} is not valid. {e}"
    raise ValueError(errmsg)
  if len(cpf) != 11:
    errmsg = f"Erro: cpf {cpf} does not have 11 digits."
    raise ValueError(errmsg)
  t1, t2, t3, dv = cpf[:3], cpf[3:6], cpf[6:9], cpf[-2:]
  dot_or_empty = '.' if adds_dots else ''
  fcpf = f"{t1}{dot_or_empty}{t2}{dot_or_empty}{t3}-{dv}"
  return fcpf


def calc_etapa_cpf_via_reduce(p_digits):
  """
  Calculates [one] (of two) verifier digit from a pre-CPF
    (@see algorithm in the calling function and this one)

  The CPF algorithm runs in 2 rounds:
    r1 for round 1: 9 digits need weights [10, 9, ..., 2]
    r2 for round 2: 10 digits need weights [11, 9, ..., 2]
  The 'arrangement' with list(range(...) treats the two cases above
    weights = list(range(setsize+1, 1, -1))
  """
  digits = trns_str_elems_to_int_lst(p_digits)
  setsize = len(p_digits)
  # list() is not necessary because it will be a parameter in map() below
  weights = range(setsize+1, 1, -1)  # general for each round (1 & 2)
  produtoria = map(lambda x, y: x * y, digits, weights)
  somatoria = reduce(lambda x, y: x + y, produtoria, 0)
  resto = somatoria % 11
  # notice dig_ver is never 10, it ranges from 0 to 9
  dig_ver = 11 - resto if resto > 1 else 0
  return dig_ver


def calcula_triple_cpf_via_reduce(digits9):
  """
  Returns the triple (dv, cpf, format_cpf(cpf))
  In the encompassing module, there are two functions for calculating
    or verifying CPF's: this one uses functools.reduce() for the somatoria part
  """
  raise_if_inconsistent_pre_cpf(digits9)
  # 1st round (1ª etapa)
  dv1 = calc_etapa_cpf_via_reduce(digits9)
  digits10 = digits9 + str(dv1)
  # 2nd round (2ª etapa)
  dv2 = calc_etapa_cpf_via_reduce(digits10)
  dv = f"{dv1}{dv2}"
  cpf = digits9 + dv
  formatted = format_cpf(cpf, True)
  return dv, cpf, formatted


def calc_digito_verificador(digitos: str) -> tuple[int, str]:
  pesos = []
  if len(digitos) == 9:  # para a 1ª etapa
    pesos = pesos_passo1  # no mutation on pesos_passo1 will happen in here
  elif len(digitos) == 10:  # para a 2ª etapa
    pesos = pesos_passo2  # no mutation on pesos_passo2 will happen in here
  parcel = 0  # outra opção: user reduce()
  for i in range(len(digitos)):
    digito = int(digitos[i])
    parcel += digito * pesos[i]
  resto = parcel % 11
  d1 = 0 if resto < 2 else 11 - resto
  # digitos_p_fase2 possui 10 dígitos: osfs 9 originais mais o resto d1
  digitos_mais_resto = digitos + str(d1)
  return d1, digitos_mais_resto


def calc_os_2digitos_verificadores_cpflike(digitos9: str) -> str:
  if digitos9 is None or len(digitos9) != 9:
    errmsg = f"Erro: gerar osfs 2 dígitos verificadores CFP ({digitos9}) necessita de 9 dígitos"
    raise ValueError(errmsg)
  d1, digitos10 = calc_digito_verificador(digitos9)
  d2, _ = calc_digito_verificador(digitos10)
  dv = f"{d1}{d2}"
  return dv


def make_random_11digit_cpf():
  digits9 = map(lambda n: random.randint(0, 9), range(9))
  digits9 = map(lambda n: str(n), digits9)
  digits9 = ''.join(digits9)
  dv = calc_os_2digitos_verificadores_cpflike(digits9)
  cpf = digits9 + dv
  return cpf


def checa_cpf_digitos_verificadores(cpf: str) -> tuple:
  if cpf is None:
    return False, None
  # print(cpf)
  digitos11 = cpf.replace('-', '')
  digitos11 = digitos11.replace('.', '')
  if len(digitos11) != 11:
    errmsg = f"Erro: checar osfs 2 dígitos verificadores CFP ({cpf}) necessita de 11 dígitos"
    raise ValueError(errmsg)
  raise_if_nonnumbers_in_list_or_str(digitos11)
  # print(digitos11)
  digits9 = digitos11[:-2]
  d1, d2 = calc_os_2digitos_verificadores_cpflike(digits9)
  dv = f"{d1}{d2}"
  # print('calculado', dv)
  given_dv = cpf[-2:]
  if dv == given_dv:
    return True, dv
  return False, dv


def calc_verifica_n_print_cpf_verificadores(cpf: str):
  """
  For adhoc-testing
  """
  if cpf is None:
    return None
  answer, dv = checa_cpf_digitos_verificadores(cpf)
  given_dv = cpf[-2:]  # even if it's formatted with dots or dash
  conjun = "" if answer is True else "não "
  word = "[cpf correto] " if answer is True else "[cpf errado] "
  scrmsg = f"""Resultado:
  {word}cpf {cpf} {conjun}possui seus 2 dígitos verificadores corretos.
    => dígitos dados no cpf = {given_dv} | dígitos calculados = {dv}"""
  print(scrmsg)
  return None


def calc_n_print_cpf(word):
  """
  For adhoc-testing
  """
  dv = calc_os_2digitos_verificadores_cpflike(word)
  cpf = f"{word}-{dv}"
  scrmsg = f"Os dígitos {word} possuem DV {dv} formando CPF {cpf} "
  print(scrmsg)


def adhoctest1():
  """
  cpf = "123456789-ab"
  calc_verifica_n_print_cpf_verificadores(cpf)
  cpf = "004623598-16"
  calc_verifica_n_print_cpf_verificadores(cpf)
  cpf = "123456789-09"
  calc_verifica_n_print_cpf_verificadores(cpf)
  print('='*40)
  """
  word = '987654321'
  calc_n_print_cpf(word)
  word = '587523365'
  calc_n_print_cpf(word)
  cpf = make_random_11digit_cpf()
  fcpf = format_cpf(cpf)
  scrmsg = f"{cpf} / {fcpf} <= make_random_11digit_cpf()"
  print(scrmsg)
  # calculate via redude()
  inpt = '987654321'
  dv, cpf, formatted = calcula_triple_cpf_via_reduce(inpt)
  scrmsg = f"{inpt} (via reduce()) => dv={dv} | cpf={cpf} | formatted={formatted}"
  print(scrmsg)
  # calculate via redude()
  inpt = '587523365'
  dv, cpf, formatted = calcula_triple_cpf_via_reduce(inpt)
  scrmsg = f"{inpt} (via reduce()) => dv={dv} | cpf={cpf} | formatted={formatted}"
  print(scrmsg)


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
