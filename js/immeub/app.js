// app.js
const express = require('express');
const app = express();
const port = 3000;

// Set EJS as the view engine
app.set('view engine', 'ejs');
app.set('views', './views');

// Route that fetches data and renders the page
app.get('/', async (req, res) => {
  try {
    // 1. Fetch data from FastAPI (running on port 8000)
    const response = await fetch('http://localhost:8000/api/billing');
    if (!response.ok) throw new Error(`HTTP error ${response.status}`);
    const cards = await response.json();

    // 2. Compute derived fields for each card and item
    const processedCards = cards.map(card => {
      // Compute item total and add sequence number
      const itemsWithTotals = card.items.map((item, index) => ({
        ...item,
        seq: index + 1,                     // column 1: sequence number
        total_for_item: item.original_value + (item.add_ons || 0) // column 5
      }));

      // Compute grand total for this card (sum of all item totals)
      const cardTotal = itemsWithTotals.reduce((sum, item) => sum + item.total_for_item, 0);

      return {
        ...card,
        items: itemsWithTotals,
        card_total: cardTotal
      };
    });

    // 3. Render the EJS template with the processed data
    res.render('index', { cards: processedCards });
  } catch (error) {
    console.error('Error fetching data:', error);
    res.status(500).send('Failed to load billing data');
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});