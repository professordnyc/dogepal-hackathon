# DOGEPAL - Local Spending Recommendation Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRIVACY](https://img.shields.io/badge/PRIVACY-Do%20Not%20Train%20%2F%20Track-red)](https://github.com/professordnyc/dogepal-hackathon)

> **Privacy Notice**: This repository is configured with `DO-NOT-TRACK` and `DO-NOT-TRAIN` rules. Please respect these privacy controls and do not use this code for training AI/ML models without explicit permission.

A local/offline spending recommendation engine that provides transparent, explainable spending insights for individuals and teams, inspired by DOGE (Department of Government Efficiency) principles.

## 🚀 Features

- **Spending Analysis**: Track and categorize transactions
- **AI-Powered Recommendations**: Get personalized spending optimization suggestions
- **Transparency Notes**: Understand the reasoning behind each recommendation
- **Local-First**: Your data stays on your machine
- **Explainable AI**: Clear explanations for all recommendations

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Streamlit
- **Database**: SQLite (with async SQLAlchemy 2.0)
- **AI/ML**: Scikit-learn, XGBoost (for recommendations)
- **Testing**: pytest
- **Containerization**: Docker (optional)

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/professordnyc/dogepal-hackathon.git
   cd dogepal-hackathon
   ```

2. **Set up a virtual environment**
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Sample Data Generation

The project includes a script to generate realistic sample data for testing and demonstration purposes.

### Generating Sample Data

1. **Run the data generation script**:
   ```bash
   python scripts/generate_sqlite_direct.py
   ```

2. **What's included**:
   - 100 realistic spending records with NYC government context
   - 71 AI-powered recommendations
   - Sample data includes:
     - NYC boroughs and departments
     - Various spending categories and vendors
     - Different recommendation types with confidence scores

3. **Customization**:
   - Edit `scripts/generate_sqlite_direct.py` to modify data generation parameters
   - Adjust the number of records by changing the count parameter
   - Modify the random seed for reproducible results

### Database Schema

The sample data populates two main tables:

1. **spending**: Contains transaction records with details like amount, vendor, and category
2. **recommendation**: Contains AI-generated recommendations linked to spending records

## 🚀 Running the Application
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python -m app.db.init_db
   ```

6. **Run the backend server**
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Run the frontend** (in a new terminal)
   ```bash
   cd frontend
   streamlit run app.py
   ```

## 📚 Documentation

- [API Documentation](http://localhost:8000/docs) (after starting the backend)
- [User Guide](docs/user_guide/README.md)
- [Developer Guide](docs/developer_guide.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by DOGE (Department of Government Efficiency) principles
- Built for the HP AI Studio Hackathon
