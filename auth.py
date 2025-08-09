import getpass
import bcrypt
import sys
import time
from datetime import datetime
from db import get_db_connection
from utils import clear_screen
from keys import redeem_license_key
from colorama import init, Fore, Style

# Colorama initialisieren
init(autoreset=True)

def show_ascii_banner():
    banner = Fore.MAGENTA + """
             ___    __      _            
            /   |  / /___  (_)___  ____ _
           / /| | / / __ \/ / __ \/ __ `/
          / ___ |/ / /_/ / / / / / /_/ / 
         /_/  |_/_/ .___/_/_/ /_/\__,_/  
                 /_/                     
    """ + Style.RESET_ALL
    print(banner)

# Ladebalken zur besseren UX
def loading_bar(task="Verarbeite", duration=1.5, steps=20):
    print(Fore.MAGENTA + f"{task}: ", end="")
    for _ in range(steps):
        time.sleep(duration / steps)
        sys.stdout.write(Fore.GREEN + "█")
        sys.stdout.flush()
    print(Style.RESET_ALL + " ✅\n")

def register():
    clear_screen()
    show_ascii_banner()
    print(Fore.CYAN + "\n=== Registrierung ===\n" + Style.RESET_ALL)

    conn = get_db_connection()
    if not conn:
        print(Fore.RED + "❌ Verbindung zur Datenbank fehlgeschlagen." + Style.RESET_ALL)
        return

    cursor = conn.cursor()

    # Benutzername abfragen & prüfen
    while True:
        username = input(Fore.YELLOW + "👤 Benutzername: " + Style.RESET_ALL).strip()
        cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
        if cursor.fetchone():
            print(Fore.RED + "⚠️  Benutzername existiert bereits. Bitte wähle einen anderen." + Style.RESET_ALL)
        else:
            break

    # Passwort abfragen & bestätigen
    while True:
        password = getpass.getpass(Fore.YELLOW + "🔒 Passwort: " + Style.RESET_ALL)
        password_confirm = getpass.getpass(Fore.YELLOW + "🔁 Passwort bestätigen: " + Style.RESET_ALL)
        if password != password_confirm:
            print(Fore.RED + "⚠️  Passwörter stimmen nicht überein. Bitte erneut eingeben." + Style.RESET_ALL)
        else:
            break

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, password_hash.decode())
    )
    conn.commit()
    loading_bar("Speichere Account")

    print(Fore.GREEN + "\n✅ Account erstellt, aber noch nicht aktiviert." + Style.RESET_ALL)
    print(Fore.BLUE + "🔑 Bitte aktiviere deinen Account mit einem Lizenzschlüssel.\n" + Style.RESET_ALL)

    cursor.close()
    conn.close()

def login():
    clear_screen()
    print(Fore.CYAN + "\n=== Login ===\n" + Style.RESET_ALL)

    conn = get_db_connection()
    if not conn:
        print(Fore.RED + "❌ Verbindung zur Datenbank fehlgeschlagen." + Style.RESET_ALL)
        return None

    cursor = conn.cursor()
    username = input(Fore.YELLOW + "👤 Benutzername: " + Style.RESET_ALL).strip()
    password = getpass.getpass(Fore.YELLOW + "🔒 Passwort: " + Style.RESET_ALL)

    cursor.execute(
        "SELECT id, password_hash, is_active, is_admin FROM users WHERE username=%s", (username,)
    )
    user = cursor.fetchone()

    if not user:
        print(Fore.RED + "❌ Benutzername oder Passwort ist falsch." + Style.RESET_ALL)
        cursor.close()
        conn.close()
        return None

    user_id, pw_hash, is_active, is_admin = user

    if not bcrypt.checkpw(password.encode(), pw_hash.encode()):
        print(Fore.RED + "❌ Benutzername oder Passwort ist falsch." + Style.RESET_ALL)
        cursor.close()
        conn.close()
        return None

    # Account nicht aktiviert
    if not is_active:
        print(Fore.RED + "\n🔒 Dein Account ist noch nicht aktiviert." + Style.RESET_ALL)
        print("🗝️  Bitte gib deinen Lizenzschlüssel ein, um ihn freizuschalten.\n")
        activated = False
        while not activated:
            key = input(Fore.YELLOW + "🔑 Lizenzschlüssel: " + Style.RESET_ALL).strip()
            success, days_left = redeem_license_key(user_id, key)
            if success:
                loading_bar("Aktiviere Account")
                print(Fore.GREEN + f"\n✅ Account erfolgreich aktiviert!" + Style.RESET_ALL)
                print(Fore.CYAN + f"📅 Lizenz gültig für {days_left} weitere Tage.\n" + Style.RESET_ALL)
                activated = True
            else:
                print(Fore.RED + "❌ Ungültiger oder bereits genutzter Schlüssel." + Style.RESET_ALL)

        print("Bitte logge dich erneut ein.\n")
        cursor.close()
        conn.close()
        return None

    # Erfolgreicher Login
    cursor.close()
    conn.close()
    return {
        "id": user_id,
        "username": username,
        "is_admin": is_admin
    }
