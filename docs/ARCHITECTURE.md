# System Architecture

This document outlines the high-level architecture and design decisions for the DOGEPAL application.

## Overview

DOGEPAL is built with a simple, modular architecture designed for local development and deployment. The application follows a traditional three-tier architecture:

1. **Presentation Layer**: Streamlit-based web interface
2. **Application Layer**: Python business logic
3. **Data Layer**: SQLite database with SQLAlchemy ORM

## Components

### 1. Frontend (Streamlit)

- **app.py**: Main entry point for the Streamlit application
- **Components**:
  - Dashboard: Main overview of spending data
  - Spending Analysis: Detailed transaction views
  - Recommendations: AI-powered cost-saving suggestions

### 2. Backend (Python)

- **config.py**: Application configuration and environment variables
- **database.py**: Database connection and session management
- **app/models/**: SQLAlchemy data models
  - `spending.py`: Spending and recommendation models

### 3. Data Storage

- **SQLite Database**: Local file-based storage (dogepal.db)
- **MLflow**: Optional model tracking and management

## Data Flow

1. User interacts with the Streamlit interface
2. Streamlit calls appropriate Python functions
3. Functions interact with the database through SQLAlchemy models
4. Results are processed and returned to the UI
5. Streamlit updates the interface with new data

## Design Decisions

### Technology Choices

- **Streamlit**: Chosen for rapid UI development and data visualization
- **SQLite**: Lightweight, file-based database for local development
- **SQLAlchemy**: ORM for database interactions and migrations
- **MLflow**: For model tracking and management

### Security Considerations

- All sensitive configuration is stored in environment variables
- Database connection strings are not hardcoded
- Input validation is performed at the Streamlit layer

## Future Considerations

- Potential migration to a client-server architecture if needed
- Support for additional database backends (PostgreSQL, MySQL)
- API layer for third-party integrations
- User authentication and authorization

## Dependencies

See [requirements.txt](../requirements.txt) for a complete list of dependencies.
