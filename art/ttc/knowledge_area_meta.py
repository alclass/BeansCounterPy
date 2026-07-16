#!/usr/bin/env python3
"""

This script attempts to read metadata information
  from TTC stored courses throughout a conventioned directory tree.

"""
COURSE_ID_PREFIX = '_ TTC '
COURSE_URL_INTERPOL = 'www.teachco.com/couse/%s'
MP3_PRODUCTION_PREFICES = [
  'mp3s_converted', 'mp3s_converted', 'mp3s_moved', 'mp3s_not_generated',
]


class KnowledgeArea:
  """
  Represents a "Knowledge Area" object

Examples:

  Knowledge Area (kaid=1):
      name: Physics
      path: /Physical Science/Physics

  Knowledge Area (kaid=2):
      name: Physics
      path: /Physical Science/Physics/Quantum Physics

  Knowledge Area (kaid=3):
      name: Physics
      path: /Philosophy/Individual Philosophers/Bertrand Russell

  """
  follower_id = 1

  def __init__(self, name=None, parent=None):
    if parent is None:
      self.name = 'root'
      self.kaid = 1
      self.parent = None
    else:
      self.name = name
      self.parent = parent
      KnowledgeArea.follower_id += 1
      self.kaid = KnowledgeArea.follower_id
    self._parents = None
    self.pathstr = None

  @property
  def pid(self):
    if self.parent is None:
      return None
    return self.parent

  @property
  def parents(self):
    if self._parents is None:
      self._parents = []
      if self.parent is not None:
        self._parents = [self.parent] + self.parent.parents
    return self._parents

  @property
  def path(self):
    if self.pathstr is None:
      pathstr = self.name
      for parent in self.parents:
        name = parent.name
        if name != 'root':
          pathstr = parent.name + '/' + pathstr
        else:
          pathstr = '/' + pathstr
      self.pathstr = pathstr
    return self.pathstr

  def __str__(self):
    output = f"""Knowledge Area (kaid={self.kaid}):
    name: {self.name}
    path: {self.path}"""
    return output


def adhoctests():
  root_ka = KnowledgeArea()
  phys_sci = KnowledgeArea(name='Physical Science', parent=root_ka)
  physics = KnowledgeArea(name='Physics', parent=phys_sci)
  print(physics)
  huma = KnowledgeArea(name='Humanities', parent=root_ka)
  philosophy = KnowledgeArea(name='Philosophy', parent=huma)
  print(philosophy)
  ancient_phil = KnowledgeArea(name='Ancient Philosophy', parent=philosophy)
  print(ancient_phil)


def process():
  """

  """
  pass


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
  adhoctests()
