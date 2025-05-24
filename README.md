# Fitgent 2.0 Database Setup

This document provides instructions for setting up and connecting to the PostgreSQL database for Fitgent 2.0.

## Prerequisites

- PostgreSQL server installed and running.
- Python 3 installed.
- `psycopg2-binary` Python package.

## Database and Table Creation

The database `fitgent_db` and table `user_health_data` are created automatically by the setup process. The table schema is as follows:

- `user_id`: INT
- `date`: DATE
- `steps`: INT
- `sleep_hours`: FLOAT
- `heart_rate_avg`: FLOAT
- `stress_score`: INT
- `calories_burned`: FLOAT

## Connecting to the Database

A Python script `db_connect.py` is provided to demonstrate how to connect to the database.

### 1. Install `psycopg2-binary`

If you haven't already, install the `psycopg2-binary` package using pip:

```bash
pip install psycopg2-binary
```

### 2. Run the Connection Script

Execute the `db_connect.py` script to test the connection:

```bash
python db_connect.py
```

If the connection is successful, you will see the message "Successfully connected to the database!".

### 3. Integrating with Flask

To connect to the database from your Flask application, you can adapt the `connect_to_db()` function from `db_connect.py`. Ensure that you have the `psycopg2-binary` package installed in your Flask application's environment.

**Example (inside your Flask app):**

```python
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="fitgent_db",
        user="postgres",  # Replace with your PostgreSQL username if different
        password="",  # Replace with your PostgreSQL password if you set one
        host="localhost",
        port="5432"
    )
    return conn

# Example usage in a Flask route
# from flask import Flask
# app = Flask(__name__)
#
# @app.route('/test-db')
# def test_db():
#     conn = None
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor()
#         cur.execute('SELECT version();')
#         db_version = cur.fetchone()
#         cur.close()
#         return f"Database version: {db_version}"
#     except (Exception, psycopg2.Error) as error:
#         return f"Error while connecting to PostgreSQL: {error}"
#     finally:
#         if conn:
#             conn.close()
```

Remember to handle database connections and cursors properly, including closing them after use, to prevent resource leaks.

## Deployment

This section outlines how to deploy the Fitgent 2.0 Flask application.

### 1. Overview

Fitgent 2.0 is a Flask application. It can be deployed to various Platform-as-a-Service (PaaS) providers like Heroku or Render, or any server environment that can host Python WSGI applications (e.g., using Gunicorn or uWSGI behind a web server like Nginx).

### 2. Prerequisites for Deployment

*   **PostgreSQL Database:** A PostgreSQL database accessible by your deployment environment is required. Most PaaS providers offer this as an add-on, or you can use an externally hosted database.
*   **Git:** For version control and for deploying to most PaaS platforms.

### 3. Key Files for Deployment

*   **`requirements.txt`:** This file lists all the Python dependencies (e.g., Flask, psycopg2-binary, requests, gunicorn). When deploying to a PaaS, the platform typically reads this file and installs these dependencies automatically.
*   **`Procfile`:** This file specifies the commands that are executed by the platform to start your application. For Fitgent 2.0, it tells the platform to use Gunicorn to serve the Flask app (`app:app` refers to the `app` object within the `app.py` file).

### 4. Environment Variables Setup

For security and proper configuration, Fitgent 2.0 relies on environment variables. These must be set in your deployment environment (e.g., through the PaaS dashboard or CLI). **Do not hardcode sensitive credentials in your codebase.**

The following environment variables need to be configured:

*   `DB_HOST`: The hostname or IP address of your PostgreSQL database server.
*   `DB_PORT`: The port number for your PostgreSQL database (usually `5432`).
*   `DB_USER`: The username for connecting to your PostgreSQL database.
*   `DB_PASSWORD`: The password for the specified database user.
*   `DB_NAME`: The name of the database to use (e.g., `fitgent_db`).
*   `NEWS_API_KEY`: API key for newsapi.org, if the news feed feature that uses this key is active. (Note: The current news feed is static, but the variable is available for future dynamic content).
*   `FLASK_APP="app.py"`: Standard Flask variable, tells Flask where to find the application instance.
*   `FLASK_ENV="production"`: Crucial for security and performance. This disables debug mode and other development-only features.
*   `PYTHONUNBUFFERED=1`: Often recommended for Gunicorn deployments to ensure logs are output immediately.

**Example of Setting Environment Variables:**
Most PaaS providers have a section in their application settings UI where you can add these key-value pairs. Alternatively, using a CLI tool provided by the platform:
```bash
# Example for Heroku CLI
heroku config:set DB_HOST=your_db_host.compute.amazonaws.com
heroku config:set DB_USER=your_db_user
# ... and so on for all variables.

# Example for Render
# Variables can be set in the "Environment" section of your service settings.
```

### 5. General Deployment Steps (Example for Heroku/Render-like platforms)

1.  **Sign Up:** Create an account on your chosen PaaS platform (e.g., Heroku, Render).
2.  **Create Application:** Create a new application/service on the platform.
3.  **Connect Git Repository:** Link your Git repository (e.g., GitHub, GitLab) to the platform for automated or manual deployments.
4.  **Database Setup:**
    *   Provision a PostgreSQL database add-on via the platform's dashboard.
    *   Or, if using an external database, ensure it's accessible from the platform and obtain its connection details.
5.  **Configure Environment Variables:**
    *   Set the `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` environment variables using the connection details from your database. (Note: Some platforms might provide a single `DATABASE_URL` which you might need to parse or adapt your `get_db_connection` function for, but Fitgent 2.0 currently uses individual `DB_*` variables).
    *   Set `FLASK_APP`, `FLASK_ENV`, `NEWS_API_KEY` (if used), and any other necessary environment variables.
6.  **Trigger Deployment:**
    *   Push your code to the main branch of your connected Git repository. Most PaaS platforms will automatically detect the push and start building and deploying your application.
    *   Alternatively, you might trigger a manual deployment through the platform's dashboard.
7.  **Check Logs:** Monitor the deployment logs provided by the platform for any build errors, application startup issues, or runtime errors. Address any issues as needed.

Once deployed, your Fitgent 2.0 application should be accessible via the URL provided by the hosting platform.
