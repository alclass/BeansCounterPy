#!/usr/bin/env python3
"""
art/models/escadas/stairStepHeightsCorrection.py
  A script that calculates step heights, to be leveled with mass,
    for a stair with non-equal step heights.

  This script:
    a) has an 11-step stair example hardcoded.
    b) does not correct 'negative delta' (*).

    (*) This (negative delta) is the case where the steps
      would have to be carved out (some sort of concrete-cutting-out)
      instead of mass-filling-up, the latter its intention.

    In the hardcoded example,
      the last two step-heights are not 'corrected'
        (or mass-filled-up).

  TO-DO:
    To make it more general, this hardcoded list might
      be read from a file or as arguments from the command line.

Usage:
  $stairStepHeightsCorrection.py [-nr] [-r]
    where:
      [-nr] => (the default) process 'non-recursively'
      [-r] => process 'recursively'

Example:
  $stairStepHeightsCorrection.py -r
     Runs this script calculating the step increase heights recursively

"""
import sys
from dataclasses import dataclass
# hardcoded example: TO-DO: generalize its input
degraus = 29, 25, 24, 24, 24, 27, 22, 21, 21, 22, 21


@dataclass
class Step:
  """
  Represents a stair step and when in a collection has the purpose
    of calculating step heights that 'soften' unequal heights.
  """
  seq: int
  h: int
  dh: int
  prev_h: int | None = None
  DEFAULT_HEIGHT = 24

  def calc_step_increase(self, prev_step=None):
    if prev_step is None:
      prev_step = Step(-1, -1, 0)
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
  """
  Notice that in this script 'steps' is not a global variable
  So, when processing recursively, the recurse function needs
  to return steps as a new list
    ('steps' is not mutated in the recursive function)
  """
  steps = []
  for i, height in enumerate(list(degraus)):
    step = Step(
      seq=i+1,
      h=height,
      dh=0,
    )
    steps.append(step)
  return steps


def calc_step_height_increase_nonrecurs(steps):
  """
  This function is for the non-recursive approach.
  """
  prev_step = None
  for i, step in enumerate(steps):
    if i == 0:
      # for the first step, there no previous one
      prev_step = step
      prev_step.calc_step_increase()
      continue
    step.calc_step_increase(prev_step)
    prev_step = step


def calc_step_height_increase_recursively(prev_step, steps, aftersteps):
  """
  This function is for the recursive approach.
  """
  if len(steps) > 0:
    step = steps.pop()
    aftersteps.append(step)
  else:
    return aftersteps
  print('len steps', len(steps), 'len aftersteps', len(aftersteps))
  step.calc_step_increase(prev_step)
  return calc_step_height_increase_recursively(step, steps, aftersteps)


def print_steps(steps):
  for step in steps:
    print(step)


def process_via_recurs_or_nonrecurs(
    steps,
    is_recursive_process=False
  ):
  if is_recursive_process:
    steps = list(reversed(steps))
    prev_step = steps.pop()
    prev_step.calc_step_increase(None)
    aftersteps = [prev_step]
    # steps (consumed in the recursive functions) returns 'processed' via aftersteps
    steps = calc_step_height_increase_recursively(prev_step, steps, aftersteps)
  else:
    # steps updates 'in-place' in the non-recursive function
    calc_step_height_increase_nonrecurs(steps)
  return steps


def ztreat_first_step_n_seqorder(steps, to_be_recursive):
  """
  No longer used/needed.

  # establish dh for the first step
  # if data series above has not changed
     (the first hard coded height series in this program),
     the first height increase is 29-24=5

  About which step is the first one
    (the one that does not have a previous one)
    a) the first step in a non-recursive approach is the first element in list
    b) the first step in a recursive approach is the last element in list
       but, notice, the whole list is reversed, so the last becomes the first
  """
  if to_be_recursive:
    # reverse order for the recursive processing
    steps = list(reversed(steps))
  step = steps[0]
  step.dh = step.h - step.DEFAULT_HEIGHT
  step.prev_h = step.h
  step.h = step.h - step.dh
  # 'steps' is not global, so we must return it
  return steps


def create_steps_n_pŕocess(to_be_recursive):
  """
  """
  steps = create_steps()
  # the necessity to receive 'steps' back is because
  # it's changed (to aftersteps) when processing recursively
  steps = process_via_recurs_or_nonrecurs(steps, to_be_recursive)
  print_steps(steps)


def get_args():
  is_recursive = None
  for arg in sys.argv[1:]:
    if arg == "-h" or arg == '--help':
      print(__doc__)
      sys.exit(0)
    elif arg.startswith("-r"):
      is_recursive = True
    elif arg.startswith("-nr"):
      is_recursive = False
  # default it if an argument was not given
  is_recursive = is_recursive or False  # though None could be 'cast' as 'False'
  return is_recursive


def process():
  is_recursive = get_args() or False
  scrmsg = f"Program: stairStepHeightsCorrection.py (for {len(degraus)} steps)\n"
  scrmsg += f"\tis_recursive = {is_recursive}"
  print(scrmsg)
  create_steps_n_pŕocess(is_recursive)


if __name__ == '__main__':
  """
  adhoc_test1()
  """
  process()
