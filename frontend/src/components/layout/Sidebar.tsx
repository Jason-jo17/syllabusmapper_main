"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  Map as MapIcon, 
  LayoutGrid, 
  BarChart2, 
  AlertTriangle, 
  Upload, 
  GraduationCap,
  Calendar
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: GraduationCap },
  { href: "/map", label: "Skills Map", icon: MapIcon },
  { href: "/grid", label: "Curriculum Grid", icon: LayoutGrid },
  { href: "/events", label: "Events Browser", icon: Calendar },
  { href: "/compare", label: "Compare Roles", icon: BarChart2 },
  { href: "/gap", label: "Gap Analysis", icon: AlertTriangle },
  { href: "/upload", label: "Upload Syllabus", icon: Upload },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[240px] flex-shrink-0 bg-[var(--bg1)] border-r border-[var(--bd)] flex flex-col transition-colors duration-200">
      <div className="p-4 border-b border-[var(--bd)]">
        <h1 className="text-[var(--tx)] font-bold text-lg leading-tight">SyllabusMapper</h1>
        <p className="text-[var(--acc)] text-[11px] font-mono mt-0.5">L0–L5 Intelligence</p>
      </div>

      {/* Role Selector Placeholder */}
      <div className="p-4 border-b border-[var(--bd)]">
        <div className="text-[10px] uppercase font-mono tracking-wider text-[var(--tx3)] mb-2">Selected Role</div>
        <select className="w-full bg-[var(--bg2)] border border-[var(--bd)] text-sm text-[var(--tx)] rounded-md px-2 py-1.5 focus:outline-none focus:border-[var(--acc)] transition-colors">
          <option value="ece">Embedded Electronics</option>
          <option value="swdev">Software Developer</option>
          <option value="dataeng">Data Engineer</option>
          <option value="fssd">Full Stack DataDev</option>
        </select>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                isActive 
                  ? "bg-[var(--glow)] text-[var(--acc2)] font-medium" 
                  : "text-[var(--tx2)] hover:bg-[var(--bg2)] hover:text-[var(--tx)]"
              }`}
            >
              <item.icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Level Legend */}
      <div className="p-4 border-t border-[var(--bd)] text-[10px] font-mono">
        <div className="text-[var(--tx3)] mb-2 uppercase tracking-widest">Levels</div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2 text-[var(--tx2)]"><span className="w-2 h-2 rounded bg-[#f59e0b]"></span>L0 Foundation</div>
          <div className="flex items-center gap-2 text-[var(--tx2)]"><span className="w-2 h-2 rounded bg-[#3b82f6]"></span>L1 Intern Trainee</div>
          <div className="flex items-center gap-2 text-[var(--tx2)]"><span className="w-2 h-2 rounded bg-[#22c55e]"></span>L2 Junior Engineer</div>
          <div className="flex items-center gap-2 text-[var(--tx2)]"><span className="w-2 h-2 rounded bg-[#a855f7]"></span>L3 Mid-Level</div>
          <div className="flex items-center gap-2 text-[var(--tx2)]"><span className="w-2 h-2 rounded bg-[#f43f5e]"></span>L4 Senior Engineer</div>
          <div className="flex items-center gap-2 text-[var(--tx2)]"><span className="w-2 h-2 rounded bg-[#06b6d4]"></span>L5 Principal</div>
        </div>
      </div>
    </aside>
  );
}
