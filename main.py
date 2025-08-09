from utils import clear_screen
from auth import login, register
from user import user_dashboard
from admin import admin_dashboard
from db import initialize_tables
from colorama import init, Fore, Style
import sys
import time

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

def loading_bar(task="Lade", duration=4, steps=20):
    print(f"{task}: ", end="")
    for _ in range(steps):
        time.sleep(duration / steps)
        sys.stdout.write("█")
        sys.stdout.flush()
    print(" ✅\n")
    time.sleep(1)

def main():
    clear_screen()
    show_ascii_banner()
    loading_bar("Initialisiere Datenbank")
    initialize_tables()

    while True:
        clear_screen()
        show_ascii_banner()
        print("Willkommen\n")
        print("Bitte wählen Sie eine Option:\n")
        print(" [1] 🔑  Login")
        print(" [2] 📝  Registrieren")
        print(" [3] ❌  Beenden")
        print("\n================================================\n")

        choice = input("Option wählen: ").strip()

        if choice == "1":
            user = login()
            if user:
                loading_bar("Benutzerdaten werden geladen")
                if user['is_admin']:
                    admin_dashboard(user)
                else:
                    user_dashboard(user)

        elif choice == "2":
            register()

        elif choice == "3":
            print("\n👋  Auf Wiedersehen!")
            break

        else:
            print("\n⚠️  Ungültige Eingabe. Bitte versuchen Sie es erneut.")
            input("\nDrücken Sie Enter, um fortzufahren...")

if __name__ == "__main__":
    main()
