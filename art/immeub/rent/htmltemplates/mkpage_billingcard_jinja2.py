"""
art/immeub/rent/htmltemplates/mkpage_billingcard_jinja2.py

"""
from jinja2 import Environment, FileSystemLoader
import jinja2
import settings as sett
from pathlib import Path
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.
import art.immeub.rent.pdntcmdls.rentcontract_pydant as rentm  # pers.
import art.immeub.rent.billmodels.billingcard_pydantic as bcm  # bcm.
import art.immeub.rent.create_adhoc_objects.billingcards_createdata as creatbc  # creatbc.make_billingcard2
# Set up the template environment to load files from the current directory
middlepath = "js/templates/jinjatemplates"
appsrootfolder = Path(sett.APP_ROOTFOLDER)
templates_abspath = appsrootfolder / middlepath
templatefilename = 'billingcard_customjs.j2.html'
templatefile = templates_abspath / templatefilename


def get_template() -> jinja2.Template:
  # 1. Initialize the environment with FileSystemLoader
  env = Environment(loader=FileSystemLoader(templates_abspath))
  # 2. Target file as a Path object
  file_path = templatefile
  # 3. Make path relative to the loader directory and convert to string
  print('file_path', file_path)
  print('templates_abspath', templates_abspath)
  pathrelativeto = file_path.relative_to(templates_abspath).as_posix()
  print('pathrelativeto', pathrelativeto)
  relative_template_path = pathrelativeto
  # 4. Load the template successfully
  template = env.get_template(relative_template_path)
  return template


def render_html(billingcard) -> None:
  """
  To import it:
    import art.immeub.rent.htmltemplates.jinja2_adhoctest1 as jj2  # jj2.render_html()
  """
  template = get_template()
  rendered_html = template.render(bc=billingcard)
  outputfile = templates_abspath / "output_billingcard.html"
  # Save the generated content to a new HTML file
  with open(outputfile, "w", encoding="utf-8") as f:
    f.write(rendered_html)
  scrmsg = f"HTML file generated successfully as '{outputfile}'!"
  print(scrmsg)


def jinjarender_example_rentcontract() -> None:
  contrnumber = 'CDouto202401'
  billingcard = creatbc.make_billingcard2()
  if billingcard is None:
    scrmsg = f"billingcard {billingcard} not found!"
    print(scrmsg)
    return
  print('Render billingcard to Jinja')
  render_html(billingcard)


def adhoctest1() -> None:
  jinjarender_example_rentcontract()


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
