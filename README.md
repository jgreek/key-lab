# Key Lab

A powerful and configurable keyboard shortcut manager for macOS.

## Features

- Custom keyboard shortcuts for launching applications
- Command execution with iTerm2 integration
- CSV logging of shortcut usage
- Hot-reload configuration
- Usage statistics and analytics

## Setup

1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Run the application:
   ```bash
   python3 main.py
   ```

## Configuration

The application uses a `config.json` file for configuration.
Edit this file to customize your shortcuts and settings.

## Files

- `main.py` - Entry point
- `mac_key_listener.py` - Main orchestrator
- `config_manager.py` - Configuration management
- `csv_logger.py` - Usage logging
- `key_tracker.py` - Key combination tracking
- `command_executor.py` - Command execution
- `display_manager.py` - Display and UI

## Usage

Press Ctrl+C to exit the application.
