import { useQuery } from "react-query";
import dayjs from "dayjs";
import { apiClient, DailyLogEntry } from "../api/client";
import { useIndexedDBCache } from "../hooks/useIndexedDBCache";

export function DailyLogPanel() {
  const [cachedLogs, setCachedLogs] = useIndexedDBCache<DailyLogEntry[]>("daily_logs", []);
  const { data } = useQuery("daily_logs", async () => {
    const response = await apiClient.get<DailyLogEntry[]>("/daily-logs");
    setCachedLogs(response.data);
    return response.data;
  });
  const logs = data ?? cachedLogs;

  const today = dayjs().format("YYYY-MM-DD");
  const todayLogs = logs.filter((log) => log.date === today);

  return (
    <section className="rounded-2xl bg-slate-900/70 p-4 shadow-inner">
      <h2 className="text-lg font-semibold text-white">Daily Log</h2>
      <div className="mt-4 space-y-3">
        <div className="rounded-xl border border-slate-700/60 bg-slate-900/80 p-3">
          <h3 className="text-sm font-semibold text-white">Today</h3>
          <p className="mt-2 text-sm text-slate-300">What are you doing today?</p>
          <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
            <textarea className="h-24 rounded-md bg-slate-800 p-3 text-sm text-white" placeholder="Work notes" />
            <textarea className="h-24 rounded-md bg-slate-800 p-3 text-sm text-white" placeholder="Personal notes" />
          </div>
        </div>
        <div className="space-y-2">
          {todayLogs.length === 0 && <p className="text-sm text-slate-500">No entries yet.</p>}
          {todayLogs.map((entry) => (
            <div key={entry.id} className="rounded-xl border border-slate-700/60 bg-slate-900/80 p-3">
              <p className="text-sm text-slate-200">{entry.summary}</p>
              <button className="mt-2 text-xs font-medium text-indigo-400">Convert to task</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
