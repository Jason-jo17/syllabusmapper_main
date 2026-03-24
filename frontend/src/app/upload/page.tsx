"use client";
import { useState } from "react";
import { DropZone } from "@/components/upload/DropZone";
import { IngestionStatus } from "@/components/upload/IngestionStatus";
import { ManualEntryForm } from "@/components/upload/ManualEntryForm";
import { useRouter } from "next/navigation";
import { FileText, FileSpreadsheet, Keyboard } from "lucide-react";

export default function UploadPage() {
  const [ingestingId, setIngestingId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("pdf"); // pdf, csv, manual
  const router = useRouter();

  return (
    <div className="p-12 flex flex-col justify-center min-h-[80vh]">
      <div className="max-w-4xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-[#e2e6f8] mb-4 text-center">Process New Syllabus</h1>
        <p className="text-[#8b93b8] text-center mb-8 max-w-2xl mx-auto leading-relaxed text-sm">
          Upload a college syllabus in PDF format for AI extraction, or use structured CSV and manual entry to inject data directly into the industry framework.
        </p>

        {!ingestingId && (
          <div className="flex justify-center mb-10 border-b border-[#232640]">
            <button onClick={() => setActiveTab("pdf")} className={`flex justify-center items-center gap-2 pb-4 px-6 text-sm font-medium transition-colors ${activeTab === 'pdf' ? 'text-[#e2e6f8] border-b-2 border-[#6366f1]' : 'text-[#454e72] hover:text-[#8b93b8]'}`}>
              <FileText size={16} /> Smart Upload (PDF)
            </button>
            <button onClick={() => setActiveTab("csv")} className={`flex justify-center items-center gap-2 pb-4 px-6 text-sm font-medium transition-colors ${activeTab === 'csv' ? 'text-[#e2e6f8] border-b-2 border-[#6366f1]' : 'text-[#454e72] hover:text-[#8b93b8]'}`}>
              <FileSpreadsheet size={16} /> Bulk Upload (CSV)
            </button>
            <button onClick={() => setActiveTab("manual")} className={`flex justify-center items-center gap-2 pb-4 px-6 text-sm font-medium transition-colors ${activeTab === 'manual' ? 'text-[#e2e6f8] border-b-2 border-[#6366f1]' : 'text-[#454e72] hover:text-[#8b93b8]'}`}>
              <Keyboard size={16} /> Manual Data Entry
            </button>
          </div>
        )}

        {!ingestingId ? (
          <>
            {activeTab === "pdf" && <DropZone onUploadComplete={setIngestingId} mode="pdf" />}
            {activeTab === "csv" && <DropZone onUploadComplete={setIngestingId} mode="csv" />}
            {activeTab === "manual" && <ManualEntryForm onComplete={setIngestingId} />}
          </>
        ) : (
          <IngestionStatus 
            syllabusId={ingestingId} 
            onComplete={() => router.push(`/grid?syl=${ingestingId}`)} 
          />
        )}
      </div>
    </div>
  );
}
