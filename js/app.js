// 1. Import the required libraries
// app.js
const express = require('express');
const { MongoClient } = require('mongodb');

const DEFAULT_MONGO_DB = 'packt_books_db'
const DEFAULT_MONGO_COLL = 'packt_books_coll'

// 2. Create an instance of an Express application
const app = express();
const port = 3000;

// 3. MongoDB connection details
// For a local MongoDB instance running on the default port
const url = 'mongodb://localhost:27017';
const dbName = `${DEFAULT_MONGO_DB}`; // <-- Replace with your database name
const collectionName = `${DEFAULT_MONGO_COLL}`; // <-- Replace with your collection name

let db; // Variable to hold the database connection

// 4. Connect to MongoDB and start the server
async function startServer() {
  try {
    // Connect to the MongoDB server
    const client = new MongoClient(url);
    await client.connect();
    console.log('✅ Connected successfully to MongoDB server');

    // Select the database
    db = client.db(dbName);
    console.log(`✅ Using database: ${dbName}`);

    // Start the Express server *only after* the database connection is successful
    app.listen(port, () => {
      console.log(`🚀 Server is running at http://localhost:${port}`);
      console.log(`👉 To see your data, visit http://localhost:${port}/data`);
    });
  } catch (error) {
    console.error('❌ Failed to connect to MongoDB:', error);
    process.exit(1); // Exit the process if database connection fails
}
}

// 5. Define an API endpoint to get data from the collection
// When you visit http://localhost:3000/data in your browser, this code runs.
app.get('/data', async (req, res) => {
    // Check if the database connection is ready
    if (!db) {
        return res.status(500).send('Database not ready yet.');
    }

    try {
        // Get the collection
        const collection = db.collection(collectionName);

        // Find all documents in the collection and convert them to an array
        // The `{}` means "find all documents" (no filter)
        const documents = await collection.find({}).toArray();

        // Send the documents as a JSON response
        // This is what your browser will receive and display
        res.json(documents);
    } catch (error) {
        console.error('Error fetching data:', error);
        res.status(500).send('An error occurred while fetching data.');
    }
});

// 6. A simple home route for testing
app.get('/', (req, res) => {
    res.send('Hello! Go to <a href="/data">/data</a> to see your MongoDB data.');
});

// 7. Finally, start the server by calling the function we defined
startServer();
