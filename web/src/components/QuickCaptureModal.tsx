import { Fragment, useState } from "react";
import { Dialog, Transition, Listbox } from "@headlessui/react";
import { apiClient } from "../api/client";

const captureTypes = [
  { id: "task", label: "Task" },
  { id: "log", label: "Daily Log" },
  { id: "set", label: "Workout Set" },
  { id: "project_update", label: "Project Update" },
];

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export function QuickCaptureModal({ open, onClose, onSuccess }: Props) {
  const [type, setType] = useState(captureTypes[0]);
  const [title, setTitle] = useState("");
  const [context, setContext] = useState("work");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload: Record<string, unknown> = { title };
      if (type.id === "task") {
        payload["context"] = context;
        payload["due_date"] = new Date().toISOString().split("T")[0];
      } else if (type.id === "log") {
        payload["date"] = new Date().toISOString().split("T")[0];
        payload["summary"] = notes || title;
      } else if (type.id === "project_update") {
        payload["note"] = notes || title;
        payload["progress_percent"] = 10;
        payload["date"] = new Date().toISOString().split("T")[0];
        payload["project_id"] = 1;
        payload["how_it_was_done"] = "Quick capture";
      } else {
        payload["workout_id"] = 1;
        payload["exercise_id"] = 1;
        payload["set_number"] = 1;
        payload["weight"] = 45;
        payload["reps"] = 5;
      }
      await apiClient.post("/quick-capture", {
        type: type.id,
        payload,
      });
      onSuccess?.();
      onClose();
      setTitle("");
      setNotes("");
    } catch (err) {
      setError("Capture failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Transition.Root show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 translate-y-4"
              enterTo="opacity-100 translate-y-0"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 translate-y-0"
              leaveTo="opacity-0 translate-y-4"
            >
              <Dialog.Panel className="w-full max-w-md rounded-xl bg-slate-900 p-6 shadow-xl">
                <Dialog.Title className="text-lg font-semibold text-white">Quick Capture</Dialog.Title>
                <div className="mt-4 space-y-4">
                  <div>
                    <label className="text-sm font-medium text-slate-300">Capture Type</label>
                    <Listbox value={type} onChange={setType}>
                      <div className="relative mt-1">
                        <Listbox.Button className="relative w-full cursor-pointer rounded-lg bg-slate-800 py-2 pl-3 pr-10 text-left text-white shadow-md focus:outline-none">
                          <span className="block truncate">{type.label}</span>
                        </Listbox.Button>
                        <Transition
                          as={Fragment}
                          leave="transition ease-in duration-100"
                          leaveFrom="opacity-100"
                          leaveTo="opacity-0"
                        >
                          <Listbox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-slate-800 py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
                            {captureTypes.map((option) => (
                              <Listbox.Option
                                key={option.id}
                                className={({ active }) =>
                                  `relative cursor-pointer select-none py-2 pl-3 pr-9 ${
                                    active ? "bg-indigo-600 text-white" : "text-slate-200"
                                  }`
                                }
                                value={option}
                              >
                                {({ selected }) => (
                                  <span className={`block truncate ${selected ? "font-medium" : "font-normal"}`}>
                                    {option.label}
                                  </span>
                                )}
                              </Listbox.Option>
                            ))}
                          </Listbox.Options>
                        </Transition>
                      </div>
                    </Listbox>
                  </div>

                  <div>
                    <label className="text-sm font-medium text-slate-300">Title</label>
                    <input
                      className="mt-1 w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                      placeholder="What needs to happen?"
                      value={title}
                      onChange={(event) => setTitle(event.target.value)}
                    />
                  </div>

                  {type.id === "task" && (
                    <div>
                      <label className="text-sm font-medium text-slate-300">Context</label>
                      <select
                        className="mt-1 w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                        value={context}
                        onChange={(event) => setContext(event.target.value)}
                      >
                        <option value="work">Work</option>
                        <option value="personal">Personal</option>
                        <option value="general">General</option>
                      </select>
                    </div>
                  )}

                  <div>
                    <label className="text-sm font-medium text-slate-300">Notes</label>
                    <textarea
                      className="mt-1 w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                      rows={3}
                      value={notes}
                      onChange={(event) => setNotes(event.target.value)}
                    />
                  </div>

                  {error && <p className="text-sm text-red-400">{error}</p>}
                </div>

                <div className="mt-6 flex items-center justify-end gap-2">
                  <button type="button" className="rounded-md px-4 py-2 text-sm text-slate-300" onClick={onClose}>
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={loading}
                    className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
                  >
                    {loading ? "Saving..." : "Save"}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
}
