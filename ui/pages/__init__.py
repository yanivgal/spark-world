"""
UI Pages Package

Page-level logic and coordination for the Spark-World application.
"""

from .setup_page import render_setup_page
from .game_page import render_game_page

__all__ = [
    'render_setup_page',
    'render_game_page'
] 