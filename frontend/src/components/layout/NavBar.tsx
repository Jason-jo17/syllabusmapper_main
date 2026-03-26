"use client";
import { Moon, Sun, Link2, Link2Off } from "lucide-react";
import { useEffect, useState } from "react";

export function NavBar() {
  const [dark, setDark] = useState(true);
  const [apiUrl, setApiUrl] = useState<string>("");

  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setDark(isDark);
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
  }, []);

  const toggleTheme = () => {
    const newDark = !dark;
    setDark(newDark);
    if (newDark) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  const isLocal = apiUrl.includes("localhost") || apiUrl.includes("127.0.0.1");

  return (
    <header className="h-14 border-b border-[var(--bd)] bg-[var(--bg1)] flex items-center justify-between px-6 flex-shrink-0 z-10 sticky top-0 shadow-sm transition-colors duration-200">
      <div className="font-semibold text-sm text-[var(--tx)]">
        Curriculum Dashboard
      </div>
      <div className="flex items-center gap-4">
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full text-[10px] font-medium transition-all ${
          isLocal ? "bg-amber-500/10 text-amber-500 border border-amber-500/20" : "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
        }`}>
          {isLocal ? <Link2Off size={12} /> : <Link2 size={12} />}
          <span className="max-w-[150px] truncate" title={apiUrl}>
            {isLocal ? "Local API" : "Production API"}: {apiUrl.replace(/^https?:\/\//, "")}
          </span>
        </div>
        <button 
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-[var(--bg2)] text-[var(--tx2)] transition-colors"
          title={dark ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
