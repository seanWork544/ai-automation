import { useQuery } from "react-query";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import { apiClient, DashboardOverview } from "../api/client";
import { useIndexedDBCache } from "../hooks/useIndexedDBCache";

dayjs.extend(isoWeek);

export function DashboardCards() {
  const week = dayjs().format("GGGG-" + dayjs().isoWeek().toString().padStart(2, "0"));
  const [cached, setCached] = useIndexedDBCache<DashboardOverview | null>("dashboard", null);
  const { data } = useQuery(["dashboard", week], async () => {
    const response = await apiClient.get<DashboardOverview>(`/dashboard/overview?week=${week}`);
    setCached(response.data);
    return response.data;
  });
  const overview = data ?? cached;

  if (!overview) {
    return (
      <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {[1, 2, 3, 4].map((idx) => (
          <div key={idx} className="h-32 animate-pulse rounded-2xl bg-slate-900/70" />
        ))}
      </section>
    );
  }

  return (
    <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
      <Card title="Task completion" value={`${overview.task_completion_percent}%`} subtitle={`${overview.overdue_tasks} overdue`} />
      <Card title="Streaks" value={`${overview.streaks.daily_log} daily logs`} subtitle={`${overview.streaks.workout} workouts`} />
      <Card title="Workouts" value={`${overview.workout_totals.sessions} sessions`} subtitle={`${overview.workout_totals.sets} sets`} />
      <Card title="Active projects" value={`${overview.active_projects.length}`} subtitle="Needing updates" />
    </section>
  );
}

function Card({ title, value, subtitle }: { title: string; value: string; subtitle: string }) {
  return (
    <article className="rounded-2xl border border-slate-700/60 bg-slate-900/80 p-4">
      <p className="text-xs uppercase tracking-wide text-slate-400">{title}</p>
      <p className="mt-3 text-2xl font-semibold text-white">{value}</p>
      <p className="mt-1 text-sm text-slate-400">{subtitle}</p>
    </article>
  );
}
