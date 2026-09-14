import qrcode

# Dados básicos do Pix
chave_pix = "sua-chave-pix-aqui"
nome_recebedor = "Seu Nome"
cidade_recebedor = "Sua Cidade"
valor = "10.00"  # Opcional, deixe vazio se não houver valor fixo
identificador = "PEDIDO123"


# Função simples para formatar o padrão EMV do Pix (BR Code)
def monta_campo(id_campo, valor_campo):
    tamanho = f"{len(valor_campo):02d}"
    return f"{id_campo}{tamanho}{valor_campo}"

# Montagem simplificada do payload Pix
# ID 00: Payload Format Indicator, ID 26: Merchant Account Information, etc.
gui = monta_campo("00", "br.gov.bcb.pix")
chave = monta_campo("01", chave_pix)
merchant_account = monta_campo("26", gui + chave)

payload_format = monta_campo("00", "01")
categoria = monta_campo("52", "0000")
moeda = monta_campo("53", "986") # Real brasileiro
val_campo = monta_campo("54", valor) if valor else ""
pais = monta_campo("58", "BR")
nome = monta_campo("59", nome_recebedor)
cidade = monta_campo("60", cidade_recebedor)
additional_data = monta_campo("62", monta_campo("05", identificador))

# Juntando os campos sem o CRC16 (para testes básicos)
payload_parcial = (
    payload_format +
    merchant_account +
    categoria +
    moeda +
    val_campo +
    pais +
    nome +
    cidade +
    additional_data +
    "6304"  # Prefixo do CRC16
)

print("Payload Copia e Cola:", payload_parcial)

# Gerando a imagem do QR Code
img = qrcode.make(payload_parcial)
# img.save("qrcode_pix.png")
print("QR Code salvo como qrcode_pix.png")
