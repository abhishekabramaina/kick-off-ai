"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { projectsApi, employeesApi } from "@/lib/api";

export default function Home() {
  const [projects, setProjects] = useState<any[]>([]);
  const [benchCount, setBenchCount] = useState(0);

  useEffect(() => {
    projectsApi.list().then(data => setProjects(data.slice(0, 3)));
    employeesApi.bench().then(data => setBenchCount(data.length));
  }, []);

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4">
        <div>
          <h1>Welcome back</h1>
          <p className="text-muted">Streamline your project kickoff with AI.</p>
        </div>
        <Link href="/projects/new" className="btn btn-primary">
          Start New Project
        </Link>
      </header>

      <div className="flex gap-4 mb-4">
        <div className="card" style={{ flex: 1 }}>
          <h3>Projects</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700 }}>{projects.length}</p>
          <p className="text-muted">Recent projects</p>
        </div>
        <div className="card" style={{ flex: 1 }}>
          <h3>Bench</h3>
          <p style={{ fontSize: '2rem', fontWeight: 700 }}>{benchCount}</p>
          <p className="text-muted">Available employees</p>
        </div>
      </div>

      <section>
        <div className="flex justify-between items-center mb-4">
          <h2>Recent Projects</h2>
          <Link href="/projects" className="btn btn-outline">View All</Link>
        </div>
        {projects.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p className="text-muted">No projects found. Start by creating a new one!</p>
            <Link href="/projects/new" className="btn btn-primary mt-4">Create Project</Link>
          </div>
        ) : (
          <div className="flex-col gap-4">
            {projects.map(p => (
              <div key={p.id} className="card flex justify-between items-center">
                <h3>{p.name}</h3>
                <Link href={`/projects/${p.id}`} className="btn btn-outline">View Details</Link>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
