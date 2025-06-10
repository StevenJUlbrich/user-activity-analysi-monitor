# Client Activity Monitor

A desktop application for monitoring and reporting user activity across multiple Oracle databases, designed for Security Operations Center (SOC) teams.

## Overview

The Client Activity Monitor queries multiple Oracle databases to identify users who have made all four critical changes (password, email, phone, and security token) within a 24-hour window. It generates comprehensive reports and facilitates quick incident response.

## Features

- **Multi-Database Support**: Concurrent querying across multiple Oracle databases
- **Kerberos Authentication**: Secure database connections using Kerberos
- **Real-Time Monitoring**: Live status updates during query execution
- **Comprehensive Reporting**: Excel reports with detailed user activity
- **Integration Support**: Email drafts and OneNote summary entries
- **Audit Trail**: Complete logging of who ran reports and when

## Prerequisites

- Python 3.10 or higher
- Oracle Instant Client 19c or higher
- Kerberos configuration (krb5.conf)
- Valid Kerberos ticket (kinit)
- Oracle database access with appropriate permissions

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourorg/client-activity-monitor.git
   cd client-activity-monitor
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Configure your databases in `configs/databases.yaml`

4. Run the application:
   ```bash
   poetry run python src/client_activity_monitor/main.py
   ```

## Configuration

### Application Settings (configs/app_settings.yaml)

Configure Oracle client paths and user settings:
- Oracle Instant Client directory
- Kerberos configuration file path
- Kerberos cache file path
- Your user SID

### Database Configuration (configs/databases.yaml)

```yaml
databases:
  - name: client_activity_analysis
    host: your.database.host
    port: 1521
    service_name: YOUR_SERVICE
    default_schema: AUDIT_LOGS
    sql_queries:
      - name: "Get all email changes"
        query_location: "queries/get_all_email_changes.sql"
```

## Usage

1. **Initial Setup**: Enter Oracle/Kerberos paths and save configuration
2. **Run KINIT**: Execute `kinit` in terminal to obtain Kerberos ticket
3. **Run Analysis**: Check the KINIT checkbox and click "Run Report"
4. **View Results**: Monitor progress in Database Status panel
5. **Export Report**: Use action buttons to email or copy results

## Architecture

The application follows the Model-View-Controller (MVC) pattern:
- **Model**: Database connections, query execution, data processing
- **View**: UI panels for configuration, analysis, and status
- **Controller**: Orchestrates operations between Model and View

## Troubleshooting

### Common Issues

- **ORA-01017**: Invalid credentials - check Kerberos ticket with `klist`
- **Connection Timeout**: Verify network access to database servers
- **Missing SQL Files**: Ensure queries/ directory contains all SQL files
- **No Results**: Check if users made changes within the time window

### Logs

- Application logs: Check the Logs panel in the UI
- Detailed logs: `logs/client_activity_monitor.log`

## Development

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

## License

[Your License Here]