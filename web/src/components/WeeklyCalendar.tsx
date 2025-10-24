import { useMemo } from "react";
import { useQuery } from "react-query";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
import { apiClient, Task } from "../api/client";
import { useIndexedDBCache } from "../hooks/useIndexedDBCache";

dayjs.extend(isoWeek);

const contexts: Record<Task["context"], string> = {
  work: "bg-blue-500/20 border-blue-500",
  personal: "bg-rose-500/20 border-rose-500",
  general: "bg-emerald-500/20 border-emerald-500",
};

export function WeeklyCalendar() {
  const [cachedTasks, setCachedTasks] = useIndexedDBCache<Task[]>("tasks", []);
  const { data } = useQuery("tasks", async () => {
    const response = await apiClient.get<Task[]>("/tasks");
    setCachedTasks(response.data);
    return response.data;
  });
  const tasks = data ?? cachedTasks;

  const startOfWeek = dayjs().isoWeekday(1);
  const days = Array.from({ length: 7 }, (_, idx) => startOfWeek.add(idx, "day"));
  const grouped = useMemo(() => {
    return days.map((day) => ({
      date: day,
      tasks: tasks.filter((task) => task.due_date && dayjs(task.due_date).isSame(day, "day")),
    }));
  }, [tasks, days]);

  return (
    <section className="rounded-2xl bg-slate-900/70 p-4 shadow-inner">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Weekly Calendar</h2>
        <p className="text-sm text-slate-400">Drag and drop coming soon</p>
      </div>
      <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-7">
        {grouped.map(({ date, tasks: dayTasks }) => (
          <div key={date.toString()} className="rounded-xl border border-slate-700/60 bg-slate-900/80 p-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-semibold text-white">{date.format("ddd")}</p>
              <span className="text-xs text-slate-400">{date.format("MMM D")}</span>
            </div>
            <div className="mt-2 space-y-2">
              {dayTasks.length === 0 && <p className="text-xs text-slate-500">No tasks yet.</p>}
              {dayTasks.map((task) => (
                <div
                  key={task.id}
                  className={`rounded-lg border px-3 py-2 text-sm text-white ${contexts[task.context]}`}
                >
                  <p className="font-medium">{task.title}</p>
                  <p className="text-xs text-slate-300">{task.status}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
