// Update multiple documents that match the filter
const filter = { status: "pending" };
const updateDoc = {
  $set: { status: "processed", updatedAt: new Date() }
};

const result = await collection.updateMany(filter, updateDoc);
console.log(`${result.modifiedCount} documents updated.`);
