"""
STRUCTURA AI — Authentication & Phone OTP Verification Manager
==============================================================
Provides industry-grade authentication for civil engineering personnel:
- User registration with Phone Number & Role (Chief Engineer, Inspector, DOT Director)
- Simulated Real-World Phone OTP Engine (generates 6-digit cryptographic OTPs with simulated SMS preview)
- Session token generation and validation
- Pre-seeded benchmark accounts for instant hackathon evaluation
"""

import sqlite3
import hashlib
import secrets
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shm_records.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    salt = "structura_ai_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()


def init_auth_tables():
    """Initializes users and OTP verification tables in SQLite."""
    conn = get_db()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        role TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        agency TEXT DEFAULT 'Department of Transportation',
        is_verified INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Phone OTP Codes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS otp_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        otp_code TEXT NOT NULL,
        action TEXT DEFAULT 'LOGIN',
        expires_at REAL NOT NULL,
        is_used INTEGER DEFAULT 0
    )
    """)

    # Active Session Tokens Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at REAL NOT NULL,
        expires_at REAL NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    conn.commit()

    # Seed default Indian infrastructure engineering accounts
    seed_users = [
        {
            "full_name": "Dr. Rajesh Iyer, FIE (CEng)",
            "email": "engineer@infraguard.ai",
            "phone": "+91-98201-88420",
            "role": "Chief Structural Engineer",
            "agency": "NHAI & MoRTH Structural Integrity Division",
            "password": hash_password("InfraGuard@2026"),
            "verified": 1
        },
        {
            "full_name": "Vikramaditya Deshmukh",
            "email": "inspector@infraguard.ai",
            "phone": "+91-98114-41020",
            "role": "Senior NDT Field Inspector",
            "agency": "MSRDC & CSIR-SERC Rapid Response Taskforce",
            "password": hash_password("InfraGuard@2026"),
            "verified": 1
        },
        {
            "full_name": "Ananya Sharma, IAS",
            "email": "director@infraguard.ai",
            "phone": "+91-99100-90001",
            "role": "MoRTH / NHAI Infrastructure Director",
            "agency": "Ministry of Road Transport & Highways (Govt. of India)",
            "password": hash_password("InfraGuard@2026"),
            "verified": 1
        }
    ]

    for u in seed_users:
        cursor.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (u["email"], u["phone"]))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("""
            UPDATE users SET full_name = ?, email = ?, phone = ?, role = ?, agency = ?, password_hash = ?, is_verified = ?
            WHERE id = ?
            """, (u["full_name"], u["email"], u["phone"], u["role"], u["agency"], u["password"], u["verified"], existing[0]))
        else:
            cursor.execute("""
            INSERT INTO users (full_name, email, phone, role, agency, password_hash, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (u["full_name"], u["email"], u["phone"], u["role"], u["agency"], u["password"], u["verified"]))

    conn.commit()
    conn.close()


def generate_otp(phone: str, action: str = "LOGIN") -> Tuple[str, str]:
    """
    Generates a secure 6-digit OTP for the given phone number.
    Returns: (otp_code, sms_preview_message)
    """
    conn = get_db()
    cursor = conn.cursor()

    # Invalidate previous OTPs for this phone
    cursor.execute("UPDATE otp_codes SET is_used = 1 WHERE phone = ? AND is_used = 0", (phone,))

    # Generate 6-digit OTP
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = time.time() + 600.0  # 10 minutes expiry

    cursor.execute("""
    INSERT INTO otp_codes (phone, otp_code, action, expires_at, is_used)
    VALUES (?, ?, ?, ?, 0)
    """, (phone, otp_code, action, expires_at))

    conn.commit()
    conn.close()

    sms_preview = f"[INFRAGUARD SECURITY] Your authentication passcode is {otp_code}. Valid for 10 minutes. Do not share this code."
    return otp_code, sms_preview


def verify_otp(phone: str, entered_otp: str) -> bool:
    """Verifies that the entered 6-digit OTP is valid, unexpired, and unused."""
    conn = get_db()
    cursor = conn.cursor()
    now = time.time()

    cursor.execute("""
    SELECT id FROM otp_codes
    WHERE phone = ? AND otp_code = ? AND is_used = 0 AND expires_at > ?
    ORDER BY id DESC LIMIT 1
    """, (phone, entered_otp.strip(), now))

    row = cursor.fetchone()
    if row:
        otp_id = row["id"]
        cursor.execute("UPDATE otp_codes SET is_used = 1 WHERE id = ?", (otp_id,))
        # Mark user phone verified
        cursor.execute("UPDATE users SET is_verified = 1 WHERE phone = ?", (phone,))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False


def create_user_session(user_id: int) -> str:
    """Generates a secure cryptographic session token."""
    token = secrets.token_hex(32)
    now = time.time()
    expires_at = now + 86400 * 7  # 7 days

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO user_sessions (token, user_id, created_at, expires_at)
    VALUES (?, ?, ?, ?)
    """, (token, user_id, now, expires_at))
    conn.commit()
    conn.close()
    return token


def authenticate_user(email_or_phone: str, password: str) -> Optional[Dict[str, Any]]:
    """Validates user password credentials."""
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = hash_password(password)

    cursor.execute("""
    SELECT id, full_name, email, phone, role, agency, is_verified
    FROM users
    WHERE (email = ? OR phone = ?) AND password_hash = ?
    """, (email_or_phone, email_or_phone, pwd_hash))

    row = cursor.fetchone()
    conn.close()
    if row:
        user_dict = dict(row)
        token = create_user_session(user_dict["id"])
        user_dict["token"] = token
        return user_dict
    return None


def register_user(full_name: str, email: str, phone: str, role: str, agency: str, password: str) -> Dict[str, Any]:
    """Registers a new user and sends an initial verification OTP."""
    conn = get_db()
    cursor = conn.cursor()

    # Check for existing email or phone
    cursor.execute("SELECT id FROM users WHERE email = ? OR phone = ?", (email, phone))
    if cursor.fetchone():
        conn.close()
        raise ValueError("A user with this email or phone number already exists.")

    pwd_hash = hash_password(password)
    cursor.execute("""
    INSERT INTO users (full_name, email, phone, role, agency, password_hash, is_verified)
    VALUES (?, ?, ?, ?, ?, ?, 0)
    """, (full_name, email, phone, role, agency, pwd_hash))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Generate initial OTP
    otp_code, sms_preview = generate_otp(phone, action="REGISTRATION")
    token = create_user_session(user_id)

    return {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "role": role,
        "agency": agency,
        "token": token,
        "otp_code": otp_code,
        "sms_preview": sms_preview
    }


def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    """Retrieves user profile from active session token."""
    conn = get_db()
    cursor = conn.cursor()
    now = time.time()

    cursor.execute("""
    SELECT u.id, u.full_name, u.email, u.phone, u.role, u.agency, u.is_verified
    FROM user_sessions s
    JOIN users u ON s.user_id = u.id
    WHERE s.token = ? AND s.expires_at > ?
    """, (token, now))

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
