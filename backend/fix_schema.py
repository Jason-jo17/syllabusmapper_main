import psycopg2

def fix_schema():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="[9902546688#$Jjd]",
        host="db.xjfsbabmhnwamplgdlgo.supabase.co",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Checking 'courses' table...")
    cur.execute("ALTER TABLE courses ADD COLUMN IF NOT EXISTS title TEXT;")
    
    print("Checking 'skill_nodes' table...")
    # Add denormalized CO columns for frontend display
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_primary_text TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_primary_course TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_primary_year TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_primary_sem TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_secondary_text TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_secondary_course TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_secondary_year TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_secondary_sem TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_tertiary_text TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_tertiary_course TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_tertiary_year TEXT;")
    cur.execute("ALTER TABLE skill_nodes ADD COLUMN IF NOT EXISTS co_tertiary_sem TEXT;")
    
    print("Schema fixed.")
    
    # Just to be safe, check if there are any courses without syllabus_id that should have one
    SYL_ID = "ece00000-0000-0000-0000-000000000000"
    cur.execute(f"UPDATE courses SET syllabus_id = '{SYL_ID}' WHERE syllabus_id IS NULL;")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    fix_schema()
