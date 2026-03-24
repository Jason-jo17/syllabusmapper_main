"use client";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function NavBar() {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const isDark = document.documentElement.classList.contains("dark");
    setDark(isDark);
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

  return (
    <header className="h-14 border-b border-[var(--bd)] bg-[var(--bg1)] flex items-center justify-between px-6 flex-shrink-0 z-10 sticky top-0 shadow-sm transition-colors duration-200">
      <div className="font-semibold text-sm text-[var(--tx)]">
        Curriculum Dashboard
      </div>
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-[var(--bg2)] text-[var(--tx2)] transition-colors"
          title={dark ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {dark ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <div className="text-[var(--tx2)] text-xs">Connected to Local Database</div>
      </div>
    </header>
  );
}
