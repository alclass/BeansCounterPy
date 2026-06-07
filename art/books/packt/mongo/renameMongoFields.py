from pymongo import MongoClient
from art.books.packt.dirwalk import DEFAULT_MONGO_DB
from art.books.packt.dirwalk import DEFAULT_MONGO_COLL

# 1. Connect to your MongoDB deployment
client = MongoClient("mongodb://localhost:27017/")

# 2. Select your database and collection
db = client[DEFAULT_MONGO_DB]
collection = db[DEFAULT_MONGO_COLL]

# 3. Define the rename operation using the $rename operator
# Format: {"$rename": {"old_field_name": "new_field_name"}}
rename_operation = {
    "$rename": {
        "isbn": "isbn13"
    }
}

# 4. Apply the change to all documents in the collection
# The empty curly braces {} match every document in the collection
result = collection.update_many({}, rename_operation)

# 5. Print the number of documents updated
print(f"Matched documents: {result.matched_count}")
print(f"Modified documents: {result.modified_count}")
