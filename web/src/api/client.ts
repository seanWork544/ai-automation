import axios from "axios";
import { openDB } from "idb";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  withCredentials: false,
});

const QUEUE_STORE = "sync-queue";

async function enqueueRequest(config: any) {
  const db = await openDB("lifestack-sync", 1, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(QUEUE_STORE)) {
        db.createObjectStore(QUEUE_STORE, { autoIncrement: true });
      }
    },
  });
  await db.add(QUEUE_STORE, {
    url: config.url,
    method: config.method,
    data: config.data,
    headers: config.headers,
  });
  if ("serviceWorker" in navigator && "SyncManager" in window) {
    const registration = await navigator.serviceWorker.ready;
    await registration.sync.register("lifestack-queue");
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!error.response && error.config && navigator.onLine === false) {
      await enqueueRequest(error.config);
      return Promise.resolve({ data: error.config.data });
    }
    return Promise.reject(error);
  }
);

export interface Task {
  id: number;
  title: string;
  context: "work" | "personal" | "general";
  due_date?: string;
  status: "todo" | "doing" | "done";
  start_time?: string;
  end_time?: string;
}

export interface DailyLogEntry {
  id: number;
  date: string;
  summary: string;
}

export interface ProjectSummary {
  id: number;
  title: string;
  status: "active" | "paused" | "done";
  context: "work" | "personal";
}

export interface DashboardOverview {
  task_completion_percent: number;
  overdue_tasks: number;
  workout_totals: {
    sessions: number;
    sets: number;
    volume_by_exercise: Record<string, number>;
  };
  latest_prs: Array<Record<string, unknown>>;
  active_projects: Array<{ id: number; title: string; last_update: string | null }>;
  streaks: Record<string, number>;
}
