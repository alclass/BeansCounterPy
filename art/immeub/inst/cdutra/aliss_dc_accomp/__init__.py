"""
art/immeub/inst/cdutra/aliss_dc_accomp/__init__.py

from local_settings import LOCAL_MONGODB_URI_STR
"""
import lib.dbfs.local_settings as dbls  # dbls.LOCAL_MONGODB_URI_STR
import art.immeub.local_settings as immeub_ls
import art.immeub.inst.cdutra.aliss_dc_accomp.local_settings as ls
IMMEUB_DBNAME = immeub_ls.IMMEUB_DBNAME
ALIS_DEBT_ACC_COLLNAME = ls.ALIS_DEBT_ACC_COLLNAME
LOCAL_MONGODB_URI_STR = dbls.LOCAL_MONGODB_URI_STR
