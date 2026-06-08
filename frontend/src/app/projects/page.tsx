"use client";

import { useEffect, useState } from "react";
import { projectsApi } from "@/lib/api";
import Link from "next/link";

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.list().then(setProjects).finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4">
        <h1>Projects</h1>
        <Link href="/projects/new" className="btn btn-primary">New Project</Link>
      </header>

      <div className="flex-col gap-4">
        {loading ? (
          <p>Loading projects...</p>
        ) : projects.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p className="text-muted">No projects found.</p>
          </div>
        ) : (
          projects.map((p) => (
            <div key={p.id} className="card flex justify-between items-center">
              <div>
                <h3>{p.name}</h3>
                <p className="text-muted">Status: {p.status.toUpperCase()}</p>
              </div>
              <div className="flex gap-4">
                <Link href={`/projects/${p.id}/resourcing`} className="btn btn-outline">
                  Resourcing
                </Link>
                <Link href={`/projects/${p.id}`} className="btn btn-primary">
                  View PRD
                </Link>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
