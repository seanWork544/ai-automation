import { useMemo, useState } from "react";
import { useQuery } from "react-query";
import { apiClient, ProjectSummary } from "../api/client";
import { useIndexedDBCache } from "../hooks/useIndexedDBCache";

interface ProjectUpdate {
  id: number;
  project_id: number;
  note: string;
  progress_percent: number;
  how_it_was_done?: string;
  date: string;
}

export function ProjectsPanel() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [cachedProjects, setCachedProjects] = useIndexedDBCache<ProjectSummary[]>("projects", []);
  const [cachedUpdates, setCachedUpdates] = useIndexedDBCache<ProjectUpdate[]>("project_updates", []);

  const { data: projects } = useQuery("projects", async () => {
    const response = await apiClient.get<ProjectSummary[]>("/projects");
    setCachedProjects(response.data);
    return response.data;
  });

  const { data: updates } = useQuery("project_updates", async () => {
    const response = await apiClient.get<ProjectUpdate[]>("/project-updates");
    setCachedUpdates(response.data);
    return response.data;
  });

  const projectList = projects ?? cachedProjects;
  const projectUpdates = updates ?? cachedUpdates;

  const filtered = useMemo(() => {
    if (statusFilter === "all") return projectList;
    return projectList.filter((project) => project.status === statusFilter);
  }, [projectList, statusFilter]);

  const latestUpdate = (projectId: number) =>
    projectUpdates
      .filter((update) => update.project_id === projectId)
      .sort((a, b) => b.date.localeCompare(a.date))[0];

  return (
    <section className="rounded-2xl bg-slate-900/70 p-4 shadow-inner">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Projects</h2>
        <select
          className="rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
        >
          <option value="all">All</option>
          <option value="active">Active</option>
          <option value="paused">Paused</option>
          <option value="done">Done</option>
        </select>
      </div>
      <div className="mt-4 space-y-3">
        {filtered.map((project) => {
          const update = latestUpdate(project.id);
          return (
            <article
              key={project.id}
              className="rounded-xl border border-slate-700/60 bg-slate-900/80 p-4 text-sm text-slate-200"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-base font-semibold text-white">{project.title}</h3>
                <span className="rounded-full bg-slate-800 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
                  {project.status}
                </span>
              </div>
              {update ? (
                <div className="mt-3 space-y-1">
                  <p className="text-xs text-slate-400">Last update: {update.date}</p>
                  <p className="font-medium">{update.note}</p>
                  <p className="text-xs text-slate-300">How: {update.how_it_was_done}</p>
                  <div className="mt-2 h-2 w-full rounded-full bg-slate-800">
                    <div className="h-2 rounded-full bg-emerald-500" style={{ width: `${update.progress_percent}%` }} />
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-xs text-slate-400">No updates yet.</p>
              )}
            </article>
          );
        })}
        {filtered.length === 0 && <p className="text-sm text-slate-500">No projects in this state.</p>}
      </div>
    </section>
  );
}
