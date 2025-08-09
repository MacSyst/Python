import random
import string
from db import get_db_connection
from datetime import datetime

def generate_license_key(length=16):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def create_license_key(expires_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    key = generate_license_key()
    cursor.execute("INSERT INTO license_keys (key_value, expires_at) VALUES (%s, %s)", (key, expires_at))
    conn.commit()
    cursor.close()
    conn.close()
    return key

def redeem_license_key(user_id, key_value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, expires_at, used FROM license_keys WHERE key_value=%s", (key_value,))
    result = cursor.fetchone()
    if not result:
        cursor.close()
        conn.close()
        return False, 0
    key_id, expires_at, used = result
    if used:
        cursor.close()
        conn.close()
        return False, 0
    if expires_at < datetime.now().date():
        cursor.close()
        conn.close()
        return False, 0

    cursor.execute("UPDATE license_keys SET used=TRUE WHERE id=%s", (key_id,))
    cursor.execute("UPDATE users SET is_active=TRUE WHERE id=%s", (user_id,))
    cursor.execute("INSERT INTO licenses (user_id, expires_at) VALUES (%s, %s)", (user_id, expires_at))
    conn.commit()
    cursor.close()
    conn.close()

    days_left = (expires_at - datetime.now().date()).days
    return True, days_left

