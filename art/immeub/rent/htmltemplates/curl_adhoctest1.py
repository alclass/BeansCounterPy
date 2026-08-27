import os
curl_comm = """
curl -X POST 'https://e.customjs.io/html2pdf' \
  -H 'Content-Type: application/json' \
  -H 'x-api-key: YOUR_API_KEY' \
  -H 'customjs-origin: inline/pdf-generator' \
  -d '{"input":{"issuer":{"companyName":"Company Name","address":"Address","taxId":"Tax ID","phone":"Phone","email":"Email","payment":{"accountNumber":"","BIC":"","bankName":"","referencePrefix":"INV-"},"logoUrl":"https://zapier-images.imgix.net/storage/developer_cli/6f3096e904d8168587ad67f1219f2c0e.png"},"recipient":{"name":"Your Client Name","address":"Address","taxId":"Tax ID"},"billing":{"invoiceNumber":"INV-12","invoiceDate":"2025-10-24","dueDate":"2025-10-24","currency":"EUR","taxRate":19,"notes":"It was a pleasure doing business with you."},"items":[{"description":"Enter item name or description","quantity":1,"unitPrice":100},{"description":"Enter item name or description","quantity":1,"unitPrice":100}]},"code":"const { HTML2PDF } = require('\''./utils'\''); const nunjucks = require('\''nunjucks'\''); const fetch = require('\''node-fetch'\''); const tpl = '\''https://www.customjs.space/pdf-templates/Invoice1.html'\''; const templateString = await fetch(tpl).then(r => r.text()); const renderedHtml = nunjucks.renderString(templateString, { invoiceData: JSON.stringify(input) }); return HTML2PDF(renderedHtml);","returnBinary":"true"}' \
  > customjs-output.pdf
"""
print(curl_comm)
os.system(curl_comm)