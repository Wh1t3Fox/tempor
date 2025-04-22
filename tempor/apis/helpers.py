""""Helper Functions for the APIs."""

from ..exceptions import AuthorizationError

def authorized(func):
    """Enforce authentication for function."""
    def wrapper(self, *args, **kwargs):
        if self.is_authorized():
            return func(self, *args, **kwargs)
        else:
            raise AuthorizationError('Invalid API Token!')
    return wrapper



