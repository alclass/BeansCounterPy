#!/usr/bin/env python3
"""
Based on regexp explained in:
  https://regex101.com/r/YP1Vdn/3

^\d{1,3}(?:\.\d{3})*(?:,\d+)?$|^\d+(?:,)?\d+$

1st Alternative ^\d{1,3}(?:\.\d{3})*(?:,\d+)?$
^ asserts position at start of a line
\d matches a digit (equivalent to [0-9])
{1,3} matches the previous token between 1 and 3 times, as many times as possible, giving back as needed (greedy)
Non-capturing group (?:\.\d{3})*
* matches the previous token between zero and unlimited times, as many times as possible, giving back as needed (greedy)
\. matches the character . with index 4610 (2E16 or 568) literally (case sensitive)
\d  matches a digit (equivalent to [0-9])
{3} matches the previous token exactly 3 times
Non-capturing group (?:,\d+)?
? matches the previous token between zero and one times, as many times as possible, giving back as needed (greedy)
, matches the character , with index 4410 (2C16 or 548) literally (case sensitive)
\d
 matches a digit (equivalent to [0-9])
+ matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)
$ asserts position at the end of a line
2nd Alternative ^\d+(?:,)?\d+$
^ asserts position at start of a line
\d
 matches a digit (equivalent to [0-9])
+ matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)
Non-capturing group (?:,)?
? matches the previous token between zero and one times, as many times as possible, giving back as needed (greedy)
, matches the character , with index 4410 (2C16 or 548) literally (case sensitive)
\d
 matches a digit (equivalent to [0-9])
+ matches the previous token between one and unlimited times, as many times as possible, giving back as needed (greedy)
$ asserts position at the end of a line
Global pattern flags
g modifier: global. All matches (don't return after first match)
m modifier: multi line. Causes ^ and $ to match the begin/end of each line (not only begin/end of string)
https://regex101.com/r/uY6Kcm/1
https://regex101.com/delete/rXUybKX1OrFaThw8HMyExJ3dBfFKLihDMtHC
https://regex101.com/delete/1/7zs0lJeXr6GYUFQjDNd8HsrCxjCbp8fKUFro
"""
import re

teststr = '''
1.000,00
.000,00
.000.000,00
0.000,00
111
111,11
111.111,11
11.111.110,00
11.1111.11,00
111
11.11
1111.00
10111111,00
111.000,
11.111,00
111111,00
10.000,00000000
1000.100.00
1.000.000,00
-12.345,67
12.345,67
'''


def print_result_on_teststr():
  regex_patstr = r"^\d{1,3}(?:\.\d{3})*(?:,\d+)?$|^\d+(?:,)?\d+$"
  recomp = re.compile(regex_patstr)
  lines = teststr.split('\n')
  for snumber in lines:
    if len(snumber) == 0:
      continue
    matchobj = recomp.match(snumber)
    print('supposed number ', snumber, ' => ', matchobj)


t2 = '31/03/2023 SALDO ANTERIOR               209.046,56                                                  17.983,676394'


def print_result_on_2ndteststr():
  regex_patstr = r"(\b\d{1,3}(?:\.\d{3})*(?:,\d+)?$)"
  regex_patstr = r"(\b\d{1,3}(?:\.\d{3})*(?:,\d+)?\b)"
  recomp = re.compile(regex_patstr)
  findall = recomp.findall(t2)
  matchobj = recomp.match(t2)
  print('test2', t2)
  exprstr = 'no groups' if not matchobj else matchobj.groups()
  print('matchobj => ', matchobj, 'groups', exprstr)
  print('findall => ', findall)


def example1_from_pynative():
  """
  https://pynative.com/python-regex-capturing-groups/
  """
  print('example1_from_pynative()')
  target_string = "The price of PINEAPPLE ice cream is 20"
  # two groups enclosed in separate ( and ) bracket
  result = re.search(r"(\b[A-Z]+\b).+(\b\d+)", target_string)
  # Extract matching values of all groups
  # group 1 output 'PINEAPPLE'; group 2 output 20
  print('target_string', target_string)
  print('groups', result.groups(), 'group 1', result.group(1), 'group 2', result.group(2))


if __name__ == '__main__':
  print_result_on_2ndteststr()
  example1_from_pynative()
