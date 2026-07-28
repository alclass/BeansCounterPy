"""
https://www.ipeadata.gov.br/api/

"""
odata4 = """
{
  "@odata.context":"http://ipeadata.gov.br/api/odata4/$metadata","value":[
    {
      "name":"Paises","kind":"EntitySet","url":"Paises"
    },{
      "name":"Metadados","kind":"EntitySet","url":"Metadados"
    },{
      "name":"Temas","kind":"EntitySet","url":"Temas"
    },{
      "name":"Territorios","kind":"EntitySet","url":"Territorios"
    },{
      "name":"Valores","kind":"EntitySet","url":"Valores"
    },{
      "name":"ValoresStr","kind":"EntitySet","url":"ValoresStr"
    }
  ]
}
"""
url = "http://www.ipeadata.gov.br/api/odata4/"
pass
