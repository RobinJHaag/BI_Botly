import sqlite3
import os


def dew_it():
    if os.path.exists("botly.db"):
        os.remove("botly.db")  # not from a Jedi
    con = sqlite3.connect("botly.db")
    cur = con.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS refund_requests;
    DROP TABLE IF EXISTS support_tickets;
    DROP TABLE IF EXISTS products;
    DROP TABLE IF EXISTS channels;
    DROP TABLE IF EXISTS issue_types;
    DROP TABLE IF EXISTS dates;

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL
    );

    CREATE TABLE channels (
        channel_id INTEGER PRIMARY KEY,
        channel_name TEXT NOT NULL
    );

    CREATE TABLE issue_types (
        issue_type_id INTEGER PRIMARY KEY,
        issue_label TEXT NOT NULL
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
        product_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        issue_type_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
        FOREIGN KEY (issue_type_id) REFERENCES issue_types(issue_type_id),
        FOREIGN KEY (date_id) REFERENCES dates(date_id)
    );

    CREATE TABLE refund_requests (
        refund_id INTEGER PRIMARY KEY,
        ticket_id INTEGER,
        product_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        date_id INTEGER NOT NULL,
        amount NUMERIC NOT NULL,
        approved BOOLEAN NOT NULL,
        FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (channel_id) REFERENCES channels(channel_id),
        FOREIGN KEY (date_id) REFERENCES dates(date_id)
    );
    """)
    con.commit()
    con.close()
    print("The data side of the Force is strong with this one.")


if __name__ == "__main__":
    dew_it()
