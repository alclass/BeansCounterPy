#!/usr/bin/env python3
"""
art/books/packt/mongo/adhoc_mongo/mongoReadWriteExample.py

"""
from pymongo import MongoClient

# 1. Connect to MongoDB (Change the URI if you use MongoDB Atlas)
# For local MongoDB: "mongodb://localhost:27017/"
# For MongoDB Atlas: "mongodb+srv://<username>:<password>@cluster.mongodb.net/"
connection_string = "mongodb://localhost:27017/"
client = MongoClient(connection_string)

# 2. Select Database and Collection
db = client["company_db"]
collection = db["employees"]

# ==========================================
# WRITE OPERATIONS (Insert Data)
# ==========================================

# Insert a single document
employee_data = {
    "name": "Alice Smith",
    "department": "Engineering",
    "skills": ["Python", "MongoDB", "Docker"],
    "experience_years": 5
}
insert_result = collection.insert_one(employee_data)
print(f"✅ Successfully inserted document with ID: {insert_result.inserted_id}")

# Insert multiple documents at once
multiple_employees = [
    {"name": "Bob Jones", "department": "Design", "skills": ["Figma", "UI/UX"], "experience_years": 3},
    {"name": "Charlie Brown", "department": "Engineering", "skills": ["Java", "SQL"], "experience_years": 7}
]
collection.insert_many(multiple_employees)


# ==========================================
# READ OPERATIONS (Query Data)
# ==========================================

# Read ONE document matching a filter
query_filter = {"name": "Alice Smith"}
single_employee = collection.find_one(query_filter)
print("\n🔍 Found Single Employee:")
print(single_employee)

# Read ALL documents in the collection
print("\n📋 All Employees in Database:")
for employee in collection.find():
    print(f"- {employee['name']} ({employee['department']})")

# Read documents using advanced filters (e.g., experience > 4 years)
print("\n⚡ Experienced Engineers (> 4 years):")
advanced_query = {"experience_years": {"$gt": 4}}
for employee in collection.find(advanced_query):
    print(f"- {employee['name']}: {employee['experience_years']} years")

# 3. Close the connection when done
client.close()
