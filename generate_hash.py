#!/usr/bin/env python3
"""
Script to generate bcrypt hash for password
Run this on your server to get the correct hash for your environment
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "senha123"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hashed}")
print("\nRun this SQL to update the database:")
print(f"UPDATE usuarios SET senha_hash = '{hashed}' WHERE email = 'coraline@gmail.com';")
