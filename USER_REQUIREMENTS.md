# SyllabusMapper Setup Checklist

To bring the SyllabusMapper platform to life, we need a few specific files and configuration keys from you. 

Here is everything needed to complete the setup and run the application locally.

## 1. The Excel Files (Data Seeding)
The AI backend requires your industry mapping data to generate embeddings and populate the PostgreSQL database. Please provide the following 4 files. 

You can either **drag and drop them into the chat** so I can place them for you, or you can manually place them in the `backend/data/` folder:
- [ ] `ECE_L0L5_VTU_CO_v2.xlsx`
- [ ] `SW_Dev_L0_L5_Concepts_Skills.xlsx`
- [ ] `Data_Engineer_L0_L5_Breakdown.xlsx`
- [ ] `FullStack_DataDev_L0_L5_Breakdown.xlsx`

---

## 2. API Keys & Environment Variables
The application relies on Supabase for the Vector Database, Anthropic for parsing/mapping, and Voyage AI for embedding. 

You will need to create and populate the following `.env` files.

### Backend (`backend/.env`)
Create a file named `.env` in the `backend/` directory with the following keys:
```env
# Supabase Configuration (Use the Service Role Key for Admin privileges)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key

# Supabase Storage (Optional for this iteration, but good to have)
SUPABASE_BUCKET=syllabi

# AI API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key
VOYAGE_API_KEY=your_voyage_api_key
```

### Frontend (`frontend/.env.local`)
Create a file named `.env.local` in the `frontend/` directory with the following keys:
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# Backend URL (Leave as is for local development)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 3. Database Migration
Before we can seed the data, the Supabase database needs the correct tables and `pgvector` extensions.
- [ ] Go to your Supabase project dashboard.
- [ ] Open the **SQL Editor**.
- [ ] Copy and paste the contents of `supabase/migrations/001_schema.sql` and click **Run**.
- [ ] Copy and paste the contents of `supabase/migrations/002_vector_functions.sql` and click **Run**.

---

## 4. Run the Application
Once the above is complete, you are ready to launch!

**Step A: Seed the Database**
Run the ingestion script to parse the Excel files, generate embeddings, and store them in Supabase.
```bash
cd backend
python data/seed_l0l5.py
```

**Step B: Start the AI Backend**
Start the FastAPI server.
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Step C: Start the Frontend UI**
Start the Next.js React application.
```bash
cd frontend
npm run dev
```
