#!/usr/bin/python3
"""

Do original em https://github.com/Alexsussa/pixqrcodegen

TODO: separar a classe do módulo em duas.
Uma como "classe de dados".
A outra como "classe geradora".
  Ou, noutra opção, reorganizar os atributos.
"""
import crcmod
import qrcode
import os
import lib.fncfs.dinerofs.pixfs.pix_repr_gen as pgen  # pgen.get_pixdatafolder_abspath


class Payload:

  def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
    self.qrcode = None
    self.payload = None
    self.crc16code = None
    self.nome = nome
    self.chavepix = chavepix
    self.valor = valor.replace(',', '.')
    self.cidade = cidade
    self.txtId = txtId
    self.diretorio_qr_code = diretorio or None
    self.nome_tam = len(self.nome)
    self.chavepix_tam = len(self.chavepix)
    self.valor_tam = len(self.valor)
    self.cidade_tam = len(self.cidade)
    self.txtId_tam = len(self.txtId)
    self.merchant_account_tam = f'0014BR.GOV.BCB.PIX01{self.chavepix_tam:02}{self.chavepix}'
    self.transaction_amount_tam = f'{self.valor_tam:02}{float(self.valor):.2f}'
    self.add_data_field_tam = f'05{self.txtId_tam:02}{self.txtId}'
    self.nome_tam = f'{self.nome_tam:02}'
    self.cidade_tam = f'{self.cidade_tam:02}'
    self.payload_format = '000201'
    self.merchant_account = f'26{len(self.merchant_account_tam):02}{self.merchant_account_tam}'
    self.merchantCategCode = '52040000'
    self.transactionCurrency = '5303986'
    self.transactionAmount = f'54{self.transaction_amount_tam}'
    self.countryCode = '5802BR'
    self.merchantName = f'59{self.nome_tam:02}{self.nome}'
    self.merchantCity = f'60{self.cidade_tam:02}{self.cidade}'
    self.addDataField = f'62{len(self.add_data_field_tam):02}{self.add_data_field_tam}'
    self.crc16 = '6304'

  def gerar_payload(self):
    self.payload = (
        f'{self.payload_format}{self.merchant_account}'
        f'{self.merchantCategCode}{self.transactionCurrency}'
        f'{self.transactionAmount}{self.countryCode}{self.merchantName}'
        f'{self.merchantCity}{self.addDataField}{self.crc16}'
    )
    self.gerar_crc16(self.payload)

  def gerar_crc16(self, payload):
    crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
    self.crc16code = hex(crc16(str(payload).encode('utf-8')))
    self.crc16Code_formatado = str(self.crc16code).replace('0x', '').upper().zfill(4)
    self.payload_completa = f'{payload}{self.crc16Code_formatado}'
    self.gerar_qr_code(self.payload_completa, self.diretorio_qr_code)

  def gerar_qr_code(self, payload, diretorio):
    """
    dir = os.path.expanduser(diretorio)
    """
    self.qrcode = qrcode.make(payload)
    datadirpath = pgen.get_pixdatafolder_abspath()
    self.diretorio_qr_code = self.diretorio_qr_code or datadirpath
    pngfile = self.diretorio_qr_code / 'pixqrcodegen.png'
    self.qrcode.save(pngfile)
    scrmsg = f'gerado QR-Code em [{pngfile}]'
    print(scrmsg)
    print(payload)


if __name__ == '__main__':
  # 12345678900 seria o formato do CPF sem pontos e traços
  pl = Payload('Nome Sobrenome', '12345678900', '1.00', 'Cidade Ficticia', 'LOJA01')
  pl.gerar_payload()
