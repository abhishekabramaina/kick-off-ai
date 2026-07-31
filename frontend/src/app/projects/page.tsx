"use client";

import { useEffect, useState } from "react";
import { projectsApi } from "@/lib/api";
import Link from "next/link";
import { 
  IconUsers, 
  IconFileText, 
  IconArchive, 
  IconRestore, 
  IconTrash, 
  IconPlus,
  IconCalendar
} from "@/components/Icons";

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"active" | "archived">("active");

  const loadProjects = () => {
    setLoading(true);
    projectsApi.list()
      .then(setProjects)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const handleArchive = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to archive "${name}"?`)) return;
    try {
      await projectsApi.archive(id);
      loadProjects();
    } catch (err: any) {
      alert(err.message || "Failed to archive project");
    }
  };

  const handleUnarchive = async (id: string, name: string) => {
    try {
      await projectsApi.unarchive(id);
      loadProjects();
    } catch (err: any) {
      alert(err.message || "Failed to restore project");
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to PERMANENTLY delete "${name}"?\nThis will remove all associated roles and matches.`)) return;
    try {
      await projectsApi.delete(id);
      loadProjects();
    } catch (err: any) {
      alert(err.message || "Failed to delete project");
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "";
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    } catch {
      return dateStr;
    }
  };

  const filteredProjects = projects.filter(p => 
    activeTab === "archived" ? p.status === "archived" : p.status !== "archived"
  );

  const activeCount = projects.filter(p => p.status !== "archived").length;
  const archivedCount = projects.filter(p => p.status === "archived").length;

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4">
        <div>
          <h1>Projects</h1>
          <p className="text-muted">Manage active and archived project kickoffs.</p>
        </div>
        <Link href="/projects/new" className="btn btn-primary flex items-center gap-4">
          <IconPlus size={18} />
          <span>New Project</span>
        </Link>
      </header>

      {/* Tabs */}
      <div className="flex gap-4 mb-4" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
        <button 
          className={`btn ${activeTab === 'active' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('active')}
        >
          Active ({activeCount})
        </button>
        <button 
          className={`btn ${activeTab === 'archived' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('archived')}
        >
          Archived ({archivedCount})
        </button>
      </div>

      <div className="flex-col gap-4">
        {loading ? (
          <p>Loading projects...</p>
        ) : filteredProjects.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p className="text-muted">
              {activeTab === 'active' ? 'No active projects found.' : 'No archived projects.'}
            </p>
          </div>
        ) : (
          filteredProjects.map((p) => {
            const roleCount = p.roles ? p.roles.length : 0;

            return (
              <div key={p.id} className="card flex justify-between items-center">
                <div>
                  <div className="flex items-center gap-4">
                    <h3>{p.name}</h3>
                    <span className={`badge ${
                      p.status === 'finalized' ? 'badge-success' : 
                      p.status === 'archived' ? 'badge-archived' : 'badge-warning'
                    }`}>
                      {p.status.toUpperCase()}
                    </span>
                  </div>

                  {/* Clean & Minimal Metadata Line (Zero Drama) */}
                  <div className="flex items-center gap-4 text-muted flex-wrap" style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
                    <span>ID: #{p.id}</span>
                    {p.created_at && (
                      <>
                        <span style={{ opacity: 0.4 }}>•</span>
                        <span className="flex items-center gap-4">
                          <IconCalendar size={13} />
                          {formatDate(p.created_at)}
                        </span>
                      </>
                    )}
                    <span style={{ opacity: 0.4 }}>•</span>
                    <span className="flex items-center gap-4">
                      <IconUsers size={13} />
                      {roleCount} {roleCount === 1 ? 'Role' : 'Roles'}
                    </span>
                  </div>
                </div>

                {/* Microsoft Fluent Pipe-Separated Icon Toolbar */}
                <div className="toolbar-group">
                  {activeTab === 'active' ? (
                    <>
                      <div className="tooltip-wrapper">
                        <Link 
                          href={`/projects/${p.id}/resourcing`} 
                          className="toolbar-icon-btn toolbar-icon-btn-primary"
                          aria-label="Resourcing"
                        >
                          <IconUsers size={18} />
                        </Link>
                        <span className="fluent-tooltip">Resourcing</span>
                      </div>

                      <div className="tooltip-wrapper">
                        <Link 
                          href={`/projects/${p.id}`} 
                          className="toolbar-icon-btn toolbar-icon-btn-primary"
                          aria-label="View PRD"
                        >
                          <IconFileText size={18} />
                        </Link>
                        <span className="fluent-tooltip">View PRD</span>
                      </div>

                      <div className="pipe-divider" />

                      <div className="tooltip-wrapper">
                        <button 
                          className="toolbar-icon-btn toolbar-icon-btn-archive"
                          onClick={() => handleArchive(p.id, p.name)}
                          aria-label="Archive Project"
                        >
                          <IconArchive size={18} />
                        </button>
                        <span className="fluent-tooltip">Archive Project</span>
                      </div>
                    </>
                  ) : (
                    <div className="tooltip-wrapper">
                      <button 
                        className="toolbar-icon-btn toolbar-icon-btn-success"
                        onClick={() => handleUnarchive(p.id, p.name)}
                        aria-label="Restore Project"
                      >
                        <IconRestore size={18} />
                      </button>
                      <span className="fluent-tooltip">Restore Project</span>
                    </div>
                  )}

                  <div className="pipe-divider" />

                  <div className="tooltip-wrapper">
                    <button 
                      className="toolbar-icon-btn toolbar-icon-btn-danger"
                      onClick={() => handleDelete(p.id, p.name)}
                      aria-label="Delete Project"
                    >
                      <IconTrash size={18} />
                    </button>
                    <span className="fluent-tooltip">Delete Project</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
