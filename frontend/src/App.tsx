import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
};

export default function App() {
  const [health, setHealth] = useState<string>("…");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/health/")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json() as Promise<HealthResponse>;
      })
      .then((data) => setHealth(data.status))
      .catch((err: unknown) => {
        const message = err instanceof Error ? err.message : "unknown error";
        setError(message);
      });
  }, []);

  return (
    <main className="app">
      <h1>OB2 — платформа платного контента</h1>
      <p>Итерация 1: каркас SPA + API через nginx.</p>
      <section className="card">
        <h2>Health check</h2>
        {error ? (
          <p className="error">API недоступен: {error}</p>
        ) : (
          <p>
            <code>/api/health/</code> → <strong>{health}</strong>
          </p>
        )}
      </section>
    </main>
  );
}
