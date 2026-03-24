import psycopg2
import pandas as pd
import uuid

def ingest_events():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="[9902546688#$Jjd]",
        host="db.xjfsbabmhnwamplgdlgo.supabase.co",
        port="5432"
    )
    conn.autocommit = True
    cur = conn.cursor()

    print("Creating 'events' table...")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        event_name TEXT,
        organizing_body TEXT,
        description TEXT,
        problem_statement TEXT,
        registration_links TEXT,
        keywords TEXT,
        event_registration_deadline TEXT,
        event_date TEXT,
        location TEXT,
        mode TEXT,
        knowledge_domain_1 TEXT,
        knowledge_domain_2 TEXT,
        knowledge_domain_3 TEXT,
        exposure_status TEXT,
        exposure_score TEXT,
        bl_level TEXT,
        bl_level_no TEXT,
        bl_level_change TEXT,
        bl_level_change_no TEXT,
        cumulative_bl TEXT,
        recognition TEXT,
        monetary TEXT,
        career TEXT,
        exceptional TEXT,
        total_score TEXT,
        event_type TEXT,
        emi_score TEXT,
        knowledge_set_1 TEXT,
        skill_knowledge_1 TEXT,
        bl_level_1 TEXT,
        knowledge_set_2 TEXT,
        skill_knowledge_2 TEXT,
        bl_level_2 TEXT,
        knowledge_set_3 TEXT,
        skill_knowledge_3 TEXT,
        bl_level_3 TEXT,
        kn_set_avrg TEXT,
        ranking_index TEXT,
        image_url TEXT
    );
    """)

    csv_path = r"D:\Event Mastersheet mockup - Copy of tester 2 (2).csv"
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Clean col names
    columns = [
        "Event Name", "Organizing Body", "Description of Event", "problem statement description",
        "Registration Links", "Keywords ( event + problem statement)", "Event registration Deadline",
        "Current year event date", "Location", "Mode",
        "Knowledge Domain 1", "Knowledge Domain 2", "Knowledge Domain 3",
        "Exposure status", "Exposure score", "Bl level", "bl level no", "Bl level change",
        "bl Level change no", "cumulative bl", "Recognition", "Monetary", "Career", "Exceptional",
        "Total", "Event type", "EMI score",
        "knowledge set 1", "skill knowledge", "Bl level 1",
        "knowledge set 2", "skill knowledge.1", "Bl level 2",
        "knowledge set 3", "skill knowledge.2", "Bl level 3",
        "kn set avrg", "ranking( index)", "image url"
    ]
    
    # Try reading headers dynamically but pandas auto renames duplicate columns like "skill knowledge", "skill knowledge.1" etc.
    # Let's map df columns safely.
    
    insert_query = """
    INSERT INTO events (
        event_name, organizing_body, description, problem_statement, registration_links, keywords,
        event_registration_deadline, event_date, location, mode, 
        knowledge_domain_1, knowledge_domain_2, knowledge_domain_3,
        exposure_status, exposure_score, bl_level, bl_level_no, bl_level_change, bl_level_change_no, cumulative_bl,
        recognition, monetary, career, exceptional, total_score, event_type, emi_score,
        knowledge_set_1, skill_knowledge_1, bl_level_1,
        knowledge_set_2, skill_knowledge_2, bl_level_2,
        knowledge_set_3, skill_knowledge_3, bl_level_3,
        kn_set_avrg, ranking_index, image_url
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    
    inserted = 0
    cur.execute("TRUNCATE TABLE events;") # Clear existing for clean ingest
    
    for i, row in df.iterrows():
        try:
            event_name = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
            if not event_name or event_name.strip() == "":
                continue
                
            data = (
                str(row.iloc[0]) if pd.notna(row.iloc[0]) else None,  # Event Name
                str(row.iloc[1]) if pd.notna(row.iloc[1]) else None,  # Organizing Body
                str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,  # Description
                str(row.iloc[3]) if pd.notna(row.iloc[3]) else None,  # problem statement
                str(row.iloc[4]) if pd.notna(row.iloc[4]) else None,  # Registration Links
                str(row.iloc[5]) if pd.notna(row.iloc[5]) else None,  # Keywords
                str(row.iloc[6]) if pd.notna(row.iloc[6]) else None,  # Deadline
                str(row.iloc[7]) if pd.notna(row.iloc[7]) else None,  # Date
                str(row.iloc[8]) if pd.notna(row.iloc[8]) else None,  # Location
                str(row.iloc[9]) if pd.notna(row.iloc[9]) else None,  # Mode
                str(row.iloc[15]) if pd.notna(row.iloc[15]) else None, # KD1
                str(row.iloc[16]) if pd.notna(row.iloc[16]) else None, # KD2
                str(row.iloc[17]) if pd.notna(row.iloc[17]) else None, # KD3
                str(row.iloc[18]) if pd.notna(row.iloc[18]) else None, # Exposure status
                str(row.iloc[19]) if pd.notna(row.iloc[19]) else None, # Exposure score
                str(row.iloc[20]) if pd.notna(row.iloc[20]) else None, # Bl level
                str(row.iloc[21]) if pd.notna(row.iloc[21]) else None, # bl level no
                str(row.iloc[22]) if pd.notna(row.iloc[22]) else None, # Bl level change
                str(row.iloc[23]) if pd.notna(row.iloc[23]) else None, # bl Level change no
                str(row.iloc[24]) if pd.notna(row.iloc[24]) else None, # cumulative bl
                str(row.iloc[25]) if pd.notna(row.iloc[25]) else None, # Recognition
                str(row.iloc[26]) if pd.notna(row.iloc[26]) else None, # Monetary
                str(row.iloc[27]) if pd.notna(row.iloc[27]) else None, # Career
                str(row.iloc[28]) if pd.notna(row.iloc[28]) else None, # Exceptional
                str(row.iloc[29]) if pd.notna(row.iloc[29]) else None, # Total
                str(row.iloc[30]) if pd.notna(row.iloc[30]) else None, # Event type
                str(row.iloc[31]) if pd.notna(row.iloc[31]) else None, # EMI score
                str(row.iloc[32]) if pd.notna(row.iloc[32]) else None, # knowledge set 1
                str(row.iloc[33]) if pd.notna(row.iloc[33]) else None, # skill knowledge 1
                str(row.iloc[34]) if pd.notna(row.iloc[34]) else None, # Bl level 1
                str(row.iloc[35]) if pd.notna(row.iloc[35]) else None, # knowledge set 2
                str(row.iloc[36]) if pd.notna(row.iloc[36]) else None, # skill knowledge 2
                str(row.iloc[37]) if pd.notna(row.iloc[37]) else None, # Bl level 2
                str(row.iloc[38]) if pd.notna(row.iloc[38]) else None, # knowledge set 3
                str(row.iloc[39]) if pd.notna(row.iloc[39]) else None, # skill knowledge 3
                str(row.iloc[40]) if pd.notna(row.iloc[40]) else None, # Bl level 3
                str(row.iloc[41]) if pd.notna(row.iloc[41]) else None, # kn set avrg
                str(row.iloc[42]) if pd.notna(row.iloc[42]) else None, # ranking(index)
                str(row.iloc[43]) if pd.notna(row.iloc[43]) else None, # image url
            )
            cur.execute(insert_query, data)
            inserted += 1
        except Exception as e:
            print(f"Error on row {i}: {e}")
            
    print(f"Successfully inserted {inserted} events into the database.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    ingest_events()
