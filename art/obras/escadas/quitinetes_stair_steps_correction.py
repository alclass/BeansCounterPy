#!/usr/bin/env python3
"""
art/books/packt/folders/packtInfoDirTreeExtractor.py

"""
from dataclasses import dataclass
degraus = 29, 25, 24, 24, 24, 27, 22, 21, 21, 22, 21


@dataclass
class Step:
  seq: int
  h: int
  dh: int
  prev_h: int | None = None
  DEFAULT_HEIGHT = 24

  def calc_step_increase(self, prev_step):
    # 1 record (copy) the original height (it will be changed)
    self.prev_h = self.h
    # 2 find dh based on target height
    self.dh = self.h + prev_step.dh - self.DEFAULT_HEIGHT
    # 3 zero dh if it got negative
    # as a consequence for this case, height may end up smaller than target
    self.dh = self.dh if self.dh > 0 else 0
    # 4 update height to its new 'logical' value
    self.h = self.h - self.dh + prev_step.dh

  def __str__(self):
    outstr = f"s={self.seq}|prev={self.prev_h}|h={self.h}|dt={self.dh}"
    return outstr


def create_steps():
  steps = []
  for i, height in enumerate(list(degraus)):
    step = Step(
      seq=i+1,
      h=height,
      dh=0,
    )
    steps.append(step)
  steps = list(reversed(steps))
  return steps


def calc_step_height_increase_recursively(prev_step, steps):
  print('recurse', prev_step)
  if len(steps) > 0:
    step = steps.pop()
  else:
    return
  step.calc_step_increase(prev_step)
  return calc_step_height_increase_recursively(step, steps)


def process():
  """
  """
  steps = create_steps()
  step = steps.pop()
  # establish dh for the first step
  # if data above has not changed, the first height increase is 29-24=5
  step.dh = step.h - step.DEFAULT_HEIGHT
  calc_step_height_increase_recursively(step, steps)


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
