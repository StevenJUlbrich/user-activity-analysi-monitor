# EZ Connect Oracle Sequence

- Validation Steps:
Validation of OracleClientConfig and DatabaseConnectionConfig.
- Environment Configuration:
Setting environment variables like ORACLE_HOME, PATH, KRB5_CONFIG, and KRB5CCNAME.
Creating necessary directories and configuration files (sqlnet.ora).
- Connection Establishment:
Generating the EZ Connect string.
Connecting to the database and optionally setting the default schema.
- Query Execution:
Interaction with the database to execute queries and return results.
- Transaction Management:
Explicit steps for beginning, committing, and rolling back transactions.
- Connection Closure:
Closing the connection and logging the closure.

```mermaid
    sequenceDiagram
    autonumber
    participant User
    participant OracleKerberosConnection
    participant OracleClientConfig
    participant Database
    participant Logger
    participant Environment

    User->>OracleKerberosConnection: Initialize with config
    OracleKerberosConnection->>OracleClientConfig: Validate Oracle client configuration
    OracleClientConfig-->>OracleKerberosConnection: Validation successful
    OracleKerberosConnection->>OracleKerberosConnection: Validate database connection config
    OracleKerberosConnection->>Logger: Configure logging
    Logger-->>OracleKerberosConnection: Logging configured
    OracleKerberosConnection->>OracleKerberosConnection: Setup environment
    OracleKerberosConnection->>Environment: Configure Oracle client environment
    Environment->>Environment: Set ORACLE_HOME, PATH, KRB5_CONFIG, KRB5CCNAME
    Environment->>Environment: Create network/admin directory
    Environment->>Environment: Create sqlnet.ora file
    Environment->>OracleClientConfig: Initialize Oracle client
    OracleClientConfig-->>Environment: Initialization successful
    OracleKerberosConnection->>OracleKerberosConnection: Generate EZ Connect string
    OracleKerberosConnection->>Database: Connect using EZ Connect string
    Database-->>OracleKerberosConnection: Connection object
    OracleKerberosConnection->>OracleKerberosConnection: Check if default schema is provided
    OracleKerberosConnection->>Database: Set default schema (if provided)
    Database-->>OracleKerberosConnection: Default schema set
    OracleKerberosConnection-->>User: Return connection

    User->>OracleKerberosConnection: Execute query
    OracleKerberosConnection->>Database: Execute SQL query
    Database-->>OracleKerberosConnection: Query results
    OracleKerberosConnection-->>User: Return query results

    User->>OracleKerberosConnection: Begin transaction
    OracleKerberosConnection->>Logger: Log transaction start
    Logger-->>OracleKerberosConnection: Transaction logged

    User->>OracleKerberosConnection: Commit transaction
    OracleKerberosConnection->>Database: Commit changes
    Database-->>OracleKerberosConnection: Commit successful
    OracleKerberosConnection->>Logger: Log commit
    Logger-->>OracleKerberosConnection: Commit logged

    User->>OracleKerberosConnection: Rollback transaction
    OracleKerberosConnection->>Database: Rollback changes
    Database-->>OracleKerberosConnection: Rollback successful
    OracleKerberosConnection->>Logger: Log rollback
    Logger-->>OracleKerberosConnection: Rollback logged

    User->>OracleKerberosConnection: Close connection
    OracleKerberosConnection->>Database: Close connection
    Database-->>OracleKerberosConnection: Connection closed
    OracleKerberosConnection->>Logger: Log connection closure
    Logger-->>OracleKerberosConnection: Closure logged

```
