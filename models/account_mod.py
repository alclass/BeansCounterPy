#!/usr/bin/env python3
"""
account_mod.py
This module contains the Account class
"""
import sqlite3


class Account:

  def __init__(self, name, bank=None):
    self.name = name
    self.continue_from_date = None

  def db_insert(self, name, bank=None):

