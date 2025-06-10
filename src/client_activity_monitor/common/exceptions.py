class ClientActivityMonitorError(Exception):
    """Base exception for application errors."""
    pass

class ConfigurationError(ClientActivityMonitorError):
    """Configuration-related errors."""
    pass

class DatabaseConnectionError(ClientActivityMonitorError):
    """Database connection errors."""
    pass

class QueryExecutionError(ClientActivityMonitorError):
    """Query execution errors."""
    pass

class ReportGenerationError(ClientActivityMonitorError):
    """Report generation errors."""
    pass

class ExternalIntegrationError(ClientActivityMonitorError):
    """Email/OneNote integration errors."""
    pass