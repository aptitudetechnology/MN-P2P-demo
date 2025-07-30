# ModularNucleoid P2P Demo

## Overview

A Flask web application: ModularNucleoid P2P Demo (Fortran + Wasm + PeerJS)

This project was generated using the Flask App Generator Wizard.

## Features

* **Modular Structure**: Organized into blueprints for clean code management.
* **Database**: SQLite3 (lightweight, file-based database)
* **Front-end**: Responsive UI with Bootstrap 5 and Bootstrap Icons.
* **Configuration**: Environment variable based configuration using `.env`.
* **Logging**: Basic application logging to console and file.

### Selected Features:
* **User Authentication**: Yes
* **File Upload Handling**: Yes
* **REST API Endpoints**: Yes
* **Background Task Support**: Yes

## Getting Started

### 1. Clone the repository (or extract the generated app)

```bash
# If this was a git repo, you'd clone it
# git clone https://github.com/your-repo/MN-P2P-demo.git
# cd MN-P2P-demo
```

### 2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the `.env` file and adjust settings as needed:

```bash
cp .env .env.local  # Optional: create a local copy
# Edit .env with your specific settings
```

### 5. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

MN-P2P-demo/
├── app.py                 # Main application entry point
├── paths.py              # Path configurations
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── routes/              # Route blueprints
│   ├── __init__.py
│   ├── main.py         # Main routes
│   └── api.py          # API routes
├── templates/          # Jinja2 templates
│   ├── base.html
│   ├── dashboard.html
│   └── error.html
├── static/            # Static files
│   ├── css/
│   │   └── custom.css
│   ├── js/
│   │   └── app.js
│   ├── uploads/       # File uploads
│   └── images/        # Static images
├── utils/             # Utility modules
│   ├── __init__.py
│   ├── database.py    # Database utilities
│   ├── helpers.py     # Helper functions
│   └── validators.py  # Input validators
├── data/              # Data storage
│   └── backups/       # Database backups
├── config/            # Configuration files
└── logs/              # Application logs
```

## Configuration

The application uses environment variables for configuration. Key settings in `.env`:

* `FLASK_APP`: Application entry point
* `FLASK_ENV`: Environment (development/production)
* `SECRET_KEY`: Secret key for sessions
* `DATABASE_URL`: Database connection string

## Development

### Adding New Routes

1. Create route functions in `routes/main.py` or `routes/api.py`
2. Add corresponding templates in `templates/`
3. Update navigation in the base template if needed

### Database Operations

Database utilities are available in `utils/database.py`:

```python
from utils.database import get_db_connection, execute_query
```

### Styling

Custom styles go in `static/css/custom.css`. The application uses Bootstrap 5 for base styling.

## Deployment

### Using Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 app:app
```

### Environment Variables for Production

Set these environment variables in production:

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=your-database-url-here
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created by SMILHS (2025)

---

*Generated with Flask App Generator Wizard*
