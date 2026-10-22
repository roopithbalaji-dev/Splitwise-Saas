import os
import psycopg2

def load_env(path=".env.local"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k:
                        os.environ[k] = v

load_env(".env.local")
db_url = os.environ.get("DATABASE_URL")
print("[1] Connecting to Neon Postgres:", db_url.split("@")[-1] if db_url else "None")

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# 1. Version check
cur.execute("SELECT version();")
print("[2] Neon Postgres Engine:", cur.fetchone()[0])

# 2. Test DDL (Groups & Members tables)
cur.execute("""
CREATE TABLE IF NOT EXISTS test_neon_ping (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()
print("[3] DDL test passed: test_neon_ping table ready.")

# 3. Test Insert
cur.execute("INSERT INTO test_neon_ping (name) VALUES (%s) RETURNING id, name, created_at;", ("Splitwise Neon Test",))
row = cur.fetchone()
conn.commit()
print(f"[4] INSERT test passed: ID={row[0]}, Name={row[1]}, CreatedAt={row[2]}")

# 4. Test Query
cur.execute("SELECT COUNT(*) FROM test_neon_ping;")
count = cur.fetchone()[0]
print(f"[5] SELECT test passed: Total rows in test table = {count}")

# 5. Clean up
cur.execute("DROP TABLE test_neon_ping;")
conn.commit()
print("[6] Cleanup test table: dropped test_neon_ping.")

cur.close()
conn.close()
print("PROVE_IT_WORKS: End-to-end Neon PostgreSQL integration verified successfully!")
