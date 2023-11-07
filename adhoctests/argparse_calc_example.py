#!/usr/bin/env python3
"""
  https://realpython.com/command-line-interfaces-python-argparse/
  One Example:
    parser.add_argument("--veggies", nargs="+")
    parser.add_argument("--fruits", nargs="*")
      $ python cooking.py --veggies pepper tomato --fruits apple banana
    parser.add_argument("--size", choices=["S", "M", "L", "XL"], default="M")
    my_parser.add_argument("--weekday", type=int, choices=range(1, 8))
"""
import argparse


def add():
  pass


def sub():
  pass


def mul():
  pass


def div():
  pass


def dispatch():
  global_parser = argparse.ArgumentParser(prog="calc")
  subparsers = global_parser.add_subparsers(title="subcommands", help="arithmetic operations")
  arg_template = {
    "dest": "operands",
    "type": float,
    "nargs": 2,
    "metavar": "OPERAND",
    "help": "a numeric value",
  }
  add_parser = subparsers.add_parser("add", help="add two numbers a and b")
  add_parser.add_argument(**arg_template)
  add_parser.set_defaults(func=add)
  sub_parser = subparsers.add_parser("sub", help="subtract two numbers a and b")
  sub_parser.add_argument(**arg_template)
  sub_parser.set_defaults(func=sub)
  mul_parser = subparsers.add_parser("mul", help="multiply two numbers a and b")
  mul_parser.add_argument(**arg_template)
  mul_parser.set_defaults(func=mul)
  div_parser = subparsers.add_parser("div", help="divide two numbers a and b")
  div_parser.add_argument(**arg_template)
  div_parser.set_defaults(func=div)
  args = global_parser.parse_args()
  print(args.func(*args.operands))


def adhoctests():
  """
  for entry in target_dir.iterdir():
    print(build_output(entry, long=args.long))
  pass

  """
  parser = argparse.ArgumentParser()
  parser = argparse.ArgumentParser(
    prog="ls",
    description="List the content of a directory",
    epilog="Thanks for using %(prog)s! :)",
  )
  general = parser.add_argument_group("general output")
  general.add_argument("path")
  detailed = parser.add_argument_group("detailed output")
  detailed.add_argument("-l", "--long", action="store_true")
  args = parser.parse_args()
  parser.add_argument("-c", "--connect", action="store_true")


def process():
  pass


if __name__ == '__main__':
  """
  adhoctests()
  """
  process()
