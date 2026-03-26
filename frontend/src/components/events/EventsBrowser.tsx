"use client";

import { useState, useEffect } from "react";
import { Search, Filter, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

import type { Event } from "@/lib/types";
import { API_URL } from "@/lib/config";

export function EventsBrowser() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    async function fetchEvents() {
      try {
        const res = await fetch(`${API_URL}/api/events`);
        const data = await res.json();
        setEvents(data);
      } catch (e) {
        console.error("Failed to fetch events", e);
      } finally {
        setLoading(false);
      }
    }
    fetchEvents();
  }, []);

  const filteredEvents = events.filter((e) =>
    e.event_name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    e.knowledge_domain_1?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Search & Filters */}
      <div className="flex gap-4 items-center bg-[var(--bg2)] p-4 rounded-lg border border-[var(--bd)]">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--tx3)]" />
          <input
            type="text"
            placeholder="Search events by name, domain, or skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[var(--bg3)] border border-[var(--bd)] text-[var(--tx)] text-sm rounded-md pl-10 pr-4 py-2 focus:outline-none focus:border-[var(--acc)]"
          />
        </div>
        <Button variant="outline" className="flex items-center gap-2">
          <Filter size={16} /> Filters
        </Button>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="text-[var(--tx2)] animate-pulse">Loading events...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredEvents.map((ev) => (
            <div
              key={ev.id}
              className="bg-[var(--bg2)] border border-[var(--bd)] rounded-xl overflow-hidden hover:border-[var(--bd2)] transition-colors flex flex-col"
            >
              <div className="p-5 flex-1">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs font-medium px-2 py-1 rounded bg-[rgba(99,102,241,0.1)] text-[var(--acc2)] border border-[rgba(99,102,241,0.2)]">
                    {ev.event_type || "Event"}
                  </span>
                  <div className="flex items-center gap-1 text-[var(--tx3)] text-xs">
                    <Calendar size={14} />
                    <span>2024</span>
                  </div>
                </div>
                <h3 className="font-semibold text-[var(--tx)] text-sm leading-tight mb-2 line-clamp-2">
                  {ev.event_name}
                </h3>
                <p className="text-xs text-[var(--tx2)] line-clamp-2 mb-4">
                  {ev.organizing_body}
                </p>

                <div className="space-y-2 mt-auto">
                  {ev.knowledge_domain_1 && (
                    <div className="text-xs text-[var(--tx2)] truncate">
                      <span className="text-[var(--tx3)]">Domain:</span> {ev.knowledge_domain_1}
                    </div>
                  )}
                  {ev.mode && (
                    <div className="text-xs text-[var(--tx2)] truncate">
                      <span className="text-[var(--tx3)]">Mode:</span> {ev.mode}
                    </div>
                  )}
                  {ev.skills_addressed && ev.skills_addressed.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1">
                      {ev.skills_addressed.slice(0, 3).map((s, idx) => (
                        <span key={idx} className="text-[10px] bg-[var(--bg3)] text-[var(--tx2)] px-1.5 py-0.5 rounded border border-[var(--bd)] truncate max-w-full">
                          {s.knowledge_set}
                        </span>
                      ))}
                      {ev.skills_addressed.length > 3 && (
                        <span className="text-[10px] text-[var(--tx3)] px-1">
                          +{ev.skills_addressed.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <div className="border-t border-[var(--bd)] p-3 bg-[var(--bg1)]">
                <Link href={`/events/${ev.id}`} className="w-full">
                  <Button className="w-full text-xs py-1 h-8" variant="default">
                    View & Configure Assessment
                  </Button>
                </Link>
              </div>
            </div>
          ))}
          
          {filteredEvents.length === 0 && (
            <div className="col-span-full py-12 text-center text-[var(--tx3)]">
              No events found. Try adjusting your search.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
