from db import get_db_connection
from keys import create_license_key
from utils import clear_screen
from datetime import datetime
import getpass
import bcrypt
import requests  # oben in admin.py einfügen

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1378802304966463628/tFnXSJ-adrFLAAW3fNcSFmOx4M4IpuVe5NmNxx4Y5udXwCWI4bCf2b0kE1EoefnOskFk"

def show_ascii_banner():
    banner = """
             ___    __      _            
            /   |  / /___  (_)___  ____ _
           / /| | / / __ \/ / __ \/ __ `/
          / ___ |/ / /_/ / / / / / /_/ / 
         /_/  |_/_/ .___/_/_/ /_/\__,_/  
                 /_/      Admin Panel    
    """
    print(banner)

def admin_dashboard(user):
    while True:
        clear_screen()
        show_ascii_banner()
        print(f"Angemeldet als: {user['username']} (Admin)\n")
        print("1. Alle Nutzer anzeigen")
        print("2. Lizenzschlüssel generieren")
        print("3. Nutzer aktivieren")
        print("4. Benutzer erstellen")
        print("5. Benutzer löschen")
        print("6. Logout")

        choice = input("\nOption wählen: ").strip()
        if choice == "1":
            show_users()
        elif choice == "2":
            generate_key()
        elif choice == "3":
            activate_user()
        elif choice == "4":
            create_user()
        elif choice == "5":
            delete_user()
        elif choice == "6":
            break
        else:
            print("❌ Ungültige Option.")
            input("Weiter mit Enter...")

def show_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_active, is_admin FROM users")
    users = cursor.fetchall()
    print("\nID | Benutzername | Aktiv | Admin")
    print("-" * 40)
    for u in users:
        print(f"{u[0]} | {u[1]} | {'Ja' if u[2] else 'Nein'} | {'Ja' if u[3] else 'Nein'}")
    input("\nWeiter mit Enter...")
    cursor.close()
    conn.close()

import uuid
from datetime import datetime

def generate_key(user):  # user-Dict mit mindestens username erwartet
    expires_input = input("Gültig bis (YYYY-MM-DD): ").strip()
    try:
        expires_at = datetime.strptime(expires_input, "%Y-%m-%d").date()
    except ValueError:
        print("❌ Ungültiges Datum.")
        input("Weiter mit Enter...")
        return

    key = create_license_key(expires_at)
    created_at = datetime.utcnow()

    # Transaktions-ID generieren (UUID4, Kurzform)
    transaction_id = str(uuid.uuid4()).split('-')[0].upper()

    # Optional: Transaktions-ID & Key in DB speichern
    # save_transaction(transaction_id, user['username'], key, expires_at, created_at)

    # Paysafecard-Bon Text bauen
    receipt_lines = [
        "===================================",
        "          PAYSAFECARD BON           ",
        "===================================",
        f"Transaktions-ID: {transaction_id}",
        f"Datum:          {created_at.strftime('%d.%m.%Y %H:%M:%S UTC')}",
        f"Nutzer:         {user['username']}",
        "-----------------------------------",
        f"Code:           {key}",
        f"Betrag:         50 EUR",
        "-----------------------------------",
        "Vielen Dank für Ihren Einkauf!",
        "Bitte bewahren Sie diesen Bon auf.",
        "Dieser Beleg dient als Nachweis",
        "für Ihre Paysafecard-Transaktion.",
        "===================================",
    ]

    receipt_text = "```\n" + "\n".join(receipt_lines) + "\n```"  # Codeblock für Discord

    embed = {
        "title": "🧾 Neuer Lizenzschlüssel erstellt",
        "description": receipt_text,
        "color": 0x00FF00,
        "footer": {
            "text": "Admin Panel - Lizenzsystem"
        },
        "timestamp": created_at.isoformat() + "Z"
    }

    data = {
        "username": "LicenseBot",
        "embeds": [embed]
    }

    print(f"\n✅ Neuer Lizenzschlüssel: {key}")
    print(f"Transaktions-ID: {transaction_id}")

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code in (200, 204):
            print("📬 Webhook erfolgreich an Discord gesendet.")
        else:
            print(f"⚠️ Webhook-Fehler: {response.status_code}")
    except Exception as e:
        print(f"❌ Webhook fehlgeschlagen: {e}")

    input("Weiter mit Enter...")


# Beispiel Save-Function (müsstest du an DB anpassen)
def save_transaction(tx_id, username, key, expires_at, created_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (tx_id, username, license_key, expires_at, created_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (tx_id, username, key, expires_at, created_at))
    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Transaktion erfolgreich gespeichert.")




def activate_user():
    user_id = input("User-ID aktivieren: ").strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active=TRUE WHERE id=%s", (user_id,))
    conn.commit()
    print("✅ Benutzer wurde aktiviert.")
    input("Weiter mit Enter...")
    cursor.close()
    conn.close()

def create_user():
    username = input("🆕 Benutzername: ").strip()
    password = getpass.getpass("🔑 Passwort: ")
    password_confirm = getpass.getpass("🔁 Passwort bestätigen: ")

    if password != password_confirm:
        print("❌ Passwörter stimmen nicht überein.")
        input("Weiter mit Enter...")
        return

    is_active = input("Soll der Benutzer sofort aktiviert werden? (y/n): ").strip().lower() == 'y'
    is_admin = input("Soll der Benutzer Adminrechte erhalten? (y/n): ").strip().lower() == 'y'

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password_hash, is_active, is_admin) VALUES (%s, %s, %s, %s)",
        (username, password_hash.decode(), is_active, is_admin)
    )
    conn.commit()
    print("✅ Benutzer wurde erstellt.")
    input("Weiter mit Enter...")
    cursor.close()
    conn.close()

def delete_user():
    user_id = input("🗑️  Benutzer-ID zum Löschen: ").strip()
    confirm = input(f"Sicher, dass Benutzer-ID {user_id} gelöscht werden soll? (y/n): ").strip().lower()
    if confirm != 'y':
        print("🚫 Abgebrochen.")
        input("Weiter mit Enter...")
        return

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    print("✅ Benutzer wurde gelöscht.")
    input("Weiter mit Enter...")
    cursor.close()
    conn.close()
