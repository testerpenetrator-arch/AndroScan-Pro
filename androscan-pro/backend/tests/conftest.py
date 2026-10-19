import os

# Permite ejecutar la suite sin PostgreSQL local; producción usa DATABASE_URL PostgreSQL.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_androscan.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-only-32-bytes-long!!")
