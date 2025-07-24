#!/usr/bin/env python3
"""

"""
import time
COURSE_ID_PREFIX = '_ TTC '
avgprice = 3500
qtd = 81
total = qtd * avgprice

def find_delta():
  factor_most_expensive_by_least = 50
  multiplier_to_normalized_middle = (factor_most_expensive_by_least + 1) / 2
  least = avgprice / multiplier_to_normalized_middle
  greater =  least * factor_most_expensive_by_least
  print('greater', greater)
  print('least', least)
  delta = (greater - least) / 80
  print('delta', delta)
  total = qtd * delta
  print('total as delta times qtd', total)
  middle = (greater + least) / 2
  print('middle', middle)
  print('avgprice', avgprice)



def process():
  find_delta()

if __name__ == '__main__':
  process()
