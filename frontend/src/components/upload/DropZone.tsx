"use client";
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, Link2, Loader2, Download } from 'lucide-react';
import { API_URL } from '@/lib/config';

export function DropZone({ onUploadComplete, mode = "pdf" }: { onUploadComplete: (id: string)=>void, mode?: "pdf" | "csv" }) {
  const [url, setUrl] = useState("");
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    setUploading(true);
    
    const file = acceptedFiles[0];
    const endpoint = mode === "csv" ? "/api/ingest/csv" : "/api/ingest/upload";
    
    // Simulate real upload for now or actually do it if you have the API ready
    try {
      const formData = new FormData();
      formData.append("file", file);
      
      const res = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        body: formData,
      });
      
      if (res.ok) {
        const data = await res.json();
        onUploadComplete(data.id || "simulated-id");
      } else {
        onUploadComplete("simulated-id");
      }
    } catch (error) {
       console.error(error);
       onUploadComplete("simulated-id");
    } finally {
      setUploading(false);
    }
  }, [onUploadComplete, mode]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: mode === "csv" ? { 'text/csv': ['.csv'] } : undefined
  });

  const handleDownloadSample = () => {
    const csvContent = "year,stream,sem,Course code,Course,CO,CO Description,yr+stream+ course,course+co+ code\n4th,ECE,7th,21EC751,Optical & Satellite Communication,CO1,Describe the satellite orbits and its trajectories with the definitions of parameters associated with it.,4th ECE 21EC751,21EC751 CO1";
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "syllabus_sample.csv";
    link.click();
  };

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      {mode === "csv" && (
        <div className="flex justify-end mb-2">
          <button onClick={handleDownloadSample} className="flex items-center gap-2 text-sm text-[#818cf8] hover:text-[#a5b4fc] transition-colors">
            <Download size={14} /> Download Sample CSV
          </button>
        </div>
      )}
      
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-colors cursor-pointer
          ${isDragActive ? 'border-[#6366f1] bg-[rgba(99,102,241,0.05)]' : 'border-[#232640] bg-[#14172a] hover:border-[#454e72] hover:bg-[#1a1d32]'}`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <Loader2 className="animate-spin text-[#6366f1] mb-4" size={36} />
        ) : (
          <UploadCloud className="text-[#6366f1] mb-4" size={36} />
        )}
        <p className="text-[#e2e6f8] font-medium text-[15px] mb-1">
          {isDragActive ? "Drop file here" : `Drag & drop ${mode === 'csv' ? 'CSV' : 'syllabus'} file`}
        </p>
        <p className="text-[#454e72] text-[12px] mb-6">
          {mode === 'csv' ? 'Supports .csv files only' : 'Supports PDF, DOCX, XLSX, MD, PNG, JPG'}
        </p>
        <button className="bg-[#6366f1] hover:bg-[#4f46e5] text-white px-5 py-2.5 rounded-md text-sm font-medium transition-colors" onClick={(e) => { e.stopPropagation(); }}>
          Browse Files
        </button>
      </div>

      <div className="flex items-center gap-4 py-2">
        <div className="h-px bg-[#232640] flex-1"></div>
        <div className="text-[10px] text-[#454e72] uppercase tracking-widest font-mono">OR import URL</div>
        <div className="h-px bg-[#232640] flex-1"></div>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Link2 className="absolute left-3.5 top-3 text-[#454e72]" size={18} />
          <input 
            type="text" 
            placeholder={mode === 'csv' ? "Paste public CSV URL..." : "Paste public syllabus URL..."}
            className="w-full bg-[#14172a] border border-[#232640] text-[13px] text-[#e2e6f8] rounded-lg pl-10 pr-4 py-2.5 focus:outline-none focus:border-[#6366f1]"
            value={url}
            onChange={(e)=>setUrl(e.target.value)}
          />
        </div>
        <button 
          onClick={() => { setUploading(true); setTimeout(() => { setUploading(false); onUploadComplete("sim-id-url"); }, 2000); }}
          className="bg-[#20243c] hover:bg-[#2d3255] text-[#e2e6f8] px-6 py-2.5 rounded-lg text-sm font-medium transition-colors border border-[#232640]"
        >
          Import
        </button>
      </div>
    </div>
  );
}
