from utils import clear_screen, get_ip, get_cpu, get_gpu
from db import get_db_connection
from datetime import datetime
import asyncio
import aiohttp
import os
from colorama import Fore, Style

def user_dashboard(user):
    clear_screen()
    print(f"Welcome, {user['username']}")

    while True:
        print("\n=== Benutzer-Menü ===")
        print("1. Profil anzeigen")
        print("2. Ping-Tool starten")  # Hier Option 2 mit neuem Tool
        # Weitere Optionen wie gehabt …
        print("8. Logout")

        choice = input("Wähle eine Option: ")
        if choice == "8":
            print("Logout erfolgreich.")
            break
        elif choice == "1":
            user_dashboard(user)
        elif choice == "2":
            option_2_ping_tool()
        else:
            print("Option noch nicht implementiert.")

        input("Drücke Enter, um fortzufahren...")
        

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

async def increment_view_count(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                print("PINGED THIS SHI!")
            else:
                print("Failed ping.")
    except aiohttp.ClientError as e:
        print("An error occurred:", e)

async def run_ping_tool(url):
    # Clear screen
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    show_ascii_banner()
    print("==== BEST NETTING TOOL YOUR EYES HAVE EVER SEEN ====")
    print("GIVE US SECONDS, SAVE YOURSELF MONTHS\n")

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(increment_view_count(session, url)) for _ in range(100)]
        await asyncio.gather(*tasks)

def option_2_ping_tool():
    url = input("Enter the target IP/URL: ")
    asyncio.run(run_ping_tool(url))
    input("\nDrücke Enter, um zurück zum Menü zu gelangen...")


