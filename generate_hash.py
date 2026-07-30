"""Run to generate bcrypt hash for admin password."""
import bcrypt

password = input("Enter admin password: ").encode()
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(f"\nHash: {hashed.decode()}")
print("\nPaste this into ADMIN_PASSWORD_HASH in .env")
