import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const PORT = process.env.PORT || 3000;

// Replicate __dirname functionality in ES Modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configure EJS View Engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Modern asynchronous route handler
app.get('/', async (req, res) => {
  try {
    // Simulate fetching dynamic async data (e.g., from a database)
    const userData = { name: 'Alex', isAdmin: true };

    // Render the view and pass variables smoothly
    res.render('index', {
      pageTitle: 'Home Page',
      user: userData
    });
  } catch (error) {
    res.status(500).send('Server Error');
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Server spinning at http://localhost:${PORT}`);
});
