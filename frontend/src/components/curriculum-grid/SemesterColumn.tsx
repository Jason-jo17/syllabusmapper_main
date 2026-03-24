"use client";
import { CourseCard } from "./CourseCard";
import type { Course, SkillNode } from "@/lib/types";

interface Props {
  semesterLabel: string;
  courses: Course[];
  getCourseSkills: (cid: string) => SkillNode[];
  activeFilter: 'none'|'ece'|'l0l1'|'l2l3'|'l4l5';
  selectedCourseId: string | null;
  onSelectCourse: (course: Course) => void;
}

export function SemesterColumn({ semesterLabel, courses, getCourseSkills, activeFilter, selectedCourseId, onSelectCourse }: Props) {
  
  const filterSkills = (skills: SkillNode[], filter: string) => {
    if (filter === 'none' || filter === 'ece') return skills;
    if (filter === 'l0l1') return skills.filter(s => s.level==='L0'||s.level==='L1');
    if (filter === 'l2l3') return skills.filter(s => s.level==='L2'||s.level==='L3');
    if (filter === 'l4l5') return skills.filter(s => s.level==='L4'||s.level==='L5');
    return skills;
  };

  return (
    <div className="w-[300px] flex-shrink-0 bg-[var(--bg)] border-r border-[var(--bd)] flex flex-col h-full overflow-hidden transition-colors duration-200">
      <div className="p-3 border-b border-[var(--bd)] bg-[var(--bg1)] sticky top-0 z-10 flex-shrink-0">
        <h3 className="text-[12px] font-bold text-[var(--tx)]">{semesterLabel}</h3>
        <p className="text-[10px] text-[var(--tx2)] mt-0.5">{courses.length} courses</p>
      </div>
      <div className="p-3 overflow-y-auto flex-1">
        {courses.map(course => {
          const allSk = getCourseSkills(course.id);
          const mappedSk = filterSkills(allSk, activeFilter);
          
          let coverageType: 'direct'|'partial'|'prereq'|'none' = 'none';
          if (mappedSk.length > 0 || (course.skill_count && course.skill_count > 0)) coverageType = 'direct';
          
          return (
            <CourseCard
              key={course.id}
              course={course}
              allSkills={allSk}
              mappedSkills={mappedSk}
              coverageType={coverageType}
              isSelected={selectedCourseId === course.id}
              trackFilter={activeFilter}
              onClick={() => onSelectCourse(course)}
            />
          );
        })}
      </div>
    </div>
  );
}
