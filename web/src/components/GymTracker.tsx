import { useMemo, useState } from "react";
import { useQuery } from "react-query";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import dayjs from "dayjs";
import { apiClient } from "../api/client";
import { useIndexedDBCache } from "../hooks/useIndexedDBCache";

interface WorkoutSet {
  id: number;
  workout_id: number;
  exercise_id: number;
  set_number: number;
  weight: number;
  reps: number;
}

interface Exercise {
  id: number;
  name: string;
}

export function GymTracker() {
  const [selectedExercise, setSelectedExercise] = useState<number | null>(null);
  const [cachedSets, setCachedSets] = useIndexedDBCache<WorkoutSet[]>("workout_sets", []);
  const [cachedExercises, setCachedExercises] = useIndexedDBCache<Exercise[]>("exercises", []);

  const { data: exercises } = useQuery("exercises", async () => {
    const response = await apiClient.get<Exercise[]>("/exercises");
    setCachedExercises(response.data);
    return response.data;
  });

  const { data: workoutSets } = useQuery("workout_sets", async () => {
    const response = await apiClient.get<WorkoutSet[]>("/workout-sets");
    setCachedSets(response.data);
    return response.data;
  });

  const exerciseList = exercises ?? cachedExercises;
  const sets = workoutSets ?? cachedSets;

  const filteredSets = useMemo(() => {
    if (!selectedExercise) return sets;
    return sets.filter((set) => set.exercise_id === selectedExercise);
  }, [selectedExercise, sets]);

  const chartData = useMemo(() => {
    const grouped = new Map<number, { weight: number; date: string }>();
    filteredSets.forEach((set) => {
      const key = set.exercise_id;
      const current = grouped.get(key);
      const latest = {
        weight: current ? Math.max(current.weight, set.weight) : set.weight,
        date: dayjs().format("MMM D"),
      };
      grouped.set(key, latest);
    });
    return Array.from(grouped.entries()).map(([exerciseId, info]) => ({
      exercise: exerciseList.find((ex) => ex.id === exerciseId)?.name ?? `Exercise ${exerciseId}`,
      weight: info.weight,
    }));
  }, [filteredSets, exerciseList]);

  return (
    <section className="rounded-2xl bg-slate-900/70 p-4 shadow-inner">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Gym Progress</h2>
        <select
          className="rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white"
          value={selectedExercise ?? ""}
          onChange={(event) => setSelectedExercise(event.target.value ? Number(event.target.value) : null)}
        >
          <option value="">All exercises</option>
          {exerciseList.map((exercise) => (
            <option key={exercise.id} value={exercise.id}>
              {exercise.name}
            </option>
          ))}
        </select>
      </div>
      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-slate-200">Recent Sets</h3>
          <div className="max-h-60 space-y-2 overflow-y-auto pr-1">
            {filteredSets.map((set) => (
              <div key={set.id} className="rounded-lg border border-slate-700/60 bg-slate-900/80 p-3 text-sm text-slate-200">
                <p className="font-medium">
                  {exerciseList.find((ex) => ex.id === set.exercise_id)?.name ?? "Exercise"}
                </p>
                <p className="text-xs text-slate-400">
                  Set {set.set_number}: {set.weight} kg × {set.reps} reps
                </p>
              </div>
            ))}
            {filteredSets.length === 0 && <p className="text-sm text-slate-500">No sets yet.</p>}
          </div>
        </div>
        <div className="h-56 rounded-xl border border-slate-700/60 bg-slate-900/80 p-3">
          <h3 className="text-sm font-semibold text-slate-200">Top Set Weight</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="exercise" stroke="#cbd5f5" tick={{ fill: "#cbd5f5", fontSize: 12 }} />
              <YAxis stroke="#cbd5f5" tick={{ fill: "#cbd5f5", fontSize: 12 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0f172a", borderColor: "#1e293b", color: "#e2e8f0" }}
                cursor={{ fill: "#334155" }}
              />
              <Bar dataKey="weight" fill="#6366f1" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
