import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

def lol_fill_stuff():
    mydb = sqlite3.connect("botly.db")
    cursorthing = mydb.cursor()
    faker = Faker()

    # products
    cursorthing.execute("INSERT INTO products (product_name, category) VALUES (?, ?)", ("Logitech G Pro", "Mouse"))
    cursorthing.execute("INSERT INTO products (product_name, category) VALUES (?, ?)", ("Razer DeathAdder", "Mouse"))
    cursorthing.execute("INSERT INTO products (product_name, category) VALUES (?, ?)", ("SteelSeries Apex", "Keyboard"))
    cursorthing.execute("INSERT INTO products (product_name, category) VALUES (?, ?)", ("Corsair K70", "Keyboard"))
    cursorthing.execute("INSERT INTO products (product_name, category) VALUES (?, ?)", ("Elgato Stream Deck", "Accessory"))

    # channels
    cursorthing.execute("INSERT INTO channels (channel_name) VALUES (?)", ("Botly",))
    cursorthing.execute("INSERT INTO channels (channel_name) VALUES (?)", ("Email",))
    cursorthing.execute("INSERT INTO channels (channel_name) VALUES (?)", ("Phone",))

    # issue types
    cursorthing.execute("INSERT INTO issue_types (issue_label) VALUES (?)", ("Product Issue",))
    cursorthing.execute("INSERT INTO issue_types (issue_label) VALUES (?)", ("Shipping Delay",))
    cursorthing.execute("INSERT INTO issue_types (issue_label) VALUES (?)", ("Wrong Item",))
    cursorthing.execute("INSERT INTO issue_types (issue_label) VALUES (?)", ("General Complaint",))

    # dates
    z = 1
    while z <= 60:
        d = datetime.today() - timedelta(days=z)
        date_str = d.strftime("%Y-%m-%d")
        y = d.year
        m = d.month
        dd = d.day
        cursorthing.execute("INSERT INTO dates (date_id, date_value, year, month, day) VALUES (?, ?, ?, ?, ?)",
                            (z, date_str, y, m, dd))
        z += 1

    # tickets
    tickets = []
    for x in range(500):
        p = random.randint(1, 5)
        ch = random.randint(1, 3)
        t = random.randint(1, 4)
        d = random.randint(1, 60)
        cursorthing.execute("INSERT INTO support_tickets (product_id, channel_id, issue_type_id, date_id) VALUES (?, ?, ?, ?)",
                            (p, ch, t, d))
        tickets.append((p, ch, t, d))

    # refunds
    for y in range(120):
        tid = random.randint(1, 499)
        row = tickets[tid] if tid < len(tickets) else (1, 1, 1, 1)
        pid = row[0]
        cid = row[1]
        did = row[3]
        amount = round(random.uniform(20, 150), 2)
        approved = random.choice([0, 1])
        cursorthing.execute("INSERT INTO refund_requests (ticket_id, product_id, channel_id, date_id, amount, approved) VALUES (?, ?, ?, ?, ?, ?)",
                            (tid+1, pid, cid, did, amount, approved))

    mydb.commit()
    mydb.close()
    print("200,000 units are ready, with a million more well on the way")

