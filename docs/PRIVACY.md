# Privacy Policy

## Data Collection

DOGEPAL is designed with privacy as a core principle. By default, the application:

- **Does not collect** any personal or sensitive information
- **Does not track** user activity or behavior
- **Does not send** any data to external servers
- **Stores all data locally** on the user's machine

## Telemetry

All telemetry and analytics are **disabled by default** in the application. This is enforced through the `.windsurf.toml` configuration:

```toml
[telemetry]
enabled = false  # Disable all telemetry and data collection
track_usage = false  # Disable usage tracking

[model]
train_on_data = false  # Prevent training on user data

[privacy]
anonymize_data = true
retention_days = 0  # Don't retain any data
```

## Data Storage

All application data is stored locally in:

- **SQLite database**: `dogepal.db` in the project root
- **MLflow artifacts**: `mlruns/` directory (if MLflow tracking is enabled)
- **Environment variables**: `.env` file (not committed to version control)

## Data Processing

Any data processing happens entirely on the user's machine. No data is sent to external services unless explicitly configured by the user.

## User Control

Users have full control over their data:

1. All data is stored locally and can be deleted at any time
2. No automatic data collection or tracking
3. Clear configuration options for any data-related features

## Compliance

This application is designed to comply with:

- General Data Protection Regulation (GDPR)
- California Consumer Privacy Act (CCPA)
- Other relevant data protection regulations

## Changes to This Policy

Any changes to this privacy policy will be documented in the [CHANGELOG.md](CHANGELOG.md).

## Contact

For privacy-related questions or concerns, please open an issue in the project repository.
