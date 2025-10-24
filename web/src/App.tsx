import { useEffect, useMemo, useRef, useState } from "react";
import { MagnifyingGlassIcon, PlusIcon, SunIcon, MoonIcon } from "@heroicons/react/24/outline";
import { useQuery, useQueryClient } from "react-query";
import dayjs from "dayjs";
import { apiClient } from "./api/client";
import { DashboardCards } from "./components/DashboardCards";
import { DailyLogPanel } from "./components/DailyLogPanel";
import { GymTracker } from "./components/GymTracker";
import { ProjectsPanel } from "./components/ProjectsPanel";
import { QuickCaptureModal } from "./components/QuickCaptureModal";
import { WeeklyCalendar } from "./components/WeeklyCalendar";

interface SearchFilters {
  context: string;
  status: string;
}

export default function App() {
  const queryClient = useQueryClient();
  const [isCaptureOpen, setCaptureOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({ context: "", status: "" });
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const searchInputRef = useRef<HTMLInputElement | null>(null);

  const { data: searchResults } = useQuery<Record<string, unknown[]> | null>(
    ["search", searchTerm, filters],
    async () => {
      if (searchTerm.trim().length < 2) return null;
      const params = new URLSearchParams({ q: searchTerm });
      if (filters.context) params.set("context", filters.context);
      if (filters.status) params.set("status_filter", filters.status);
      const response = await apiClient.get("/search", { params });
      return response.data as Record<string, unknown[]>;
    },
    { keepPreviousData: true, enabled: searchTerm.trim().length >= 2 }
  );

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (event.key === "q" && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        setCaptureOpen(true);
      }
      if (event.key === "/") {
        event.preventDefault();
        searchInputRef.current?.focus();
      }
      if (event.key === "n") {
        event.preventDefault();
        setCaptureOpen(true);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("light", "dark");
    root.classList.add(theme);
  }, [theme]);

  const toggleTheme = () => setTheme((prev) => (prev === "dark" ? "light" : "dark"));

  const searchSummary = useMemo(() => {
    if (!searchResults) return "";
    const counts = Object.values(searchResults).reduce((acc, arr) => acc + arr.length, 0);
    return `${counts} results`;
  }, [searchResults]);

  return (
    <div className="min-h-screen bg-slate-950 pb-24 text-slate-100">
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-full bg-indigo-600/10 p-2 text-indigo-400">
              <PlusIcon className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-white">LifeStack</h1>
              <p className="text-xs text-slate-400">Calendar, training, logs, and projects aligned in one stack.</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <label className="text-xs uppercase tracking-wide text-slate-400">Context</label>
              <select
                className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white"
                value={filters.context}
                onChange={(event) => setFilters((prev) => ({ ...prev, context: event.target.value }))}
              >
                <option value="">All</option>
                <option value="work">Work</option>
                <option value="personal">Personal</option>
                <option value="general">General</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs uppercase tracking-wide text-slate-400">Status</label>
              <select
                className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-xs text-white"
                value={filters.status}
                onChange={(event) => setFilters((prev) => ({ ...prev, status: event.target.value }))}
              >
                <option value="">Any</option>
                <option value="todo">Todo</option>
                <option value="doing">Doing</option>
                <option value="done">Done</option>
              </select>
            </div>
            <button
              onClick={toggleTheme}
              className="rounded-full border border-slate-700 bg-slate-900 p-2 text-slate-300 hover:text-white"
            >
              {theme === "dark" ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
            </button>
          </div>
        </div>
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 pb-4">
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-3 h-5 w-5 text-slate-500" />
            <input
              ref={searchInputRef}
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search tasks, logs, projects... (/ to focus)"
              className="w-full rounded-xl border border-slate-700 bg-slate-900 py-2 pl-10 pr-4 text-sm text-white"
            />
            {searchSummary && <p className="mt-1 text-xs text-slate-500">{searchSummary}</p>}
          </div>
          <button
            onClick={() => setCaptureOpen(true)}
            className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-600/40"
          >
            <PlusIcon className="h-5 w-5" /> Quick Capture
          </button>
        </div>
      </header>

      <main className="mx-auto mt-6 flex max-w-6xl flex-col gap-6 px-4">
        <DashboardCards />
        <WeeklyCalendar />
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <DailyLogPanel />
          <GymTracker />
        </div>
        <ProjectsPanel />
        {searchResults && searchTerm.length >= 2 && (
          <section className="rounded-2xl border border-slate-700/60 bg-slate-900/80 p-4">
            <h2 className="text-lg font-semibold text-white">Search results</h2>
            <pre className="mt-3 max-h-64 overflow-auto rounded-lg bg-slate-950/60 p-3 text-xs text-slate-300">
              {JSON.stringify(searchResults, null, 2)}
            </pre>
          </section>
        )}
      </main>

      <button
        onClick={() => setCaptureOpen(true)}
        className="fixed bottom-6 right-6 flex items-center gap-2 rounded-full bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-2xl shadow-indigo-600/60"
      >
        <PlusIcon className="h-5 w-5" />
        Quick Capture
      </button>

      <QuickCaptureModal
        open={isCaptureOpen}
        onClose={() => setCaptureOpen(false)}
        onSuccess={() => {
          queryClient.invalidateQueries();
        }}
      />
    </div>
  );
}
