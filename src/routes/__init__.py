# Routes package initialization
from .base import base_router
from .auth import auth_router
from .data import data_router

__all__ = ['base_router', 'auth_router', 'data_router']