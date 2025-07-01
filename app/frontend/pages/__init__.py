"""Frontend pages package."""

# Import all page modules to register routes
from . import home, products, cart, checkout, admin, auth

__all__ = ["home", "products", "cart", "checkout", "admin", "auth"]