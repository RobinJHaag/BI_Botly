import sqlite3 as datensteckdose
import random as würfler
from datetime import datetime as uhrwerk, timedelta as tageschieber
from faker import Faker as namenszauberer


def db_fülle():
    print("Starte Datenabruf aus externen Quellen...")
    verbindung = datensteckdose.connect("botly.db")
    macher = verbindung.cursor()
    faker = namenszauberer("de_CH")

    print("Lösche alte Datenbestände...")
    macher.executescript("""
    DELETE FROM support_tickets;
    DELETE FROM refund_requests;
    DELETE FROM replacements_requests;
    """)
    print("Altdaten entfernt.")

    print("Lade Produkt- und Stammdaten...")
    produkte_liste = [
        ("Logitech G Pro X", "Mouse", 79.90), ("Razer DeathAdder V2", "Mouse", 59.90),
        ("SteelSeries Rival 650", "Mouse", 89.90), ("Corsair Dark Core", "Mouse", 84.90),
        ("Glorious Model O", "Mouse", 69.90), ("Logitech MX Keys", "Keyboard", 99.00),
        ("Corsair K70 RGB", "Keyboard", 129.90), ("SteelSeries Apex", "Keyboard", 109.90),
        ("Razer Huntsman", "Keyboard", 139.90), ("Keychron K8", "Keyboard", 89.90),
        ("Elgato Stream Deck", "Accessory", 149.00), ("HyperX QuadCast", "Accessory", 119.00),
        ("Blue Yeti X", "Accessory", 139.00), ("Logitech Brio 4K", "Accessory", 199.00),
        ("Rode NT-USB", "Accessory", 149.00), ("Samsung Odyssey G7", "Monitor", 629.00),
        ("LG UltraGear 27GL850", "Monitor", 499.00), ("Dell Alienware AW3423", "Monitor", 1149.00),
        ("ASUS TUF VG27AQ", "Monitor", 399.00), ("BenQ Zowie XL2546K", "Monitor", 499.00)
    ]
    macher.executemany("INSERT OR IGNORE INTO products (product_name, category, price) VALUES (?,?,?)", produkte_liste)

    kanal_namen = ["Botly", "E-Mail", "Telefon"]
    macher.executemany("INSERT OR IGNORE INTO channels (channel_name) VALUES (?)", [(k,) for k in kanal_namen])

    motz_kategorie = ["Defekt", "Verspätung", "Falscher Artikel", "Allgemeine Frage", "Rückgabeanfrage"]
    macher.executemany("INSERT OR IGNORE INTO issue_types (issue_label) VALUES (?)", [(m,) for m in motz_kategorie])

    lohn_liste = [28.5, 30.0, 26.0, 29.0, 31.5]
    for gehalt in lohn_liste:
        macher.execute("INSERT OR IGNORE INTO support_employees (name, hourly_wage) VALUES (?,?)",
                       (faker.first_name(), gehalt))

    kunden_daten = [(faker.name(), faker.city()) for _ in range(3000)]
    macher.executemany("INSERT OR IGNORE INTO customers (name, region) VALUES (?,?)", kunden_daten)
    print("Stammdaten geladen.")

    print("Erstelle Datumsdimension...")
    heute = uhrwerk.today()
    for nummer in range(1, 61):
        tag = heute - tageschieber(days=61 - nummer)
        macher.execute("INSERT OR IGNORE INTO dates (date_id, date_value, year, month, day) VALUES (?,?,?,?,?)",
                       (nummer, tag.strftime("%Y-%m-%d"), tag.year, tag.month, tag.day))
    print("Datumsdimension bereit.")

    print("Generiere Support-Tickets und lade in DWH...")
    alle_tickets = []
    for tag_id in range(1, 61):
        menge = int((10 + tag_id * 0.8) * 10)
        for _ in range(menge):
            kunde = würfler.randint(1, 3000)
            mitarbeiter = würfler.randint(1, 5)
            produkt = würfler.randint(1, 20)
            kanal = würfler.randint(1, 3)
            typ = würfler.randint(1, 5)
            dauer = würfler.randint(3, 45)
            macher.execute(
                "INSERT INTO support_tickets (customer_id, employee_id, product_id, channel_id, issue_type_id, date_id, handling_time_minutes) VALUES (?,?,?,?,?,?,?)",
                (kunde, mitarbeiter, produkt, kanal, typ, tag_id, dauer)
            )
            alle_tickets.append((kunde, mitarbeiter, produkt, kanal, typ, tag_id, dauer))

    for _ in range(1000):
        kunde = würfler.randint(1, 3000)
        mitarbeiter = würfler.randint(1, 5)
        kanal = würfler.randint(1, 3)
        typ = würfler.randint(1, 5)
        dauer = würfler.randint(12, 44)
        tag_id = würfler.randint(1, 60)
        macher.execute(
            "INSERT INTO support_tickets (customer_id, employee_id, product_id, channel_id, issue_type_id, date_id, handling_time_minutes) VALUES (?,?,?,?,?,?,?)",
            (kunde, mitarbeiter, 5, kanal, typ, tag_id, dauer)
        )
    print("Support-Tickets geladen.")

    print("Erstelle Rückerstattungen und Ersatzanfragen...")
    for index, eintrag in enumerate(alle_tickets[:len(alle_tickets) // 4], 1):
        dauer = würfler.randint(2, 25)
        betrag = round(würfler.uniform(15, 250), 2)
        ok = würfler.choice([0, 1])
        macher.execute(
            "INSERT INTO refund_requests (ticket_id, customer_id, employee_id, product_id, channel_id, date_id, handling_time_minutes, amount, approved) VALUES (?,?,?,?,?,?,?,?,?)",
            (index, eintrag[0], eintrag[1], eintrag[2], eintrag[3], eintrag[5], dauer, betrag, ok)
        )

    for index, eintrag in enumerate(alle_tickets[:len(alle_tickets) // 5], 1):
        dauer = würfler.randint(2, 30)
        ok = würfler.choice([0, 1])
        macher.execute(
            "INSERT INTO replacements_requests (ticket_id, customer_id, employee_id, product_id, channel_id, date_id, handling_time_minutes, approved) VALUES (?,?,?,?,?,?,?,?)",
            (index, eintrag[0], eintrag[1], eintrag[2], eintrag[3], eintrag[5], dauer, ok)
        )
    print("Rückerstattungen und Ersatzanfragen bereit.")

    print("Lade Verkaufszahlen in Data Warehouse...")
    for tag_id in range(1, 61):
        for produkt_id in range(1, 21):
            menge = 120 + würfler.randint(0, 30)
            if produkt_id == 5:
                menge += würfler.randint(30, 80)
            macher.execute("INSERT INTO sales (product_id, date_id, quantity) VALUES (?,?,?)",
                           (produkt_id, tag_id, menge))
    print("Verkaufsdaten geladen.")

    verbindung.commit()
    verbindung.close()
    print("ETL-Prozess abgeschlossen. Data Warehouse ist bereit.")
    print("200,000 units are ready, with a million more well on the way – Lama Su.")
