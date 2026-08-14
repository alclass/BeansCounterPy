from pymongo import MongoClient
uri_con_str = "mongodb://localhost:27017"
dbname = "immeub_db"
collname = "persons"
mng_cli_con_obj = MongoClient(uri_con_str)
db_obj = mng_cli_con_obj[dbname]
collection = db_obj[collname]
collcount = collection.count_documents({})
print('collcount =', collcount)

