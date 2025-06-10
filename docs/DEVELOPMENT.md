# Development Guide

This guide provides instructions for setting up a development environment and contributing to DOGEPAL.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/dogepal-hackathon.git
   cd dogepal-hackathon
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python database.py
   ```

## Running the Application

Start the Streamlit development server:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Project Structure

```
dogepal-hackathon/
├── app/                      # Main application package
│   ├── models/               # Database models
│   ├── data/                 # Data files
│   └── static/               # Static assets
├── docs/                     # Documentation
├── tests/                    # Test files
├── .env.example              # Example environment variables
├── .gitignore
├── app.py                    # Main Streamlit application
├── config.py                 # Application configuration
├── database.py               # Database setup and models
└── README.md                 # Project overview
```

## Testing

Run the test suite:

```bash
pytest
```

## Code Style

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. Before committing, please ensure your code passes:

```bash
flake8 .
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
