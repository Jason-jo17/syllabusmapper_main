"use client";

import { useEffect, useState } from "react";
import { 
  GraduationCap, 
  LayoutGrid, 
  Map as MapIcon, 
  Calendar, 
  AlertTriangle, 
  ArrowRight,
  Target,
  Zap
} from "lucide-react";
import Link from "next/link";
import { motion } from "framer-motion";

export default function Dashboard() {
  const [stats, setStats] = useState({
    courses: 48,
    skills: 1240,
    events: 24,
    gaps: 15
  });

  return (
    <div className="p-8 max-w-6xl mx-auto pb-32">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-12 relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#1a1d32] to-[#0f111a] border border-[#232640] p-8 md:p-12 shadow-2xl"
      >
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[rgba(99,102,241,0.1)] border border-[rgba(99,102,241,0.2)] text-[var(--acc2)] text-xs font-mono mb-6">
            <Zap size={14} className="animate-pulse" />
            AI-Powered Curriculum Intelligence
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-[#e2e6f8] mb-4 leading-tight">
            Map Your Curriculum to <br/>
            <span className="text-[var(--acc)]">Industry Excellence</span>
          </h1>
          <p className="text-[#8b93b8] text-lg max-w-2xl mb-8 leading-relaxed">
            Analyze, align, and bridge the gap between academic learning and real-world professional requirements with L0–L5 technical intelligence.
          </p>
          <div className="flex flex-wrap gap-4">
            <Link href="/grid" className="px-6 py-3 bg-[var(--acc)] text-black font-bold rounded-xl hover:bg-[var(--acc2)] transition-all flex items-center gap-2 group shadow-[0_0_20px_rgba(232,150,12,0.3)]">
              View Curriculum Grid
              <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/map" className="px-6 py-3 bg-[#232640] text-[#e2e6f8] font-bold rounded-xl border border-[#303651] hover:bg-[#2a2f4a] transition-all">
              Explore Skills Map
            </Link>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[80%] bg-[var(--acc)] opacity-[0.03] blur-[100px] rounded-full pointer-events-none"></div>
        <div className="absolute bottom-[-20%] left-[-10%] w-[30%] h-[60%] bg-[#4f46e5] opacity-[0.05] blur-[80px] rounded-full pointer-events-none"></div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <StatCard icon={GraduationCap} label="Total Courses" value={stats.courses} color="blue" />
        <StatCard icon={Target} label="Skills Mapped" value={stats.skills} color="green" />
        <StatCard icon={Calendar} label="Active Events" value={stats.events} color="purple" />
        <StatCard icon={AlertTriangle} label="Industry Gaps" value={stats.gaps} color="orange" />
      </div>

      {/* Quick Actions / Featured sections */}
      <h2 className="text-xl font-bold text-[#e2e6f8] mb-6 flex items-center gap-2">
        Platforms Modules
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ModuleCard 
          href="/grid"
          icon={LayoutGrid}
          title="Curriculum Grid"
          description="A comprehensive view of your entire syllabus mapped to technical levels and outcomes."
        />
        <ModuleCard 
          href="/events"
          icon={Calendar}
          title="Events Browser"
          description="Browse and associate professional events, hackathons, and competitions with curriculum skills."
        />
        <ModuleCard 
          href="/gap"
          icon={AlertTriangle}
          title="Gap Analysis"
          description="Identify where your curriculum falls short of industry job role requirements."
        />
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color }: any) {
  const colorMap: any = {
    blue: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    green: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20",
    purple: "text-purple-400 bg-purple-400/10 border-purple-400/20",
    orange: "text-orange-400 bg-orange-400/10 border-orange-400/20"
  };

  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="bg-[#1a1d32] border border-[#232640] p-6 rounded-2xl shadow-lg transition-colors hover:border-[#303651]"
    >
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 border ${colorMap[color]}`}>
        <Icon size={20} />
      </div>
      <div className="text-3xl font-bold text-[#e2e6f8] mb-1">{value.toLocaleString()}</div>
      <div className="text-[#8b93b8] text-sm">{label}</div>
    </motion.div>
  );
}

function ModuleCard({ href, icon: Icon, title, description }: any) {
  return (
    <Link href={href} className="group">
      <div className="h-full bg-[#1a1d32] border border-[#232640] p-6 rounded-2xl shadow-lg transition-all group-hover:border-[var(--acc)] group-hover:bg-[#1e223a]">
        <div className="w-12 h-12 rounded-xl bg-[#0f111a] border border-[#232640] flex items-center justify-center mb-6 text-[var(--acc)] group-hover:scale-110 transition-transform">
          <Icon size={24} />
        </div>
        <h3 className="text-lg font-bold text-[#e2e6f8] mb-2 group-hover:text-[var(--acc)] transition-colors">{title}</h3>
        <p className="text-[#8b93b8] text-sm leading-relaxed mb-6">{description}</p>
        <div className="text-[var(--acc)] text-xs font-bold flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          Open Module <ArrowRight size={14} />
        </div>
      </div>
    </Link>
  );
}
