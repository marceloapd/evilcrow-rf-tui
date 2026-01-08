"""
Main entry point for Evil Crow RF TUI
"""
import sys
from .app import EvilCrowApp


def main():
    """Main entry point"""
    app = EvilCrowApp()
    app.run()


if __name__ == "__main__":
    main()
