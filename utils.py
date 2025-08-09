import os
import socket
import platform

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_ip():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

def get_cpu():
    return platform.processor()

def get_gpu():
    # GPU-Abfrage plattformabhängig, einfach Platzhalter
    return "Generic GPU"
