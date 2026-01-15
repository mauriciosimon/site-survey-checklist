# Site Visit Checklist App

A web application for managing construction site visit checklists.

## Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL

## Setup

### 1. Create the Database

```bash
createdb site_checklist
```

Or via psql:
```sql
CREATE DATABASE site_checklist;
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Set custom database URL
export DATABASE_URL="postgresql://user:password@localhost/site_checklist"

# Run the server
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at http://localhost:3001

## Usage

1. Start PostgreSQL
2. Start the backend server (port 8000)
3. Start the frontend dev server (port 5173)
4. Open http://localhost:3001 in your browser

## Features

- Create, edit, and delete site visit checklists
- All fields organized by category:
  - Header Info (site name, surveyor, client details)
  - Building Specs (levels, heights, floor/ceiling types)
  - Access & Logistics (lift access, restrictions)
  - Finishes & Details (door, frame, glazing specs)
  - Project Status (dates, secured status)
  - Technical Requirements (acoustic, fire stopping)
  - Commercial (pricing, supplier notes)
  - Documentation (photos, notes)
- Search checklists by site name, client, or project
- Upload and view site photos
- Responsive design

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /checklists | List all checklists |
| GET | /checklists/{id} | Get single checklist |
| POST | /checklists | Create new checklist |
| PUT | /checklists/{id} | Update checklist |
| DELETE | /checklists/{id} | Delete checklist |
| POST | /checklists/{id}/photos | Upload photo |
