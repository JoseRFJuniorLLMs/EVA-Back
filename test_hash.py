#!/usr/bin/env python3
"""Test bcrypt hash generation and verification"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "senha123"

# Generate a NEW hash
new_hash = pwd_context.hash(password)
print(f"Generated hash for '{password}':")
print(new_hash)
print()

# Test verification with the new hash
result = pwd_context.verify(password, new_hash)
print(f"Verification test: {result}")
print()

# Test with the hash you tried to use
old_hash = "$2b$12$9vZ3pJ3qX5F5F5F5F5F5F.eKqVqVqVqVqVqVqVqVqVqVqVqVqVqVq"
print(f"Testing old hash: {old_hash}")
try:
    result2 = pwd_context.verify(password, old_hash)
    print(f"Old hash verification: {result2}")
except Exception as e:
    print(f"Error with old hash: {e}")
print()

print("SQL Command to update database:")
print(f"UPDATE usuarios SET senha_hash = '{new_hash}' WHERE email = 'coraline@gmail.com';")
