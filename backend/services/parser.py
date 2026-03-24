"""
Parses raw syllabus text → structured JSON with courses + COs.
Handles chunking for large documents (>12k chars).
Auto-detects Bloom's level from CO action verbs.
"""
import google.generativeai as genai
import json, os

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

SYSTEM = """You are a precise academic syllabus parser. Extract structured data and return ONLY valid JSON.

Schema:
{
  "stream": "ECE|CSE|ME|EE|...",
  "regulation": "2021 Scheme|2018 Regulation|...",
  "semesters": [{
    "semester_num": 3,
    "semester_label": "3rd Semester",
    "year_of_study": 2,
    "courses": [{
      "course_code": "21EC32",
      "course_title": "Digital System Design using Verilog",
      "credits": 4,
      "course_type": "core|elective|lab|project",
      "topics": ["module 1 topic list as string", "module 2..."],
      "course_outcomes": [{
        "co_code": "CO1",
        "description": "Full CO description text",
        "bloom_verb": "Apply",
        "bloom_level": 3
      }]
    }]
  }]
}

Bloom's levels: 1=Remember(list/recall), 2=Understand(explain/describe),
3=Apply(apply/use/demonstrate), 4=Analyse(analyse/compare/differentiate),
5=Evaluate(evaluate/judge/critique), 6=Create(design/create/develop/build)

Extract ALL courses and ALL COs. Never truncate. Unknown fields → null."""

async def parse(raw_text: str, hint_stream: str = None) -> dict:
    hint = f"\nHint: {hint_stream} stream." if hint_stream else ""
    if len(raw_text) > 12000:
        return await _chunked_parse(raw_text, hint_stream)
        
    prompt = f"System Instruction:\n{SYSTEM}\n\nUser Request:\nParse:{hint}\n\n{raw_text[:12000]}"
    response = await model.generate_content_async(
        prompt,
        generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
    )
    text = response.text.strip()
    if text.startswith('```'): text = text[text.find('{'):text.rfind('}')+1]
    return json.loads(text)

async def _chunked_parse(raw_text, hint_stream):
    chunks = [raw_text[i:i+11000] for i in range(0, len(raw_text), 11000)]
    all_sems = []; stream = None; reg = None
    for chunk in chunks:
        try:
            r = await parse(chunk, hint_stream)
            if not stream: stream = r.get('stream'); reg = r.get('regulation')
            all_sems.extend(r.get('semesters', []))
        except: pass
    seen = set(); uniq = []
    for sem in all_sems:
        courses = [c for c in sem.get('courses',[]) if c.get('course_code') not in seen and not seen.add(c.get('course_code',''))]
        if courses: sem['courses'] = courses; uniq.append(sem)
    return {'stream': stream, 'regulation': reg, 'semesters': uniq}
