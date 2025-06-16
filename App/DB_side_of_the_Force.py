import sqlite3 as datebank
import os as operatingsystem


def dew_it():
    gits_db_no = operatingsystem.path.exists("botly.db")
    if gits_db_no:
        operatingsystem.remove("botly.db")

    datebank_connector = datebank.connect("botly.db")
    sql_magicstick = datebank_connector.cursor()

    sql_magicstick.executescript("""
    DROP TABLE IF EXISTS refund_requests;
    DROP TABLE IF EXISTS support_tickets;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS support_employees;
    DROP TABLE IF EXISTS channels;
    DROP TABLE IF EXISTS issue_types;
    DROP TABLE IF EXISTS dates;
    DROP TABLE IF EXISTS replacements_requests;

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price Integer NOT NULL 
    );

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        region TEXT NOT NULL
    );

    CREATE TABLE support_employees (
        employee_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        hourly_wage NUMERIC NOT NULL
    );

    CREATE TABLE channels (
        channel_id INTEGER PRIMARY KEY,
        channel_name TEXT NOT NULL
    );

    CREATE TABLE issue_types (
        issue_type_id INTEGER PRIMARY KEY,
        issue_label TEXT NOT NULL
    );

    CREATE TABLE sales (
        sale_id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (date_id) REFERENCES dates(date_id)
    );

    CREATE TABLE dates (
        date_id INTEGER PRIMARY KEY,
        date_value DATE NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        day INTEGER NOT NULL
    );

    CREATE TABLE support_tickets (
        ticket_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        issue_type_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        handling_time_minutes INTEGER NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (employee_id) REFERENCES support_employees(employee_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
        FOREIGN KEY (issue_type_id) REFERENCES issue_types(issue_type_id),
        FOREIGN KEY (date_id) REFERENCES dates(date_id)
    );

    CREATE TABLE refund_requests (
        refund_id INTEGER PRIMARY KEY,
        ticket_id INTEGER,
        customer_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        handling_time_minutes INTEGER NOT NULL,
        amount NUMERIC NOT NULL,
        approved BOOLEAN NOT NULL,
        FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (employee_id) REFERENCES support_employees(employee_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
        FOREIGN KEY (date_id) REFERENCES dates(date_id)
    );

    CREATE TABLE replacements_requests (
        replacement_id INTEGER PRIMARY KEY,
        ticket_id INTEGER,
        customer_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        handling_time_minutes INTEGER NOT NULL,
        approved BOOLEAN NOT NULL,
        FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id),
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (employee_id) REFERENCES support_employees(employee_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
        FOREIGN KEY (date_id) REFERENCES dates(date_id)
    );
    """)

    datebank_connector.commit()
    datebank_connector.close()
    print("The data side of the Force is strong with this one.")
