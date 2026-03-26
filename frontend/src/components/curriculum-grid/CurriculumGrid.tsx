"use client";
import { useState, useEffect } from "react";
import { TrackPills } from "./TrackPills";
import { SemesterColumn } from "./SemesterColumn";
import { useSearchParams } from "next/navigation";
import { DetailPanel } from "./DetailPanel";
import type { Course, CourseOutcome, SkillNode, Event } from "@/lib/types";
import { API_URL } from "@/lib/config";

export function CurriculumGrid() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [skillsMap, setSkillsMap] = useState<Record<string, SkillNode[]>>({});
  const [cosMap, setCosMap] = useState<Record<string, CourseOutcome[]>>({});
  const [activeFilter, setActiveFilter] = useState<'none'|'ece'|'l0l1'|'l2l3'|'l4l5'>('none');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const searchParams = useSearchParams();

  const [allEvents, setAllEvents] = useState<Event[]>([]);

  useEffect(() => {
    const syllabusId = searchParams.get('syl') || "ece00000-0000-0000-0000-000000000000";
    
    fetch(`${API_URL}/api/syllabi/${syllabusId}/courses`)
      .then(r => r.json())
      .then(data => {
        setCourses(data || []);
      })
      .catch(err => console.error("Failed to fetch courses:", err));

    fetch(`${API_URL}/api/events`)
      .then(r => r.json())
      .then(data => setAllEvents(data || []))
      .catch(err => console.error("Failed to fetch events:", err));
  }, [searchParams]);

  // Fetch details (COs and Skills) when a course is selected
  useEffect(() => {
    if (!selectedCourse) return;
    
    // Fetch COs
    fetch(`${API_URL}/api/courses/${selectedCourse.id}/cos`)
      .then(r => r.json())
      .then(data => {
        setCosMap(prev => ({ ...prev, [selectedCourse.id]: data }));
      });

    // Fetch Skills
    fetch(`${API_URL}/api/courses/${selectedCourse.id}/skills`)
      .then(r => r.json())
      .then(data => {
        setSkillsMap(prev => ({ ...prev, [selectedCourse.id]: data }));
      });
  }, [selectedCourse]);

  const sems = [
    { label: "Year 1 / Semester 1-2", semNum: 1 },
    { label: "Year 2 / Semester 3", semNum: 3 },
    { label: "Year 2 / Semester 4", semNum: 4 },
    { label: "Year 3 / Semester 5", semNum: 5 },
    { label: "Year 3 / Semester 6", semNum: 6 },
    { label: "Year 4 / Semester 7", semNum: 7 },
    { label: "Year 4 / Semester 8", semNum: 8 },
  ];

  return (
    <div className="flex flex-col h-full absolute inset-0">
      <div className="px-6 py-4 flex-shrink-0 bg-[var(--bg1)]">
        <h1 className="text-2xl font-bold text-[var(--tx)] mb-2">Curriculum Grid</h1>
        <p className="text-[var(--tx2)] mb-4 text-sm">Select a course to view detailed CO-to-skill mappings.</p>
        <div className="flex items-center gap-4">
          <TrackPills activeFilter={activeFilter} onChange={setActiveFilter} />
          <select
            className="bg-[var(--bg2)] border border-[var(--bd)] text-[var(--tx)] rounded px-3 py-1.5 text-sm outline-none w-64 ml-auto"
            value={selectedCourse?.id || ""}
            onChange={(e) => {
              const c = courses.find((c) => c.id === e.target.value);
              setSelectedCourse(c || null);
            }}
          >
            <option value="">-- Select Course (Dropdown) --</option>
            {sems.map((sem) => {
              const semCourses = courses.filter(
                (c) => c.semester === sem.semNum || (sem.semNum === 1 && c.semester === 2)
              );
              if (semCourses.length === 0) return null;
              return (
                <optgroup key={sem.semNum} label={sem.label}>
                  {semCourses.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.course_code} - {c.course_title}
                    </option>
                  ))}
                </optgroup>
              );
            })}
          </select>
        </div>
      </div>
      
      <div className="flex-1 overflow-hidden relative border-t border-[var(--bd)] w-full">
        <div className="flex h-full overflow-x-auto bg-[var(--bg)]">
          {sems.map(sem => (
            <SemesterColumn
              key={sem.semNum}
              semesterLabel={sem.label}
              courses={courses.filter(c => c.semester === sem.semNum || (sem.semNum===1 && c.semester===2))}
              getCourseSkills={(cid) => skillsMap[cid] || []}
              activeFilter={activeFilter}
              selectedCourseId={selectedCourse?.id || null}
              onSelectCourse={(c) => setSelectedCourse(c)}
            />
          ))}
        </div>
        
        {/* Detail Panel */}
        <DetailPanel
          course={selectedCourse}
          cos={selectedCourse ? (cosMap[selectedCourse.id] || []) : []}
          mappedSkills={selectedCourse ? (skillsMap[selectedCourse.id] || []) : []}
          allEvents={allEvents}
          onClose={() => setSelectedCourse(null)}
        />
      </div>
    </div>
  );
}
