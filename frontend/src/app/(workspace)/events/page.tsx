import { EventsBrowser } from "@/components/events/EventsBrowser";

export default function EventsPage() {
  return (
    <div className="p-8 pb-32 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[var(--tx)] mb-2">Events Browser</h1>
        <p className="text-[var(--tx2)]">Explore Hackathons, Internships, and Competitions to boost your profile.</p>
      </div>
      <EventsBrowser />
    </div>
  );
}
