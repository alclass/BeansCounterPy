#!/usr/bin/env python3
"""
at_async_await.py


"""
import time

COURSE_ID_PREFIX = '_ TTC '


def read_after_sleep():
  time.sleep(3)
  data = 'dflkdjfa adlkjfaçlds k afadsfkçaldjfa kldfjçfl'
  return data

# @app.get('/')
async def read_results():
    results = await read_after_sleep()
    return results


def process():
  print('1')
  read_results()
  print('2')

if __name__ == '__main__':
  process()
