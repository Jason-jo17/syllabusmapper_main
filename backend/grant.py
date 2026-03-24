import psycopg2
from urllib.parse import urlparse, unquote

db_url = "postgresql://postgres:[9902546688#$Jjd]@db.xjfsbabmhnwamplgdlgo.supabase.co:5432/postgres"

# The password is "[9902546688#$Jjd]"
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="[9902546688#$Jjd]",
    host="db.xjfsbabmhnwamplgdlgo.supabase.co",
    port="5432"
)

conn.autocommit = True
cur = conn.cursor()

# Grant usage on schema
cur.execute("GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;")

# Grant all privileges on all tables in public
cur.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO anon, authenticated, service_role;")

# Grant privileges on sequences (for gen_random_uuid etc if any)
cur.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;")

# Alter default privileges for future tables
cur.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated, service_role;")

print("Permissions granted successfully.")
cur.close()
conn.close()
