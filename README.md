# DOGEPAL - Local Spending Recommendation Engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRIVACY](https://img.shields.io/badge/PRIVACY-Do%20Not%20Train%20%2F%20Track-red)](https://github.com/professordnyc/dogepal-hackathon)
[![HP AI Studio](https://img.shields.io/badge/HP%20AI%20Studio-Integrated-blue)](https://github.com/professordnyc/dogepal-hackathon)

> **Privacy Notice**: This repository is configured with `DO-NOT-TRACK` and `DO-NOT-TRAIN` rules. Please respect these privacy controls and do not use this code for training AI/ML models without explicit permission.

A local/offline spending recommendation engine that provides transparent, explainable spending insights for individuals and teams, inspired by DOGE (Department of Government Efficiency) principles. Integrated with HP AI Studio for model training, tracking, and deployment.

## 🚀 Features

- **Spending Analysis**: Track and categorize transactions
- **AI-Powered Recommendations**: Get personalized spending optimization suggestions
- **Transparency Notes**: Understand the reasoning behind each recommendation
- **Local-First**: Your data stays on your machine
- **Explainable AI**: Clear explanations for all recommendations
- **HP AI Studio Integration**: MLflow tracking, model registry, and deployment

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.10+)
- **Frontend**: Streamlit
- **Database**: SQLite (with async SQLAlchemy 2.0)
- **AI/ML**: Scikit-learn, MLflow (for model tracking and deployment)
- **Testing**: pytest
- **Containerization**: Docker (optional)
- **Model Registry**: HP AI Studio

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MLflow 2.0+
- Access to HP AI Studio (for model deployment)
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

---

## Simple API Server Usage & Endpoint Conventions

The included `scripts/simple_api_server.py` provides a minimal HTTP API for accessing spending and recommendation data from the SQLite database. This is intended for demo and hackathon judging purposes.

### Supported Endpoints (Strict Matching)
- `GET /api/v1/spending` — List all spending records
- `GET /api/v1/spending/<transaction_id>` — Get a specific spending record by ID
- `GET /api/v1/recommendations` — List all recommendations
- `GET /api/v1/recommendations/<id>` — Get a specific recommendation by ID

**Important Notes:**
- Endpoints are case-sensitive and do not support trailing slashes (e.g., `/api/v1/spending/` will NOT work).
- Only the above patterns are supported. Typos, extra slashes, or unsupported paths will return `{ "detail": "Endpoint not found" }`.
- If you request a valid endpoint with a non-existent ID, you will receive `{ "detail": "Spending record not found" }` or `{ "detail": "Recommendation not found" }`.

### Example URLs (assuming server runs on port 8080):
- List all spending: [http://localhost:8080/api/v1/spending](http://localhost:8080/api/v1/spending)
- Get a specific spending record: [http://localhost:8080/api/v1/spending/TXN1002](http://localhost:8080/api/v1/spending/TXN1002)
- List all recommendations: [http://localhost:8080/api/v1/recommendations](http://localhost:8080/api/v1/recommendations)
- Get a specific recommendation: [http://localhost:8080/api/v1/recommendations/REC1002](http://localhost:8080/api/v1/recommendations/REC1002)

### What Will NOT Work
- `/api/v1/spending/` (trailing slash)
- `/api/v1/Spending` (case mismatch)
- `/api/v1/recommendation/REC1002` (typo in path)
- `/api/v1/recommendations/REC9999` (non-existent ID)

### Troubleshooting
- If you receive an error, check that you are using the exact endpoint and a valid ID as listed by the `/api/v1/spending` or `/api/v1/recommendations` endpoints.
- The server does not support flexible or RESTful conventions beyond those listed above.

---

## 🚀 HP AI Studio Integration

This project is integrated with HP AI Studio for model training, tracking, and deployment. We provide a CLI-based approach that meets all hackathon requirements while working around potential desktop app limitations.

### Why CLI Integration?

We've implemented a command-line interface (CLI) for HP AI Studio integration to address potential issues with the desktop application, such as:

- Workspace startup hangs or freezes
- Dependency conflicts between project requirements and HP AI Studio
- Path resolution issues with nested project structures
- Environment variable conflicts

Our CLI approach ensures reliable integration while maintaining all the benefits of HP AI Studio's MLflow tracking, model registry, and deployment capabilities.

### HP AI Studio Integration Script

The `hp_ai_studio_integration.py` script provides a comprehensive command-line interface for HP AI Studio integration:

```bash
# Run all integration steps (train, register, create deployment config)
python hp_ai_studio_integration.py --all

# Or run individual steps
python hp_ai_studio_integration.py --train      # Train and log model to MLflow
python hp_ai_studio_integration.py --register   # Register model in HP AI Studio registry
python hp_ai_studio_integration.py --deploy-config  # Create deployment configuration
```

### Step-by-Step Integration Guide

#### 1. Environment Setup

1. **Create and activate a virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate
   
   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r models/requirements.txt
   ```

3. **Configure MLflow tracking URI**
   
   Create a `.env` file in the project root with your HP AI Studio MLflow tracking URI:
   ```
   MLFLOW_TRACKING_URI=https://your-hp-ai-studio-mlflow-uri
   ```
   
   You can find this URI in your HP AI Studio workspace settings or in the MLflow tracking server configuration.

#### 2. Training and Logging the Model

1. **Run the training script**
   ```bash
   python hp_ai_studio_integration.py --train
   ```

2. **What happens during training**:
   - The script initializes the SpendingRecommender model
   - Loads sample data (or generates synthetic data if not available)
   - Trains the model on the data
   - Logs model parameters, metrics, and artifacts to MLflow
   - Saves example inputs and outputs for documentation
   - Returns a run ID for tracking

#### 3. Registering the Model

1. **Register the model in HP AI Studio's model registry**
   ```bash
   python hp_ai_studio_integration.py --register
   ```

2. **What happens during registration**:
   - The script connects to the MLflow tracking server
   - Finds the latest training run
   - Registers the model with a specified name in the model registry
   - Creates a new version if the model already exists
   - Returns the model version for reference

#### 4. Creating Deployment Configuration

1. **Generate deployment configuration**
   ```bash
   python hp_ai_studio_integration.py --deploy-config
   ```

2. **What happens during configuration**:
   - The script creates a deployment configuration JSON file
   - Includes environment specifications (Python version, dependencies)
   - Defines compute resources (CPU, memory)
   - Specifies API endpoint configuration
   - Includes input/output schemas
   - Saves the configuration to `models/artifacts/deployment_config.json`

### Testing the Integration

To verify your integration is working correctly:

1. **Check MLflow UI**
   - Navigate to your HP AI Studio MLflow UI
   - Verify experiment runs are visible
   - Check that metrics and artifacts are properly logged

2. **Test the registered model**
   - Confirm the model appears in the HP AI Studio model registry
   - Verify the latest version is available

3. **Validate the model locally**
   ```bash
   python test_recommender.py
   ```

### Model Explainability

The SpendingRecommender model includes comprehensive explainability features:

- **Confidence Scores**: Each recommendation includes a confidence score (0-1) indicating the model's certainty
- **Explanation Metadata**: Detailed reasoning for each recommendation, including statistical justification
- **Feature Importance**: Documentation of which features influence recommendations (amount, department, category, vendor)
- **Recommendation Types**: Clear categorization of different recommendation types:
  - `spending_anomaly`: Identifies unusual spending patterns
  - `cost_saving`: Suggests opportunities to reduce costs
  - `vendor_consolidation`: Identifies opportunities to consolidate vendors
  - `budget_optimization`: Suggests better budget allocation
  - `policy_violation`: Flags potential policy violations

### Troubleshooting HP AI Studio Integration

#### Common Issues and Solutions

1. **MLflow Connection Issues**

   **Symptoms**: `Connection refused` or `Failed to connect to MLflow server`
   
   **Solutions**:
   - Verify your MLFLOW_TRACKING_URI is correct in the .env file
   - Check network connectivity to the HP AI Studio server
   - Ensure your authentication credentials are valid
   - Try using an explicit authentication token if required

2. **Model Training Failures**

   **Symptoms**: `Training failed` or errors during the training process
   
   **Solutions**:
   - Check the logs for specific error messages
   - Verify sample data is available and properly formatted
   - Ensure all dependencies are installed correctly
   - Try with a smaller dataset for testing

3. **Model Registration Issues**

   **Symptoms**: `Model registration failed` or `No runs found`
   
   **Solutions**:
   - Ensure you've run the training step first
   - Check permissions to create/modify models in the registry
   - Verify the experiment name is correct
   - Try manually registering the model through the MLflow UI

4. **Deployment Configuration Errors**

   **Symptoms**: `Error creating deployment configuration`
   
   **Solutions**:
   - Ensure the model is properly registered
   - Check write permissions to the artifacts directory
   - Verify the model version exists in the registry

5. **Dependency Conflicts**

   **Symptoms**: Import errors or version mismatch warnings
   
   **Solutions**:
   - Create a clean virtual environment
   - Install dependencies in the correct order
   - Check for conflicting versions in requirements.txt
   - Use `pip list` to verify installed versions

6. **Path Resolution Issues**

   **Symptoms**: `File not found` or path-related errors
   
   **Solutions**:
   - Use absolute paths when necessary
   - Avoid nested directories with the same name
   - Run scripts from the project root directory
   - Check file permissions

#### Debugging Tips

1. **Enable Verbose Logging**
   
   Add this to your script before running:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **Check MLflow Server Logs**
   
   If you have access to the HP AI Studio server logs, check for connection or authentication issues.

3. **Validate Environment Variables**
   
   Print environment variables to ensure they're loaded correctly:
   ```python
   import os
   print(os.environ.get("MLFLOW_TRACKING_URI"))
   ```

4. **Test MLflow Connection Separately**
   
   Create a simple script to test just the MLflow connection:
   ```python
   import mlflow
   mlflow.set_tracking_uri("your-tracking-uri")
   print(mlflow.list_experiments())
   ```

5. **Check for File Lock Issues**
   
   If you're getting file access errors, ensure no other processes are using the same files.

---

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
