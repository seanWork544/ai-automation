import { useEffect, useState } from "react";
import { openDB } from "idb";

const DB_NAME = "lifestack-cache";
const STORE_NAME = "entities";

export function useIndexedDBCache<T>(key: string, fallback: T) {
  const [value, setValue] = useState<T>(fallback);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const db = await openDB(DB_NAME, 1, {
        upgrade(db) {
          if (!db.objectStoreNames.contains(STORE_NAME)) {
            db.createObjectStore(STORE_NAME);
          }
        },
      });
      const cached = await db.get(STORE_NAME, key);
      if (!cancelled && cached) {
        setValue(cached as T);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [key]);

  const persist = async (next: T) => {
    setValue(next);
    const db = await openDB(DB_NAME, 1, {
      upgrade(db) {
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME);
        }
      },
    });
    await db.put(STORE_NAME, next, key);
  };

  return [value, persist] as const;
}
