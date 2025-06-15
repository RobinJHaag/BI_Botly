import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker


def db_fülle():
    data_generator_connector = sqlite3.connect("botly.db")
    data_generator_cursor = data_generator_connector.cursor()
    faker = Faker("de_CH")

    data_generator_cursor.executescript("""
    DELETE FROM support_tickets;
    DELETE FROM refund_requests;
    DELETE FROM replacements_requests;
    """)

    produkte = [
        ("Logitech G Pro X", "Mouse"), ("Razer DeathAdder V2", "Mouse"), ("SteelSeries Rival 650", "Mouse"),
        ("Corsair Dark Core", "Mouse"), ("Glorious Model O", "Mouse"), ("Logitech MX Keys", "Keyboard"),
        ("Corsair K70 RGB", "Keyboard"), ("SteelSeries Apex Pro", "Keyboard"), ("Razer Huntsman Mini", "Keyboard"),
        ("Keychron K8", "Keyboard"), ("Elgato Stream Deck XL", "Accessory"), ("HyperX QuadCast", "Accessory"),
        ("Blue Yeti X", "Accessory"), ("Logitech Brio 4K", "Accessory"), ("Rode NT-USB", "Accessory"),
        ("Samsung Odyssey G7", "Monitor"), ("LG UltraGear 27GL850", "Monitor"), ("Dell Alienware AW3423", "Monitor"),
        ("ASUS TUF VG27AQ", "Monitor"), ("BenQ Zowie XL2546K", "Monitor")
    ]
    for eintrag in produkte:
        data_generator_cursor.execute("INSERT INTO products (product_name, category) VALUES (?,?)", eintrag)

    kanal_namen = ["Botly", "E-Mail", "Telefon", "Live-Chat"]
    for k in kanal_namen:
        data_generator_cursor.execute("INSERT INTO channels (channel_name) VALUES (?)", (k,))

    typ_liste = ["Defekt", "Verspätung", "Falscher Artikel", "Allgemeine Frage", "Rückgabeanfrage"]
    for t in typ_liste:
        data_generator_cursor.execute("INSERT INTO issue_types (issue_label) VALUES (?)", (t,))

    mitarbeiter_loehne = [28.5, 30.0, 26.0, 29.0, 31.5]
    for i in range(1, 6):
        name = faker.first_name()
        lohn = mitarbeiter_loehne[i - 1]
        data_generator_cursor.execute("INSERT INTO support_employees (name, hourly_wage) VALUES (?,?)", (name, lohn))

    for i in range(1, 301):
        data_generator_cursor.execute("INSERT INTO customers (name, region) VALUES (?,?)", (faker.name(), faker.city()))

    tage = []
    heute = datetime.today()
    for tagnummer in range(1, 61):
        d = heute - timedelta(days=61 - tagnummer)
        data_generator_cursor.execute(
            "INSERT OR IGNORE INTO dates (date_id, date_value, year, month, day) VALUES (?,?,?,?,?)",
            (tagnummer, d.strftime("%Y-%m-%d"), d.year, d.month, d.day)
        )
        tage.append(tagnummer)

    alle_tickets = []
    for nummer in range(1, 60):
        anzahl = int(10 + nummer * 0.8 + random.uniform(-3, 3))
        for schleife in range(anzahl):
            kund = random.randint(1, 300)
            mitarb = random.randint(1, 5)
            prod = random.randint(1, 20)
            chan = random.randint(1, 4)
            issue = random.randint(1, 5)
            dauer = random.randint(3, 45)
            data_generator_cursor.execute(
                "INSERT INTO support_tickets (customer_id, employee_id, product_id, channel_id, issue_type_id, date_id, handling_time_minutes) VALUES (?,?,?,?,?,?,?)",
                (kund, mitarb, prod, chan, issue, nummer, dauer)
            )
            alle_tickets.append((kund, mitarb, prod, chan, issue, nummer, dauer))

    for idx in range(len(alle_tickets) // 4):
        t = alle_tickets[random.randint(0, len(alle_tickets) - 1)]
        dauer_refund = random.randint(2, 25)
        betrag = round(random.uniform(15, 250), 2)
        ok = random.choice([0, 1])
        data_generator_cursor.execute(
            "INSERT INTO refund_requests (ticket_id, customer_id, employee_id, product_id, channel_id, date_id, handling_time_minutes, amount, approved) VALUES (?,?,?,?,?,?,?,?,?)",
            (idx + 1, t[0], t[1], t[2], t[3], t[5], dauer_refund, betrag, ok)
        )

    for idx in range(len(alle_tickets) // 5):
        t = alle_tickets[random.randint(0, len(alle_tickets) - 1)]
        dauer_replace = random.randint(2, 30)
        ok = random.choice([0, 1])
        data_generator_cursor.execute(
            "INSERT INTO replacements_requests (ticket_id, customer_id, employee_id, product_id, channel_id, date_id, handling_time_minutes, approved) VALUES (?,?,?,?,?,?,?,?)",
            (idx + 1, t[0], t[1], t[2], t[3], t[5], dauer_replace, ok)
        )

    data_generator_connector.commit()
    data_generator_connector.close()
    print("200,000 units are ready, with a million more well on the way -Lama Su.")
