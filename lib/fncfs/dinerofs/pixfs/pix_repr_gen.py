"""
lib/fncfs/dinerofs/pixfs/pix_repr_gen.py
  Contains functions to generate Pix QR-code representations.

pip install crcmod qrcode pillow
pip install pixqrcodegen

https://pypi.org/project/pixqrcodegen/
  Gera a Payload do PIX e o QR Code
  pip install pixqrcodegen

https://pypi.org/project/PixPayloadGen/
  Gerar Payload pix com QRCODE
  pip install PixPayloadGen
"""
import qrcode
import crcmod
from PixPayloadGen import PayloadPixGen
import settings as sett


def get_pixdatafolder_abspath():
  """
    Method1: Usando uma biblioteca pronta
        (Mais rápido)
      A forma mais simples é utilizar pacotes já validados
      pela comunidade, como o PixPayloadGen ou o pixqrcode.

      pip install PixPayloadGen qrcode[pil]
      from PixPayloadGen import PayloadPixGen
  """
  datadirpath = sett.get_apps_data_rootdir_abspath() / 'pixes'
  datadirpath.mkdir(exist_ok=True)
  return datadirpath


def meth1():
  """
  Define os dados do pagamento (Valor, Nome do Recebedor, Chave, Cidade, Identificador da Loja)
  O valor deve ser enviado como string com pontos para os centavos (ex: '150.50')
  """
  payload = PayloadPixGen('150.50', 'Fulano de Tal', 'suachave@email.com', 'Rio de Janeiro', 'LOJA01')
  print("Código Copia e Cola gerado com sucesso!")
  # print(PayloadPixGen.QrCodGen(payload))


def gerar_payload_pix(chave, valor, nome_recebedor, cidade, txt_id="***"):
  """
  Method 2: Criando o algoritmo manualmente (Sem pacotes externos de terceiros)
  Caso queira entender a lógica de montagem dos blocos de dados (IDs comerciais da especificação do BACEN) e calcular o código verificador obrigatório (CRC16), use a estrutura abaixo.
  Será necessário instalar apenas o gerador de QR Code e o calculador de CRC16:
  pip install qrcode[pil] crcmod
  """
  # Formata o valor com duas casas decimais
  valor_str = f"{float(valor):.2f}"

  # Montagem dos blocos do padrão EMV / Banco Central
  payload = "000201"  # Payload Format Indicator

  # Informações da conta do recebedor (Chave Pix)
  merchant_account = f"0014BR.GOV.BCB.PIX01{len(chave):02d}{chave}"
  payload += f"26{len(merchant_account):02d}{merchant_account}"

  payload += "52040000"  # Merchant Category Code
  payload += "5303986"  # Transaction Currency (986 = Real)
  payload += f"54{len(valor_str):02d}{valor_str}"  # Valor da transação
  payload += "5802BR"  # Country Code
  payload += f"59{len(nome_recebedor):02d}{nome_recebedor}"  # Nome do beneficiário
  payload += f"60{len(cidade):02d}{cidade}"  # Cidade do beneficiário

  # Campo adicional (ID da transação)
  additional_data = f"05{len(txt_id):02d}{txt_id}"
  payload += f"62{len(additional_data):02d}{additional_data}"

  # Adiciona o início do campo do CRC16
  payload += "6304"

  # Cálculo do CRC16 (CCITT-FALSE)
  crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
  crc16_checksum = hex(crc16_func(payload.encode('utf-8'))).upper()[2:].zfill(4)

  payload_completo = payload + crc16_checksum
  return payload_completo


def example1():
  # 1. Configurar os dados
  chave_pix = "suachave@email.com"
  valor_cobranca = 50.00
  nome = "Fulano de Tal"
  cidade_origem = "Rio de Janeiro"
  # 2. Gerar a string Copia e Cola
  string_pix = gerar_payload_pix(chave_pix, valor_cobranca, nome, cidade_origem)
  print(f"Pix Copia e Cola: {string_pix}")

  # 3. Transformar a string em imagem de QR Code
  qr = qrcode.make(string_pix)
  pngfile = get_pixdatafolder_abspath() / 'pix_com_valor.png'
  qr.save(pngfile)
  scrmsg = f"QR Code as pngfile [{pngfile}] salvo."
  print(scrmsg)


def adhoctest():
  # example1()
  meth1()


if __name__ == "__main__":
  adhoctest()
