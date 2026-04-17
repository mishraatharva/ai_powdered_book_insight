# AI Powdered Book Insight

A Django REST API for book data and AI-powered chat access to book information. The app stores book records, exposes list/detail endpoints, and includes a chat endpoint backed by the existing RAG helper.

## Project Structure

- `book_ai/` - Django project root
  - `book_ai/settings.py` - Django settings and database configuration
  - `book_ai/urls.py` - root URL configuration
  - `books/` - Django app containing models, serializers, views, and API routes
- `requirements.txt` - Python dependencies
- `scripts/` - contains the RAG helper used by the chat endpoint

## Prerequisites

- Python 3.11+ (or compatible version)
- MySQL server running locally or accessible remotely
- Virtual environment for Python dependencies

## Setup

1. Clone the repository and change into the project folder:

   ```powershell
   cd u:\assignment\ai_powdered_book_insight
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Configure the database in `book_ai/book_ai/settings.py`.
   The current default expects MySQL with:

   - DATABASE NAME: `books_db`
   - USER: `root`
   - PASSWORD: `toor`
   - HOST: `localhost`
   - PORT: `3306`

   If you prefer SQLite for local testing, replace the `DATABASES` block with the default SQLite configuration.

5. Create migrations and apply them:

   ```powershell
   cd book_ai
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Start the server:

   ```powershell
   python manage.py runserver
   ```

## API Documentation

The app exposes the following REST API endpoints at the project root.

### List books

- Method: `GET`
- URL: `/api/books/`
- Query parameters:
  - `page` (optional) - page number, default is `1`
- Response:
  - `data` - paginated list of books
  - `total_pages` - total number of pages
  - `current_page` - current page number

Example:

```http
GET /api/books/?page=1
```

### Book detail

- Method: `GET`
- URL: `/api/books/<id>/`
- Path parameters:
  - `id` - numeric book ID
- Response:
  - full `Book` object fields including `asin`, `title`, `author`, `rating`, `reviews`, `description`, and `url`

Example:

```http
GET /api/books/1/
```

### Chat query

- Method: `POST`
- URL: `/api/chat/`
- Body: JSON containing a `query` string
- Response:
  - `answer` - generated response from the RAG helper
  - `sources` - source information returned by the helper

Example:

```http
POST /api/chat/
Content-Type: application/json

{
  "query": "What are the best AI books for beginners?"
}
```

## Notes

- The chat endpoint uses the existing `scripts/rag.py` helper.
- `django-cors-headers` is enabled with `CORS_ALLOW_ALL_ORIGINS = True` for API access from frontend apps.
- If you need to inspect or seed book data, use the `books` model and the existing project structure.

## UI Screenshots

The `images/` folder contains the frontend UI screenshots for the project:

- `book_list.png` — book listing page
- `book_details.png` — book detail view
- `chat.png` — chat interface page

Use these images as visual references for the application UI and frontend flow.
