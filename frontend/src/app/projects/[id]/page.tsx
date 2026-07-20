"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { projectsApi } from "@/lib/api";
import ReactMarkdown from "react-markdown";
import { 
  IconUsers, 
  IconArchive, 
  IconRestore, 
  IconTrash, 
  IconArrowLeft 
} from "@/components/Icons";

export default function ProjectDetail() {
  const { id } = useParams();
  const router = useRouter();
  const [project, setProject] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const loadProject = () => {
    projectsApi.get(id as string)
      .then(setProject)
      .catch(() => alert("Failed to load project"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProject();
  }, [id]);

  const handleArchiveToggle = async () => {
    if (!project) return;
    const isArchived = project.status === "archived";
    const actionText = isArchived ? "restore" : "archive";
    if (!isArchived && !confirm(`Are you sure you want to archive "${project.name}"?`)) return;

    try {
      if (isArchived) {
        await projectsApi.unarchive(id as string);
      } else {
        await projectsApi.archive(id as string);
      }
      loadProject();
    } catch (err: any) {
      alert(err.message || `Failed to ${actionText} project`);
    }
  };

  const handleDelete = async () => {
    if (!project) return;
    if (!confirm(`Are you sure you want to PERMANENTLY delete "${project.name}"?\nThis will remove all associated roles and candidate matches.`)) return;
    try {
      await projectsApi.delete(id as string);
      router.push('/projects');
    } catch (err: any) {
      alert(err.message || "Failed to delete project");
    }
  };

  if (loading) return <div>Loading project details...</div>;
  if (!project) return <div>Project not found.</div>;

  const isArchived = project.status === "archived";

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4 flex-wrap gap-4">
        <div>
          <div className="flex items-center gap-4">
            <h1>{project.name}</h1>
            <div className={`badge ${
              project.status === 'finalized' ? 'badge-success' : 
              project.status === 'archived' ? 'badge-archived' : 'badge-warning'
            }`}>
              {project.status.toUpperCase()}
            </div>
          </div>
        </div>

        {/* Microsoft Fluent Pipe-Separated Icon Toolbar */}
        <div className="toolbar-group">
          <div className="tooltip-wrapper">
            <button 
              className="toolbar-icon-btn toolbar-icon-btn-outline" 
              onClick={() => router.push('/projects')}
              aria-label="Back to List"
            >
              <IconArrowLeft size={18} />
            </button>
            <span className="fluent-tooltip">Back to List</span>
          </div>

          <div className="pipe-divider" />

          <div className="tooltip-wrapper">
            <button 
              className="toolbar-icon-btn toolbar-icon-btn-primary" 
              onClick={() => router.push(`/projects/${id}/resourcing`)}
              aria-label="View Resourcing"
            >
              <IconUsers size={18} />
            </button>
            <span className="fluent-tooltip">Resourcing</span>
          </div>

          <div className="pipe-divider" />

          <div className="tooltip-wrapper">
            <button 
              className={`toolbar-icon-btn ${isArchived ? 'toolbar-icon-btn-success' : 'toolbar-icon-btn-archive'}`}
              onClick={handleArchiveToggle}
              aria-label={isArchived ? 'Restore Project' : 'Archive Project'}
            >
              {isArchived ? <IconRestore size={18} /> : <IconArchive size={18} />}
            </button>
            <span className="fluent-tooltip">{isArchived ? 'Restore Project' : 'Archive Project'}</span>
          </div>

          <div className="pipe-divider" />

          <div className="tooltip-wrapper">
            <button 
              className="toolbar-icon-btn toolbar-icon-btn-danger" 
              onClick={handleDelete}
              aria-label="Delete Project"
            >
              <IconTrash size={18} />
            </button>
            <span className="fluent-tooltip">Delete Project</span>
          </div>
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
