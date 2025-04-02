# FastAPI Web Server for Corporate Actions and Symbology Changes

## Purpose

This project is a Python web server built using the FastAPI framework. It is designed to administer corporate actions and symbology changes for equities and other financial securities.

## Description

The main functionalities of this web server include:
- Managing corporate actions such as dividends, stock splits, mergers, etc.
- Handling symbology changes for financial securities.
- Providing endpoints to retrieve and create symbols and corporate actions.
- Ensuring data consistency and integrity through validation and error handling.
- Supporting asynchronous operations for improved performance.
- Utilizing SQLModel for database interactions.

## Features

- **Corporate Actions Management**: Create, retrieve, and manage corporate actions like dividends, stock splits, and mergers.
- **Symbology Management**: Handle changes in symbology for financial securities.
- **Data Validation**: Ensure data consistency and integrity through comprehensive validation and error handling.
- **Asynchronous Operations**: Leverage FastAPI's asynchronous capabilities for better performance.
- **Database Integration**: Use SQLModel for efficient database interactions.

## Installation

As easy as:

```bash
uv run fastapi dev --reload
```

## Note
This is a toy project created for the purpose of learning and experimenting with FastAPI. It is not intended for production use.
