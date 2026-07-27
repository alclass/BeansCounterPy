"""
art/immeub/inst/cdutra/credeb_accomp_pkg/__init__.py

import art.immeub.inst.cdutra.credeb_accomp_pkg as init
from local_settings import LOCAL_MONGODB_URI_STR
"""
import lib.dbfs.local_settings as dbls  # dbls.LOCAL_MONGODB_URI_STR
import art.immeub.local_settings as immeub_ls  #  immeub_ls.IMMEUB_DBNAME
import art.immeub.inst.cdutra.credeb_accomp_pkg.local_settings as ls
# Mongo DB config-vars
LOCAL_MONGODB_URI_STR = dbls.LOCAL_MONGODB_URI_STR
IMMEUB_DBNAME = immeub_ls.IMMEUB_DBNAME
ALIS_DEBT_ACC_COLLNAME = ls.ALIS_DEBT_ACC_COLLNAME
# money or finance factor config-vars
VALOR_META_MENSAL_BRL = 500
MORA_FIX_DEC = 0.02
