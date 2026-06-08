"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { projectsApi } from "@/lib/api";
import ReactMarkdown from "react-markdown";

export default function ProjectDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    projectsApi.get(id as string)
      .then(setProject)
      .catch(err => alert("Failed to load project"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Loading project details...</div>;
  if (!project) return <div>Project not found.</div>;

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4">
        <div>
          <h1>{project.name}</h1>
          <div className={`badge ${project.status === 'finalized' ? 'badge-success' : 'badge-warning'}`}>
            {project.status.toUpperCase()}
          </div>
        </div>
        <div className="flex gap-4">
          <button className="btn btn-outline" onClick={() => router.push('/projects')}>Back to List</button>
          <button className="btn btn-primary" onClick={() => router.push(`/projects/${id}/resourcing`)}>View Resourcing</button>
        </div>
      </header>

      <div className="card prd-content" style={{ background: '#fcfcfc' }}>
        {project.final_prd ? (
          <ReactMarkdown>{project.final_prd}</ReactMarkdown>
        ) : (
          <div style={{ padding: '2rem', textAlign: 'center' }}>
            <p className="text-muted">No PRD generated yet for this project.</p>
            <button className="btn btn-primary mt-4" onClick={() => router.push('/projects/new')}>Complete Kickoff</button>
          </div>
        )}
      </div>

      <style jsx>{`
        .prd-content :global(h1) { font-size: 1.5rem; margin-top: 1.5rem; }
        .prd-content :global(h2) { font-size: 1.25rem; margin-top: 1.25rem; }
        .prd-content :global(ul) { margin-left: 1.5rem; margin-bottom: 1rem; }
        .prd-content :global(p) { margin-bottom: 1rem; }
      `}</style>
    </div>
  );
}
