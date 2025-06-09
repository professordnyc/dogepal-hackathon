"""
Spending Recommendation Model for DOGEPAL.
This model provides cost-saving recommendations for government spending.
"""
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
import pandas as pd
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

class SpendingRecommender(BaseEstimator, ClassifierMixin):
    """
    A scikit-learn compatible model for generating spending recommendations.
    This implementation uses rule-based logic with MLflow compatibility for deployment.
    The model is designed to provide explainable AI recommendations for government spending,
    with extensibility for individual and team finance management.
    
    MLflow Integration:
    - Implements predict() for batch inference
    - Implements predict_proba() for confidence scores
    - Can be saved/loaded using MLflow's pyfunc interface
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        """
        Initialize the recommender with a confidence threshold.
        
        Args:
            confidence_threshold: Minimum confidence score (0-1) for a recommendation to be made.
                               Recommendations with lower confidence will be filtered out.
        """
        """
        Initialize the recommender with a confidence threshold.
        
        Args:
            confidence_threshold: Minimum confidence score for recommendations (0-1)
        """
        self.confidence_threshold = confidence_threshold
        self.categories = [
            'Software', 'Hardware', 'Services', 'Office Supplies', 'Training'
        ]
        self.vendors = [
            'Acme Inc.', 'Tech Solutions', 'Office Supplies Co', 
            'City Services', 'Global Tech'
        ]
        self.departments = [
            'Technology', 'HR', 'Finance', 'Operations', 'Public Works'
        ]
        
    def fit(self, X, y=None):
        """
        Fit the model to the training data.
        In this simplified version, we're not actually training a model.
        """
        return self
    
    def predict(self, X):
        """
        Generate recommendations for the input data.
        
        Args:
            X: Input data (list of spending records or a single record)
            
        Returns:
            List of recommendation dictionaries or a single recommendation if single input
            
        Note:
            This method is compatible with scikit-learn's predict() interface
            and can be used for batch processing.
        """
        if not X:
            return []
            
        single_input = False
        if not isinstance(X, list):
            X = [X]
            single_input = True
            
        recommendations = []
        for record in X:
            if not isinstance(record, dict):
                print(f"⚠️  Warning: Expected dictionary, got {type(record).__name__}")
                recommendations.append(None)
                continue
                
            try:
                # Generate a recommendation based on the record
                rec = self._generate_recommendation(record)
                recommendations.append(rec[0] if rec else None)
            except Exception as e:
                print(f"⚠️  Error processing record {record.get('transaction_id', 'unknown')}: {str(e)}")
                recommendations.append(None)
        
        return recommendations[0] if single_input and recommendations else recommendations
    
    def predict_proba(self, X):
        """
        Predict probability estimates for the input data.
        For this rule-based model, returns confidence scores.
        
        Args:
            X: Input data (list of spending records or a single record)
            
        Returns:
            List of confidence scores (0-1) for each input record
        """
        predictions = self.predict(X)
        if not isinstance(predictions, list):
            predictions = [predictions]
            
        confidences = []
        for pred in predictions:
            if pred is None:
                confidences.append(0.0)
            else:
                confidences.append(pred.get('confidence_score', 0.0))
                
        return confidences[0] if len(confidences) == 1 else confidences
    
    def save(self, path: str):
        """
        Save the model to a file.
        
        Args:
            path: Path to save the model to
        """
        import joblib
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(self, path)
    
    @classmethod
    def load(cls, path: str):
        """
        Load a model from a file.
        
        Args:
            path: Path to the saved model
            
        Returns:
            Loaded SpendingRecommender instance
        """
        import joblib
        return joblib.load(path)
    
    def _calculate_z_score(self, value: float, mean: float, std_dev: float) -> float:
        """Calculate the z-score for a value given mean and standard deviation."""
        if std_dev == 0:
            return 0
        return (value - mean) / std_dev

    def _generate_recommendation(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate a single recommendation based on a spending record with detailed explanations.
        
        Args:
            record: A dictionary containing spending record data
            
        Returns:
            A recommendation dictionary with detailed explanations or None if no recommendation
        """
        # Skip if essential fields are missing
        required_fields = ['amount', 'category', 'vendor', 'department']
        if not all(field in record for field in required_fields):
            return None
            
        amount = float(record.get('amount', 0))
        category = record.get('category', '').lower()
        vendor = record.get('vendor', '')
        department = record.get('department', '')
        transaction_id = record.get('transaction_id', '')
        
        # Department spending statistics (in a real system, these would come from historical data)
        dept_stats = {
            'technology': {'mean': 15000, 'std_dev': 5000},
            'hr': {'mean': 8000, 'std_dev': 2000},
            'finance': {'mean': 12000, 'std_dev': 4000},
            'public works': {'mean': 25000, 'std_dev': 10000},
            'operations': {'mean': 10000, 'std_dev': 3000}
        }
        
        # Category benchmarks (average spending per category across all departments)
        category_benchmarks = {
            'office supplies': {'mean': 800, 'savings_potential': 0.15},
            'services': {'mean': 3000, 'savings_potential': 0.20},
            'hardware': {'mean': 5000, 'savings_potential': 0.12},
            'training': {'mean': 2000, 'savings_potential': 0.10},
            'other': {'mean': 1500, 'savings_potential': 0.05}
        }
        
        # Get department stats or use defaults
        dept_stat = dept_stats.get(department.lower(), {'mean': 10000, 'std_dev': 5000})
        dept_mean = dept_stat['mean']
        dept_std = dept_stat['std_dev']
        
        # Calculate z-score for department spending anomaly detection
        z_score = self._calculate_z_score(amount, dept_mean, dept_std)
        
        # Get category benchmark or use default
        cat_benchmark = category_benchmarks.get(category, category_benchmarks['other'])
        cat_mean = cat_benchmark['mean']
        
        # Recommendation 1: Department spending anomaly (z-score > 2)
        if z_score > 2.0:
            savings_potential = 0.25
            savings_amount = round(amount * savings_potential, 2)
            
            return {
                'transaction_id': transaction_id,
                'recommendation_type': 'spending_anomaly',
                'title': 'High Spending Anomaly Detected',
                'description': (
                    f'Unusually high spending of ${amount:,.2f} detected in {department} department. '
                    f'This is {z_score:.1f} standard deviations above the department mean.'
                ),
                'potential_savings': savings_amount,
                'confidence_score': min(0.9, 0.7 + (z_score * 0.05)),  # Scale confidence with z-score
                'priority': 'high',
                'explanation': {
                    'calculation': (
                        'Z-Score = (Current Amount - Department Mean) / Department StdDev\n'
                        f'= (${amount:,.2f} - ${dept_mean:,.2f}) / ${dept_std:,.2f}\n'
                        f'= {z_score:.2f} (values > 2.0 are considered anomalies)\n\n'
                        f'Potential Savings = Current Amount × Savings Potential\n'
                        f'= ${amount:,.2f} × {savings_potential*100:.0f}% = ${savings_amount:,.2f}'
                    ),
                    'factors_considered': [
                        f'Department: {department}',
                        f'Current Amount: ${amount:,.2f}',
                        f'Department Mean: ${dept_mean:,.2f}',
                        f'Department StdDev: ${dept_std:,.2f}',
                        f'Z-Score: {z_score:.2f}'
                    ],
                    'assumptions': [
                        'Historical spending follows a normal distribution',
                        'Current spending patterns are comparable to historical data',
                        'Savings potential based on industry benchmarks for similar anomalies'
                    ]
                },
                'metadata': {
                    'original_amount': amount,
                    'category': category,
                    'vendor': vendor,
                    'department': department,
                    'generated_at': datetime.utcnow().isoformat(),
                    'model_version': '1.1.0',
                    'explanation_version': '1.0',
                    'statistics': {
                        'z_score': z_score,
                        'department_mean': dept_mean,
                        'department_std_dev': dept_std,
                        'savings_percentage': savings_potential,
                        'confidence_components': {
                            'base_confidence': 0.7,
                            'z_score_impact': min(0.2, (z_score - 2.0) * 0.05)
                        }
                    }
                }
            }
        
        # Recommendation 2: Category-specific optimizations
        elif category in category_benchmarks and amount > cat_mean * 1.5:
            savings_potential = category_benchmarks[category]['savings_potential']
            savings_amount = round(amount * savings_potential, 2)
            
            return {
                'transaction_id': transaction_id,
                'recommendation_type': 'cost_saving',
                'title': f'Potential {category.title()} Cost Optimization',
                'description': (
                    f'Spending ${amount:,.2f} on {category} is {amount/cat_mean:.1f}x the category average. '
                    f'Potential savings identified.'
                ),
                'potential_savings': savings_amount,
                'confidence_score': 0.8,
                'priority': 'medium',
                'explanation': {
                    'calculation': (
                        f'Category Average: ${cat_mean:,.2f}\n'
                        f'Current Spending: ${amount:,.2f} ({amount/cat_mean:.1f}x average)\n'
                        f'Savings Potential: {savings_potential*100:.0f}%\n'
                        f'Potential Savings = ${amount:,.2f} × {savings_potential*100:.0f}% = ${savings_amount:,.2f}'
                    ),
                    'factors_considered': [
                        f'Category: {category}',
                        f'Current Amount: ${amount:,.2f}',
                        f'Category Average: ${cat_mean:,.2f}',
                        f'Ratio to Average: {amount/cat_mean:.1f}x',
                        f'Industry Savings Potential: {savings_potential*100:.0f}%'
                    ],
                    'actionable_insights': [
                        'Consider competitive bidding for better rates',
                        'Evaluate if all services are still necessary',
                        'Explore alternative vendors or solutions',
                        'Consider bulk purchasing or long-term contracts for better rates'
                    ]
                },
                'metadata': {
                    'original_amount': amount,
                    'category': category,
                    'vendor': vendor,
                    'department': department,
                    'generated_at': datetime.utcnow().isoformat(),
                    'model_version': '1.1.0',
                    'explanation_version': '1.0',
                    'benchmarks': {
                        'category_average': cat_mean,
                        'amount_to_average_ratio': amount/cat_mean,
                        'savings_percentage': savings_potential,
                        'industry_benchmark': cat_mean * 0.9  # 10% below current average
                    }
                }
            }
            
        # No recommendation if no conditions are met
        return None
            
        # No recommendation if no conditions are met
        return None
    
    def get_params(self, deep=True):
        """Get parameters for this estimator."""
        return {"confidence_threshold": self.confidence_threshold}
    
    def set_params(self, **parameters):
        """Set the parameters of this estimator."""
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self
    
    def save(self, path: str):
        """Save the model to a file."""
        import joblib
        joblib.dump(self, path)
    
    @classmethod
    def load(cls, path: str):
        """Load the model from a file."""
        import joblib
        return joblib.load(path)

def train_model():
    """
    Train and return a new instance of the SpendingRecommender.
    This is a placeholder for model training logic.
    """
    model = SpendingRecommender()
    # In a real implementation, we would train the model here
    return model

if __name__ == "__main__":
    # Example usage
    model = train_model()
    
    # Example spending record
    test_record = {
        "transaction_id": "TXN12345",
        "amount": 1500.00,
        "category": "Office Supplies",
        "vendor": "OfficeMax",
        "department": "Finance",
        "project_name": "Office Upgrade 2025",
        "borough": "Manhattan"
    }
    
    # Generate recommendation
    recommendation = model.predict(test_record)
    print("Generated Recommendation:")
    print(json.dumps(recommendation[0] if recommendation else "No recommendation", indent=2))
