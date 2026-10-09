# HakimBlog

A modern, high-signal technical publication and software engineering blog built with **Django** and **Wagtail CMS**. Inspired by clean engineering publications like *Real Python*, *Baeldung*, and *GeeksforGeeks*.

---

## Features

- **Structured Knowledge Architecture**:
  - Categorized engineering tracks (Python & Django, Backend Architecture, AI & ML, Cloud & DevOps, Database Systems).
  - Multi-column topic digests, featured hero articles, and recent tutorial feeds.
- **Rich StreamField Content Modeling**:
  - Prism.js syntax-highlighted code blocks with language indicators and one-click copy.
  - Callout cards (Info, Warning, Tip, Success).
  - Downloadable resource attachments (source code archives, PDF cheatsheets).
  - Screenshots & diagram galleries.
- **Multi-Theme Engine**:
  - Persistent **Light (Technical White)**, **Dark (Navy Space)**, **Sepia (Reading Mode)**, and **System (Auto-OS)** modes with zero flash-of-unstyled-content (FOUC).
- **Interactive Community & Discussions**:
  - Threaded comment system with guest support and authenticated author badges.
  - Built-in comment moderation and approval workflow.
- **Dual Admin Control Panels**:
  - **Wagtail CMS (`/admin/`)**: Visual page tree editor, draft/publish workflows, snippets, and image/document management.
  - **Django Admin (`/django-admin/`)**: Powered by **Jazzmin** with tabbed editing forms, live theme selector, and model moderation.
- **Full-Text Search & Tag Cloud**:
  - Instant keyword filtering across tutorials, categories, and tags.

---

## Tech Stack

- **Backend**: Python 3.12+, Django 6.1+, Wagtail CMS 8.0+
- **Database**: SQLite (default) / PostgreSQL (production ready)
- **Frontend**: Vanilla Semantic HTML5 & Modern CSS Variables (no bloated utility frameworks)
- **Code Highlighting**: PrismJS
- **Admin UI**: Wagtail Admin & Django Jazzmin

---

## Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/HakimBlog.git
cd HakimBlog
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create a Superuser
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and visit:
- **Public Website**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Wagtail CMS Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Django Control Panel**: [http://127.0.0.1:8000/django-admin/](http://127.0.0.1:8000/django-admin/)

---

## Project Structure

```text
HakimBlog/
├── HakimBlog/                # Project configuration & settings
│   ├── settings/             # Base, Dev, and Production settings
│   ├── static/               # Global CSS, JS, and brand assets
│   ├── templates/            # Global templates, base layout, auth views
│   └── urls.py               # Core routing table
├── blog/                     # Blog application & models
│   ├── models.py             # BlogPage, BlogIndexPage, BlogCategory, BlogComment
│   ├── admin.py              # Django Admin registrations & inlines
│   ├── wagtail_hooks.py      # Wagtail Snippet ViewSets & menus
│   ├── views.py              # Custom auth and comment handlers
│   └── templates/blog/       # Article templates, blocks, and feeds
├── home/                     # Homepage application
│   ├── models.py             # HomePage model and curated queries
│   └── templates/home/       # Homepage layout & digests
├── search/                   # Search view & template handling
├── media/                    # User-uploaded images and documents
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## License

This project is licensed under the MIT License.
