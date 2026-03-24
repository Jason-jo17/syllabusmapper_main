"use client";
import { useState } from "react";
import { Loader2, Plus } from "lucide-react";

export function ManualEntryForm({ onComplete }: { onComplete: (co_id: string) => void }) {
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    year: "4th",
    stream: "ECE",
    semester: "7th",
    course_code: "",
    course_name: "",
    co_code: "CO1",
    co_description: "",
    yr_stream_course: "",
    course_co_code: ""
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/ingest/manual`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      
      const data = await res.json();
      if (res.ok && data.co_id) {
        // Form submitted successfully, clear description so they can add CO2
        setFormData(prev => ({ 
          ...prev, 
          co_code: `CO${parseInt(prev.co_code.replace('CO','')) + 1}`,
          co_description: "",
          yr_stream_course: "",
          course_co_code: ""
        }));
        onComplete(data.co_id);
      }
    } catch (error) {
      console.error("Submission failed", error);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl mx-auto bg-[#14172a] p-8 rounded-xl border border-[#232640]">
      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Year</label>
          <input required type="text" name="year" value={formData.year} onChange={handleChange} placeholder="e.g. 4th" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
        <div>
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Stream</label>
          <input required type="text" name="stream" value={formData.stream} onChange={handleChange} placeholder="e.g. ECE" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
        <div>
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Semester</label>
          <input required type="text" name="semester" value={formData.semester} onChange={handleChange} placeholder="e.g. 7th" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1">
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Course Code</label>
          <input required type="text" name="course_code" value={formData.course_code} onChange={handleChange} placeholder="e.g. 21EC751" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
        <div className="col-span-2">
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Course Name</label>
          <input required type="text" name="course_name" value={formData.course_name} onChange={handleChange} placeholder="e.g. Optical & Satellite Communication" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
      </div>

      <div className="h-px w-full bg-[#232640] my-2"></div>

      <div>
        <div className="flex justify-between items-center mb-1.5">
          <label className="block text-xs font-medium text-[#8b93b8] uppercase">Course Outcome (CO)</label>
          <input required type="text" name="co_code" value={formData.co_code} onChange={handleChange} className="bg-[#09090f] border border-[#232640] rounded px-2 py-0.5 text-xs text-[#a5b4fc] w-16 text-center focus:border-[#6366f1] focus:outline-none font-mono" />
        </div>
        <textarea 
          required 
          name="co_description" 
          value={formData.co_description} 
          onChange={handleChange} 
          placeholder="Describe the learning outcome..." 
          rows={3}
          className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none resize-none" 
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Yr + Stream + Course</label>
          <input required type="text" name="yr_stream_course" value={formData.yr_stream_course} onChange={handleChange} placeholder="e.g. 4th ECE 21EC751" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
        <div>
          <label className="block text-xs font-medium text-[#8b93b8] uppercase mb-1.5">Course + CO + Code</label>
          <input required type="text" name="course_co_code" value={formData.course_co_code} onChange={handleChange} placeholder="e.g. 21EC751 CO1" className="w-full bg-[#09090f] border border-[#232640] rounded-lg px-3 py-2 text-sm text-[#e2e6f8] focus:border-[#6366f1] focus:outline-none" />
        </div>
      </div>

      <button disabled={submitting} type="submit" className="w-full flex items-center justify-center gap-2 bg-[#6366f1] hover:bg-[#4f46e5] text-white px-5 py-2.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
        {submitting ? <Loader2 className="animate-spin" size={18} /> : <Plus size={18} />}
        {submitting ? "Mapping to Framework..." : "Add Course Outcome"}
      </button>
    </form>
  );
}
