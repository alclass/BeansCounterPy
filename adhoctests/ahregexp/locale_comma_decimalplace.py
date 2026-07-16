#!/usr/bin/env python3
"""
adhoctests/regexp/locale_comma_decimalplace.py


https://stackoverflow.com/questions/7106417/convert-decimal-mark-when-reading-numbers-as-input
"""
import locale
import re
# a) Set to users preferred locale:
loc = locale.getlocale()  # get and save current locale
print('1 loc', loc)
locale.setlocale(locale.LC_ALL, '')
print('2 loc', loc)
# Or a specific locale:
locale.setlocale(locale.LC_NUMERIC, "en_DK.UTF-8")  # "en_DK.UTF-8"
strval = "3,14"
print('strval', strval, 'locale.atof =>', locale.atof(strval))
# b)
decmark_reg = re.compile(r'(?<=\d),(?=\d)')
ss = 'abc , 2,5 def ,5,88 or (2,5, 8,12, 8945,3 )'
print(ss)
print(decmark_reg.sub('.', ss))
# c)
loc = locale.getlocale()  # get and save current locale
print('loc', loc)
# use locale that provided the number;
# example if German locale was used:
# locale.setlocale(locale.LC_NUMERIC, "fr_FR.UTF-8")
print('loc', loc)
pythonnumber = locale.atof(strval)
print('pythonnumber', pythonnumber)
locale.setlocale(locale.LC_ALL, loc)  # restore saved loca
