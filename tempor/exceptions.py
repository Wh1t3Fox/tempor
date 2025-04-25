"""Custom Exception Handlers."""

class AuthorizationError(Exception):
    """Catch and Throw Auth Errors."""

    pass

class PackerConfigurationError(Exception):
    """Throw Config related error for Packer."""

    pass

class UnsupportedProviderError(Exception):
    """Thrown when the provider is not supported."""

    pass
