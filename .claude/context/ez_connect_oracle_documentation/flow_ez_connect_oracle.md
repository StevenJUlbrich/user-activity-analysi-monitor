# EZ Connect Oracle Flow

This diagram represents the high-level flow of the connection process in the OracleKerberosConnection class. Let me know if you'd like to customize it further or focus on a different part of the workflow.

```mermaid
graph TD
    A[Start] --> B[Initialize OracleKerberosConnection]
    B --> C{Config Type?}
    C -->|Dictionary| D[Validate Config with Pydantic]
    C -->|DatabaseConnectionConfig| E[Use Provided Config]
    D --> F[Extract Configuration Values]
    E --> F
    F --> G[Setup Environment Variables]
    G --> H[Initialize Oracle Client]
    H --> I{Connection Type?}
    I -->|Kerberos| J[Connect using Kerberos Authentication]
    I -->|Username/Password| K[Connect using Credentials]
    I -->|Wallet| L[Connect using Wallet]
    J --> M[Set Default Schema if Provided]
    K --> M
    L --> M
    M --> N[Connection Established]
    N --> O{Operation?}
    O -->|Execute Query| P[Run SQL Query and Fetch Results]
    O -->|Transaction| Q[Begin, Commit, or Rollback Transaction]
    O -->|Connection Pool| R[Create or Use Connection Pool]
    P --> S[Return Query Results]
    Q --> T[Transaction Completed]
    R --> U[Pool Operation Completed]
    S --> V[End]
    T --> V
    U --> V
    V[End]
```
