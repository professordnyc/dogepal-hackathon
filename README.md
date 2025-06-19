# DOGEPAL

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

AI-Powered Government Spending Analysis Tool

## Overview

DOGEPAL is a streamlined, privacy-focused tool for analyzing and optimizing government spending. This version features a simple Streamlit interface with a SQLite backend, designed for local development and analysis.

This project is a streamlined version of a full-featured DOGEPAL project in development. This prototype was developed for the 2025 NVIDIA/HP AI Studio hackathon.

> **Privacy First**: This project is configured with telemetry disabled and no data collection. See our [privacy policy](docs/PRIVACY.md) for details.

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/professordnyc/dogepal-hackathon.git
   cd dogepal-hackathon
   ```

2. **Set up the environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure the application**
   ```bash
   # Copy and edit the example environment file
   copy .env.example .env
   ```

4. **Initialize the database**
   ```bash
   python database.py
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser** to `http://localhost:8501`

## Documentation

For more detailed information, please refer to:

- [Development Guide](docs/DEVELOPMENT.md) - Setup and contribution guidelines
- [System Architecture](docs/ARCHITECTURE.md) - Technical design and components
- [Changelog](docs/CHANGELOG.md) - Version history and changes
- [Privacy Policy](docs/PRIVACY.md) - Data handling and privacy practices

## Features

- **Spending Dashboard**: Visualize and analyze government spending
- **AI-Powered Insights**: Get automated recommendations
- **Local-First**: Runs entirely offline with SQLite
- **Privacy-Focused**: No telemetry or data collection
- **Open Source**: MIT Licensed for transparency and community contributions

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.9+
- **Database**: SQLite with SQLAlchemy ORM
- **AI/ML**: Scikit-learn, MLflow (optional)
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Sample Data

Sample data can be loaded using the included script:

```bash
python scripts/load_sample_data.py
```

This will populate the database with example spending records and recommendations for demonstration purposes.

## API Access

The application provides a simple REST API for programmatic access:

### Endpoints

- `GET /api/v1/spending` - List all spending records
- `GET /api/v1/spending/{transaction_id}` - Get a specific spending record
- `GET /api/v1/recommendations` - List all recommendations
- `GET /api/v1/recommendations/{id}` - Get a specific recommendation

Example usage with `curl`:

```bash
# List all spending records
curl http://localhost:8501/api/v1/spending

# Get a specific recommendation
curl http://localhost:8501/api/v1/recommendations/1
   
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

## Development

For development setup and contribution guidelines, please see the [Development Guide](docs/DEVELOPMENT.md).

## Troubleshooting

### Database Connection Issues
- Ensure the SQLite database file exists and is writable
- Check that no other process has locked the database
- Verify the database path in your `.env` file

### Missing Dependencies
If you encounter missing module errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Port Already in Use
If port 8501 is already in use, you can change it by setting the `PORT` environment variable:

```bash
# Windows
set PORT=8502
streamlit run app.py

# macOS/Linux
PORT=8502 streamlit run app.py
```

## Getting Help

For additional help or to report issues, please open an issue on our [GitHub repository](https://github.com/professordnyc/dogepal-hackathon/issues).

## Contributing

We welcome contributions! Please see our [Development Guide](docs/DEVELOPMENT.md) for details on how to contribute to this project.
