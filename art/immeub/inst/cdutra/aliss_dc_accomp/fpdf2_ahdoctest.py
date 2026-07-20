"""
art/immeub/inst/cdutra/aliss_dc_accomp/fpdf2_ahdoctest.py

"""
from fpdf import FPDF

# 1. Instantiate the FPDF object
pdf = FPDF(orientation="P", unit="mm", format="A4")

# 2. Add a page to initialize the cursor
pdf.add_page()

# 3. Set the font (Core fonts: helvetica, times, courier)
pdf.set_font("helvetica", size=12)

text = "Hello World!"
# 4. Add content using text cells
pdf.cell(w=0, h=10, new_x="LMARGIN", new_y="NEXT", align="C", text=text)

# 5. Output and save the file
pdf.output("hello_world.pdf")
