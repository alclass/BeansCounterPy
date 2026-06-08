
degraus = 29, 25, 24, 24, 24, 27, 22, 21, 21, 22, 21
for d in degraus:
  print(d)

class Correction:

  def __init__(self, degraus):
    self.degraus = degraus

  def delta(self, d1, d2):
    return d1 - d2

  def list_deltas(self):
    deg = self.degraus
    deltas = map(lambda i: deg[i] - deg[i+1], range(len(self.degraus[:-1])))
    print(list(deltas))

  def new_heights(self):
    subir_tuple = 0, 5, 5, 5, 5, 4, 8, 7, 7, 6, 5, 5l
    subir = list(subir_tuple)
    new_degraus = []
    for n_deg in range(1, len(self.degraus)+1):
      i = n_deg - 1
      if n_deg == 1:
        new_d = self.degraus[i] - subir[i+1]
        new_degraus.append(new_d)
        continue
      new_d = self.degraus[i] + subir[i] - subir[i+1]
      new_degraus.append(new_d)
    print(new_degraus)

  def process(self):
    self.list_deltas()
    self.new_heights()


def process():
  corr = Correction(degraus)
  corr.process()


if __name__ == '__main__':
  """
  adhoc_test1()
  adhoc_test2()
  """
  process()
