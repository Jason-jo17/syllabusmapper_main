import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="[9902546688#$Jjd]",
    host="db.xjfsbabmhnwamplgdlgo.supabase.co",
    port="5432"
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("TRUNCATE TABLE job_roles CASCADE;")
cur.execute("TRUNCATE TABLE syllabi CASCADE;")
cur.execute("TRUNCATE TABLE colleges CASCADE;")
print("Tables truncated")
cur.close()
conn.close()
