const filter = { status: "pending" };
const documents = await collection.find(filter).toArray();

for (const doc of documents) {
  // Application logic
  await collection.updateOne(
      { _id: doc._id },
      { $set: { reviewed: true } }
  );
}
