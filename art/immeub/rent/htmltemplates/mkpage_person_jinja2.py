"""
art/immeub/rent/htmltemplates/mkpage_person_jinja2.py

"""
from jinja2 import Environment, FileSystemLoader
import jinja2
import settings as sett
from pathlib import Path
import art.immeub.rent.billmodels.billingcard_pydantic as bcard  # bcard.PydtcBillingCard
import art.immeub.rent.pdntcmdls.person_pydant as pers  # pers.
# Set up the template environment to load files from the current directory
middlepath = "js/templates/jinjatemplates"
appsrootfolder = Path(sett.APP_ROOTFOLDER)
templates_abspath = appsrootfolder / middlepath
templatefilename = 'person_template.html'
templatefile = templates_abspath / templatefilename


def get_template() -> jinja2.Template:
  # 1. Initialize the environment with FileSystemLoader
  env = Environment(loader=FileSystemLoader(templates_abspath))
  # 2. Target file as a Path object
  file_path = templatefile
  # 3. Make path relative to the loader directory and convert to string
  relative_template_path = file_path.relative_to(templates_abspath).as_posix()
  # 4. Load the template successfully
  template = env.get_template(relative_template_path)
  return template


def render_html(person) -> None:
  """
  To import it:
    import art.immeub.rent.htmltemplates.jinja2_adhoctest1 as jj2  # jj2.render_html()
  """
  template = get_template()
  rendered_html = template.render(person)
  outputfile = templates_abspath / "person_template.html"
  # Save the generated content to a new HTML file
  with open(outputfile, "w", encoding="utf-8") as f:
    f.write(rendered_html)
  scrmsg = f"HTML file generated successfully as '{outputfile}'!"
  print(scrmsg)


def adhoctest1() -> None:
  person = pers.fetch_person_by_cpf('12345678224')
  persondict = person.to_jsondict()
  print(persondict)
  print('Render')
  render_html(person)


def process():
  """
  """
  pass


if __name__ == '__main__':
  """
  process()
  """
  adhoctest1()
