/*
   js/showbooktable/showbooks.js 20260615_e56c16
   to run this node server:
     $ cd js (from the app's root-folder)
     $ node showbooks.js
 */
const express = require('express');
const mongoose = require('mongoose');
const app = express();
const PORT = 3000;
const MONGO_DBNAME = "packt_books_db";
// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// MongoDB connection
let url =  'mongodb://localhost:27017/' + MONGO_DBNAME
mongoose.connect(url, {  // linter said: Promise returned from connect is ignored
  // useNewUrlParser: true,
  // useUnifiedTopology: true,
});
const db = mongoose.connection;
db.on('error', console.error.bind(console, 'connection error:'));
db.once('open', () => {
  console.log('Connected to MongoDB');
});

// Book Schema with unique ISBN-13
const bookSchema = new mongoose.Schema({
  title: { type: String, required: true },
  year: { type: Number, required: true },
  authors: { type: String, required: true },
  isbn13: { type: String, required: true, unique: true },
  createdAt: { type: Date, default: Date.now },
  updatedAt: { type: Date, default: Date.now }
});

const Book = mongoose.model('Book', bookSchema, 'packt_books_coll');

// ========== API ROUTES ==========

// Get all bookroutes (sorted by creation date by default)
app.get('/api/books', async (req, res) => {
  try {
    const books = await Book.find().sort({ createdAt: 1 });
    res.json(books);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Create a new book
app.post('/api/books', async (req, res) => {
  try {
    const { title, year, authors, isbn13 } = req.body;
    const book = new Book({ title, year, authors, isbn13 });
    await book.save();
    res.status(201).json(book);
  } catch (err) {
    if (err.code === 11000) {
      res.status(400).json({ error: 'ISBN-13 must be unique' });
    } else {
      res.status(400).json({ error: err.message });
    }
  }
});

// Update a book
app.put('/api/books/:id', async (req, res) => {
  try {
    const { title, year, authors, isbn13 } = req.body;
    const bookId = req.params.id;
    
    // Check if another book has the same ISBN-13
    const existingBook = await Book.findOne({ isbn13, _id: { $ne: bookId } });
    if (existingBook) {
      return res.status(400).json({ error: 'ISBN-13 must be unique' });
    }
    
    const updatedBook = await Book.findByIdAndUpdate(
      bookId,
      { title, year, authors, isbn13 },
      { new: true, runValidators: true }
    );
    res.json(updatedBook);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Delete a book
app.delete('/api/books/:id', async (req, res) => {
  try {
    await Book.findByIdAndDelete(req.params.id);
    res.status(204).send();
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ========== MAIN PAGE ==========
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Book Manager</title>
      <style>
        * {
          box-sizing: border-box;
          font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
        }
        body {
          background: #f5f7fb;
          margin: 0;
          padding: 2rem;
        }
        .container {
          max-width: 1300px;
          margin: 0 auto;
          background: white;
          border-radius: 1rem;
          box-shadow: 0 4px 6px rgba(0,0,0,0.05);
          overflow: hidden;
          padding: 1.5rem;
        }
        h1 {
          margin: 0 0 0.5rem 0;
          font-size: 1.8rem;
          color: #1e293b;
        }
        .header-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
          gap: 1rem;
        }
        .add-btn {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.6rem 1.2rem;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.2s;
        }
        .add-btn:hover {
          background: #2563eb;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          background: white;
          border-radius: 0.75rem;
          overflow: auto;
          display: block;
        }
        th, td {
          padding: 0.75rem 1rem;
          text-align: left;
          border-bottom: 1px solid #e2e8f0;
        }
        th {
          background-color: #f8fafc;
          font-weight: 600;
          color: #0f172a;
          cursor: pointer;
          user-select: none;
          position: relative;
        }
        th:hover {
          background-color: #f1f5f9;
        }
        th.sort-asc::after, th.sort-desc::after {
          content: "▼";
          font-size: 0.7rem;
          margin-left: 0.5rem;
          display: inline-block;
        }
        th.sort-asc::after {
          transform: rotate(180deg);
        }
        .action-buttons {
          display: flex;
          gap: 0.5rem;
        }
        button.edit, button.delete {
          border: none;
          padding: 0.3rem 0.7rem;
          border-radius: 0.375rem;
          cursor: pointer;
          font-size: 0.8rem;
          font-weight: 500;
        }
        button.edit {
          background: #fef9c3;
          color: #854d0e;
        }
        button.edit:hover {
          background: #fde047;
        }
        button.delete {
          background: #fee2e2;
          color: #b91c1c;
        }
        button.delete:hover {
          background: #fecaca;
        }
        /* Modal styles */
        .modal {
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0,0,0,0.5);
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }
        .modal-content {
          background: white;
          padding: 1.8rem;
          border-radius: 1rem;
          width: 90%;
          max-width: 500px;
          box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        }
        .modal-content h3 {
          margin-top: 0;
          margin-bottom: 1rem;
        }
        .modal-content input {
          width: 100%;
          padding: 0.6rem;
          margin: 0.5rem 0 1rem 0;
          border: 1px solid #cbd5e1;
          border-radius: 0.5rem;
          font-size: 0.9rem;
        }
        .modal-content button {
          padding: 0.6rem 1rem;
          border-radius: 0.5rem;
          border: none;
          cursor: pointer;
          margin-right: 0.5rem;
        }
        .submit-btn {
          background: #3b82f6;
          color: white;
        }
        .cancel-btn {
          background: #e2e8f0;
        }
        .error-msg {
          color: #dc2626;
          font-size: 0.8rem;
          margin: 0.3rem 0;
          display: none;
        }
        .empty-row td {
          text-align: center;
          padding: 2rem;
          color: #64748b;
        }
        @media (max-width: 768px) {
          body { padding: 1rem; }
          th, td { padding: 0.5rem; }
          .action-buttons { flex-direction: column; gap: 0.3rem; }
        }
      </style>
    </head>
    <body>
    <div class="container">
      <div class="header-bar">
        <h1>📚 Book Collection</h1>
        <button class="add-btn" id="openAddModalBtn">+ Add New Book</button>
      </div>
      <div style="overflow-x: auto;">
        <table id="booksTable">
          <thead>
            <tr>
              <th data-sort="seq">Seq</th>
              <th data-sort="title">Title</th>
              <th data-sort="year">Year</th>
              <th data-sort="authors">Authors</th>
              <th data-sort="isbn13">ISBN-13</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody id="tableBody">
            <tr><td colspan="6" class="empty-row">Loading books...</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal for Add/Edit -->
    <div id="bookModal" class="modal">
      <div class="modal-content">
        <h3 id="modalTitle">Add New Book</h3>
        <input type="hidden" id="bookId" />
        <div>
          <label>Title *</label>
          <input type="text" id="title" placeholder="Book title" />
        </div>
        <div>
          <label>Year *</label>
          <input type="number" id="year" placeholder="Publication year" />
        </div>
        <div>
          <label>Authors *</label>
          <input type="text" id="authors" placeholder="Author name(s)" />
        </div>
        <div>
          <label>ISBN-13 * (unique)</label>
          <input type="text" id="isbn13" placeholder="978-3-16-148410-0" />
        </div>
        <div id="modalError" class="error-msg"></div>
        <div style="margin-top: 1rem;">
          <button id="modalSubmitBtn" class="submit-btn">Save</button>
          <button id="modalCancelBtn" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>

    <script>
      // Global state
      let booksData = [];
      let currentSortField = 'createdAt';    // default sort by creation (Seq order)
      let currentSortDirection = 'asc';      // 'asc' or 'desc'
      
      // DOM elements
      const tableBody = document.getElementById('tableBody');
      const modal = document.getElementById('bookModal');
      const modalTitle = document.getElementById('modalTitle');
      const bookIdInput = document.getElementById('bookId');
      const titleInput = document.getElementById('title');
      const yearInput = document.getElementById('year');
      const authorsInput = document.getElementById('authors');
      const isbn13Input = document.getElementById('isbn13');
      const modalError = document.getElementById('modalError');
      const modalSubmitBtn = document.getElementById('modalSubmitBtn');
      const modalCancelBtn = document.getElementById('modalCancelBtn');
      const openAddModalBtn = document.getElementById('openAddModalBtn');
      
      // Helper: Sorting function
      function sortBooks(books, field, direction) {
        const sorted = [...books];
        sorted.sort((a, b) => {
          let aVal, bVal;
          
          // Special handling for seq (based on createdAt)
          if (field === 'seq') {
            aVal = new Date(a.createdAt).getTime();
            bVal = new Date(b.createdAt).getTime();
          } else if (field === 'year') {
            aVal = a.year;
            bVal = b.year;
          } else if (field === 'title' || field === 'authors' || field === 'isbn13') {
            aVal = (a[field] || '').toLowerCase();
            bVal = (b[field] || '').toLowerCase();
          } else {
            aVal = a[field];
            bVal = b[field];
          }
          
          if (aVal < bVal) return direction === 'asc' ? -1 : 1;
          if (aVal > bVal) return direction === 'asc' ? 1 : -1;
          return 0;
        });
        return sorted;
      }
      
      // Render table with current sorting
      function renderTable() {
        if (!booksData.length) {
          tableBody.innerHTML = '<tr><td colspan="6" class="empty-row">No bookroutes found. Add a book to get started!</td></tr>';
          return;
        }
        
        const sortedBooks = sortBooks(booksData, currentSortField, currentSortDirection);
        
        let html = '';
        sortedBooks.forEach((book, index) => {
          html += \`
            <tr>
              <td>\${index + 1}</td>
              <td>\${escapeHtml(book.title)}</td>
              <td>\${book.year}</td>
              <td>\${escapeHtml(book.authors)}</td>
              <td>\${escapeHtml(book.isbn13)}</td>
              <td class="action-buttons">
                <button class="edit" data-id="\${book._id}">✏️ Edit</button>
                <button class="delete" data-id="\${book._id}">🗑️ Delete</button>
              </td>
            </tr>
          \`;
        });
        tableBody.innerHTML = html;
        
        // Attach event listeners to edit/delete buttons
        document.querySelectorAll('.edit').forEach(btn => {
          btn.addEventListener('click', () => {  // param e removed
            const id = btn.getAttribute('data-id');
            openEditModal(id);
          });
        });
        
        document.querySelectorAll('.delete').forEach(btn => {
          btn.addEventListener('click', async () => {  // param e removed
            const id = btn.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this book?')) {
              try {
                const res = await fetch(\`/api/books/\${id}\`, { method: 'DELETE' });
                if (res.ok) {
                  await fetchBooks();
                } else {
                  const err = await res.json();
                  alert('Delete failed: ' + (err.error || 'Unknown error'));
                }
              } catch (err) {
                alert('Error deleting book');
              }
            }
          });
        });
      }
      
      // Escape HTML to prevent injection
      function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/[&<>]/g, function(m) {
          if (m === '&') return '&amp;';
          if (m === '<') return '&lt;';
          if (m === '>') return '&gt;';
          return m;
        }).replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]/g, function(c) {
          return c;
        });
      }
      
      // Fetch bookroutes from API
      async function fetchBooks() {
        try {
          const response = await fetch('/api/books');
          if (!response.ok) throw new Error('Failed to fetch');
          booksData = await response.json();
          renderTable();
        } catch (err) {
          console.error(err);
          tableBody.innerHTML = '<tr><td colspan="6" class="empty-row">Error loading bookroutes. Is the server running?</td></tr>';
        }
      }
      
      // Open modal for adding
      function openAddModal() {
        modalTitle.innerText = 'Add New Book';
        bookIdInput.value = '';
        titleInput.value = '';
        yearInput.value = '';
        authorsInput.value = '';
        isbn13Input.value = '';
        modalError.style.display = 'none';
        modal.style.display = 'flex';
      }
      
      // Open modal for editing
      async function openEditModal(id) {
        const book = booksData.find(b => b._id === id);
        if (!book) return;
        
        modalTitle.innerText = 'Edit Book';
        bookIdInput.value = book._id;
        titleInput.value = book.title;
        yearInput.value = book.year;
        authorsInput.value = book.authors;
        isbn13Input.value = book.isbn13;
        modalError.style.display = 'none';
        modal.style.display = 'flex';
      }
      
      // Save book (create or update)
      async function saveBook() {
        const id = bookIdInput.value;
        const title = titleInput.value.trim();
        const year = parseInt(yearInput.value);
        const authors = authorsInput.value.trim();
        const isbn13 = isbn13Input.value.trim();
        
        if (!title || !year || !authors || !isbn13) {
          modalError.innerText = 'All fields are required.';
          modalError.style.display = 'block';
          return;
        }
        
        const bookData = { title, year, authors, isbn13 };
        
        try {
          let response;
          if (id) {
            // Update
            response = await fetch(\`/api/books/\${id}\`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(bookData)
            });
          } else {
            // Create
            response = await fetch('/api/books', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(bookData)
            });
          }
          
          if (response.ok) {
            modal.style.display = 'none';
            await fetchBooks();
          } else {
            const errorData = await response.json();
            modalError.innerText = errorData.error || 'Validation failed';
            modalError.style.display = 'block';
          }
        } catch (err) {
          modalError.innerText = 'Network error. Please try again.';
          modalError.style.display = 'block';
        }
      }
      
      // Sorting header click handling
      function setupSorting() {
        const headers = document.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
          header.addEventListener('click', () => {
            const sortField = header.getAttribute('data-sort');
            
            if (currentSortField === sortField) {
              // Toggle direction
              currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            } else {
              currentSortField = sortField;
              currentSortDirection = 'asc';
            }
            
            // Update UI arrows
            headers.forEach(th => {
              th.classList.remove('sort-asc', 'sort-desc');
            });
            if (currentSortDirection === 'asc') {
              header.classList.add('sort-asc');
            } else {
              header.classList.add('sort-desc');
            }
            
            renderTable(); // re-render with new sort
          });
        });
      }
      
      // Modal close handlers
      modalCancelBtn.addEventListener('click', () => {
        modal.style.display = 'none';
      });
      window.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
      });
      modalSubmitBtn.addEventListener('click', saveBook);
      openAddModalBtn.addEventListener('click', openAddModal);
      
      // Initialize app
      async function init() {
        await fetchBooks();
        setupSorting();
        // Default arrow on Seq (since default sort is createdAt -> Seq)
        const seqHeader = document.querySelector('th[data-sort="seq"]');
        if (seqHeader) seqHeader.classList.add('sort-asc');
      }
      
      init();
    </script>
    </body>
    </html>
  `);
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});