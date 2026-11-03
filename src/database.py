"""
MySQL Database Manager Module
Handles connection, table creation, record insertion, and queries for
products, sales, and forecast results with graceful fallbacks.
"""

import os
import time
import socket
import mysql.connector
from mysql.connector import Error
import pandas as pd

# In-memory status cache to avoid TCP connection timeouts on every template render
_STATUS_CACHE = None
_STATUS_CACHE_TIME = 0


def is_port_reachable(host: str, port: int, timeout: float = 0.3) -> bool:
    """Fast pre-check to test if the MySQL port is open before attempting handshake."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def load_env_file(filepath: str = ".env"):
    """Lightweight .env parser that loads key=value pairs into os.environ."""
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass


# Load local .env if present
load_env_file()


def get_db_config():
    """Returns database configuration from environment variables."""
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'sales_forecasting_db'),
        'port': int(os.environ.get('DB_PORT', 3306)),
        'connection_timeout': 3
    }


def get_connection(use_database=True):
    """
    Attempts to establish a MySQL connection.
    Returns (connection, error_message).
    """
    config = get_db_config()
    if not is_port_reachable(config['host'], config['port']):
        return None, f"Port {config['port']} on {config['host']} is not reachable. (MySQL service offline)"

    if not use_database:
        config_copy = config.copy()
        config_copy.pop('database', None)
        config = config_copy

    try:
        conn = mysql.connector.connect(**config)
        return conn, None
    except Error as e:
        return None, str(e)


def check_db_status(force: bool = False):
    """
    Checks MySQL connectivity and database table presence with caching.
    Returns status dictionary.
    """
    global _STATUS_CACHE, _STATUS_CACHE_TIME
    now = time.time()
    if not force and _STATUS_CACHE is not None and (now - _STATUS_CACHE_TIME < 15):
        return _STATUS_CACHE

    config = get_db_config()
    status = {
        'connected': False,
        'database_exists': False,
        'tables_exist': False,
        'record_count': 0,
        'host': config['host'],
        'port': config['port'],
        'user': config['user'],
        'database': config['database'],
        'message': ''
    }

    # Step 0: Fast socket check
    if not is_port_reachable(config['host'], config['port']):
        status['message'] = f"MySQL server is offline or unreachable at {config['host']}:{config['port']}. System is running in CSV Mode."
        _STATUS_CACHE = status
        _STATUS_CACHE_TIME = now
        return status

    # Step 1: Check server connection without database
    conn, err = get_connection(use_database=False)
    if not conn:
        status['message'] = f"Cannot authenticate with MySQL server at {config['host']}:{config['port']}. Error: {err}"
        _STATUS_CACHE = status
        _STATUS_CACHE_TIME = now
        return status

    status['connected'] = True

    try:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (config['database'],))
        db_found = cursor.fetchone()
        if not db_found:
            status['message'] = f"MySQL server connected, but database '{config['database']}' does not exist yet. Click 'Initialize MySQL DB' to create it."
            cursor.close()
            conn.close()
            _STATUS_CACHE = status
            _STATUS_CACHE_TIME = now
            return status

        status['database_exists'] = True
        cursor.close()
        conn.close()

        # Step 2: Check tables in database
        db_conn, db_err = get_connection(use_database=True)
        if not db_conn:
            status['message'] = f"Could not open database '{config['database']}': {db_err}"
            _STATUS_CACHE = status
            _STATUS_CACHE_TIME = now
            return status

        cursor = db_conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0].lower() for t in cursor.fetchall()]
        has_tables = all(tbl in tables for tbl in ['products', 'sales', 'forecasts'])
        status['tables_exist'] = has_tables

        if has_tables:
            cursor.execute("SELECT COUNT(*) FROM sales")
            count = cursor.fetchone()[0]
            status['record_count'] = count
            status['message'] = f"MySQL connected and ready. Database has {count} sales records."
        else:
            status['message'] = f"Database '{config['database']}' exists, but missing required tables. Click 'Initialize MySQL DB'."

        cursor.close()
        db_conn.close()
    except Error as e:
        status['message'] = f"MySQL query error: {str(e)}"

    _STATUS_CACHE = status
    _STATUS_CACHE_TIME = now
    return status


def init_db():
    """
    Creates the database and executes schema to create products, sales, and forecasts tables.
    Returns (success: bool, message: str).
    """
    config = get_db_config()
    conn, err = get_connection(use_database=False)
    if not conn:
        return False, f"Failed to connect to MySQL server: {err}"

    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config['database']}` DEFAULT CHARACTER SET utf8mb4;")
        cursor.close()
        conn.close()

        # Now connect to newly ensured database
        db_conn, db_err = get_connection(use_database=True)
        if not db_conn:
            return False, f"Database created, but failed to connect: {db_err}"

        cursor = db_conn.cursor()

        # Create products table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            category VARCHAR(100) DEFAULT 'General'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Create sales table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT NOT NULL,
            sale_date DATE NOT NULL,
            quantity INT NOT NULL,
            unit_price DECIMAL(10,2) NOT NULL,
            region VARCHAR(100) DEFAULT 'Default',
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        # Create forecasts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            forecast_id INT AUTO_INCREMENT PRIMARY KEY,
            period VARCHAR(50) NOT NULL,
            method VARCHAR(50) NOT NULL,
            predicted_value DECIMAL(10,2) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)

        db_conn.commit()
        cursor.close()
        db_conn.close()
        return True, f"Database '{config['database']}' and tables initialized successfully."
    except Error as e:
        return False, f"Error initializing database: {str(e)}"


def save_sales_to_db(df: pd.DataFrame):
    """
    Inserts cleaned sales dataframe into MySQL database (populating products and sales tables).
    Returns (success: bool, count: int, message: str).
    """
    db_conn, err = get_connection(use_database=True)
    if not db_conn:
        return False, 0, f"Cannot connect to MySQL: {err}"

    try:
        cursor = db_conn.cursor()

        # Upsert Products
        products = df[['product_id', 'product_name', 'category']].drop_duplicates(subset=['product_id'])
        prod_query = """
        INSERT INTO products (product_id, product_name, category)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE product_name=VALUES(product_name), category=VALUES(category);
        """
        prod_data = [(int(row['product_id']), str(row['product_name']), str(row['category'])) 
                     for _, row in products.iterrows()]
        cursor.executemany(prod_query, prod_data)

        # Clear existing sales or append
        # To make it clean and avoid duplicates during sync, we can optionally clear sales
        cursor.execute("DELETE FROM sales")

        # Insert Sales
        sales_query = """
        INSERT INTO sales (product_id, sale_date, quantity, unit_price, region)
        VALUES (%s, %s, %s, %s, %s)
        """
        sales_data = [
            (int(row['product_id']), str(row['sale_date']), int(row['quantity']), float(row['unit_price']), str(row.get('region', 'Default')))
            for _, row in df.iterrows()
        ]
        cursor.executemany(sales_query, sales_data)

        db_conn.commit()
        count = len(sales_data)
        cursor.close()
        db_conn.close()
        return True, count, f"Successfully saved {count} sales records into MySQL."
    except Error as e:
        return False, 0, f"Failed to save records to MySQL: {str(e)}"


def load_sales_from_db():
    """
    Loads sales data from MySQL joined with products into a pandas DataFrame.
    Returns (df, error_message).
    """
    db_conn, err = get_connection(use_database=True)
    if not db_conn:
        return None, f"Database connection error: {err}"

    try:
        query = """
        SELECT s.sale_id, s.product_id, p.product_name, p.category, s.sale_date, 
               s.quantity, s.unit_price, s.region
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        ORDER BY s.sale_date ASC, s.sale_id ASC
        """
        df = pd.read_sql(query, db_conn)
        db_conn.close()
        
        if df.empty:
            return None, "MySQL sales table is currently empty."
            
        df['sale_date'] = pd.to_datetime(df['sale_date']).dt.strftime('%Y-%m-%d')
        df['quantity'] = df['quantity'].astype(int)
        df['unit_price'] = df['unit_price'].astype(float)
        df['revenue'] = (df['quantity'] * df['unit_price']).round(2)
        return df, None
    except Exception as e:
        return None, f"Failed to load data from MySQL: {str(e)}"


def save_forecast_to_db(period: str, method: str, predicted_value: float):
    """Saves a single forecast result entry into the MySQL forecasts table."""
    db_conn, _ = get_connection(use_database=True)
    if not db_conn:
        return False
    try:
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO forecasts (period, method, predicted_value) VALUES (%s, %s, %s)",
            (str(period), str(method), float(predicted_value))
        )
        db_conn.commit()
        cursor.close()
        db_conn.close()
        return True
    except Exception:
        return False


def get_saved_forecasts(limit: int = 20):
    """Retrieves recent saved forecasts from MySQL."""
    db_conn, _ = get_connection(use_database=True)
    if not db_conn:
        return []
    try:
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT forecast_id, period, method, predicted_value, created_at FROM forecasts ORDER BY forecast_id DESC LIMIT %s",
            (limit,)
        )
        results = cursor.fetchall()
        cursor.close()
        db_conn.close()
        return results
    except Exception:
        return []
