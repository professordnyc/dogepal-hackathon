# DOGEPAL Spending Recommendation Model

This directory contains the machine learning model for generating cost-saving recommendations for government spending in the DOGEPAL application.

## Model Overview

- **Name**: Spending Recommender
- **Type**: Rule-based recommendation system
- **Purpose**: Identify potential cost savings in government spending
- **Input**: Spending records with amount, category, vendor, and department
- **Output**: Actionable recommendations with estimated savings

## Model Features

- **Recommendation Types**:
  - Cost savings opportunities
  - Vendor consolidation
  - Spending anomalies detection
  - Budget optimization

- **Key Metrics**:
  - Confidence scores for each recommendation
  - Estimated potential savings
  - Priority levels (high/medium/low)

## Getting Started

### Prerequisites

- Python 3.8+
- Dependencies listed in `requirements.txt`

### Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Training the Model

To train and save the model:

```bash
python -m models.train
```

This will create a `model_artifacts` directory containing:
- `spending_recommender.joblib`: The trained model
- `model_card.json`: Model metadata and schema information

### Testing the Model

To test the model with sample data:

```bash
python -m models.test_model
```

## Model Deployment

### HP AI Studio Integration

This model is designed to be deployed to HP AI Studio. Follow these steps to deploy:

1. **Package the Model**:
   Ensure the model artifacts are in the `model_artifacts` directory.

2. **Create a Deployment Package**:
   ```bash
   # Install the HP AI Studio SDK if needed
   pip install hpe-ai-studio-sdk
   
   # Create a deployment package
   python -m hpe_ai_studio_sdk package create \
     --name "dogepal-spending-recommender" \
     --version "1.0.0" \
     --model-path model_artifacts/spending_recommender.joblib \
     --handler spending_recommender:SpendingRecommender
   ```

3. **Deploy to HP AI Studio**:
   Follow the HP AI Studio documentation to deploy the packaged model to your workspace.

## Model API

The model exposes the following interface:

### `predict(record: Dict) -> List[Dict]`

Generate recommendations for a single spending record.

**Parameters:**
- `record`: Dictionary containing spending record data

**Returns:**
- List of recommendation dictionaries, or empty list if no recommendations

### `save(path: str) -> None`

Save the model to a file.

**Parameters:**
- `path`: Path to save the model file

### `@classmethod load(path: str) -> SpendingRecommender`

Load a saved model from file.

**Parameters:**
- `path`: Path to the saved model file

**Returns:**
- Loaded SpendingRecommender instance

## Model Card

For detailed information about the model's performance, limitations, and intended use, see `model_card.json` after training.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
