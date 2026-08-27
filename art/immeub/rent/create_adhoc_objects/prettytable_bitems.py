"""


To import it:
  art.immeub.rent.create_adhoc_objects.prettytable_bitems as ppbitems  # ppbitems.PrettyTableForBI
"""
from prettytable import PrettyTable


class PrettyTableForBI:

  def __init__(self):
    self.table = PrettyTable()
    self.headers = ["seq", "descrição", "mês ref.", "valor"]
    self.table.field_names = self.headers

  def add_to_table(self, bitem):
    values = bitem.get_the_4_billingitem_values_as_lst()
    self.table.add_row(values)
