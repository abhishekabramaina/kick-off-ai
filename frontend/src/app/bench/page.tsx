"use client";

import { useEffect, useState } from "react";
import { employeesApi } from "@/lib/api";
import { 
  IconPlus, 
  IconSearch, 
  IconCheck, 
  IconPause, 
  IconArchive, 
  IconRestore, 
  IconEdit, 
  IconUsers 
} from "@/components/Icons";

export default function Bench() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"on_bench" | "assigned" | "suspended" | "archived" | "all">("on_bench");
  const [searchQuery, setSearchQuery] = useState("");

  // Collapsible summary states
  const [expandedIds, setExpandedIds] = useState<Record<number, boolean>>({});

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedEmp, setSelectedEmp] = useState<any>(null);

  // Form states
  const [name, setName] = useState("");
  const [resumeText, setResumeText] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadEmployees = () => {
    setLoading(true);
    employeesApi.list()
      .then(setEmployees)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const toggleExpand = (id: number) => {
    setExpandedIds(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleStatusChange = async (id: number | string, newStatus: string) => {
    try {
      await employeesApi.updateStatus(id, newStatus);
      loadEmployees();
    } catch (err: any) {
      alert(err.message || "Failed to update status");
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !resumeText.trim()) {
      alert("Please enter candidate name and resume details.");
      return;
    }
    setSubmitting(true);
    try {
      await employeesApi.create({ name, resume_text: resumeText, is_on_bench: true, status: "on_bench" });
      setName("");
      setResumeText("");
      setShowAddModal(false);
      loadEmployees();
    } catch (err: any) {
      alert(err.message || "Failed to create talent profile");
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEmp) return;
    setSubmitting(true);
    try {
      await employeesApi.updateProfile(selectedEmp.id, { name, resume_text: resumeText });
      setShowEditModal(false);
      setSelectedEmp(null);
      loadEmployees();
    } catch (err: any) {
      alert(err.message || "Failed to update profile");
    } finally {
      setSubmitting(false);
    }
  };

  const openEdit = (emp: any) => {
    setSelectedEmp(emp);
    setName(emp.name);
    setResumeText(emp.resume_text || "");
    setShowEditModal(true);
  };

  // Filter candidates
  const filteredEmployees = employees.filter((emp) => {
    const statusMatch = activeTab === "all" ? true : (emp.status || (emp.is_on_bench ? "on_bench" : "assigned")) === activeTab;
    const searchMatch = !searchQuery.trim() || 
      emp.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (emp.resume_text && emp.resume_text.toLowerCase().includes(searchQuery.toLowerCase()));
    return statusMatch && searchMatch;
  });

  const getStatusBadge = (status: string, isOnBench: boolean) => {
    const st = status || (isOnBench ? "on_bench" : "assigned");
    switch (st) {
      case "on_bench":
        return <span className="badge badge-bench">AVAILABLE (BENCH)</span>;
      case "assigned":
        return <span className="badge badge-assigned">DEPLOYED (PROJECT)</span>;
      case "suspended":
        return <span className="badge badge-suspended">ON HOLD (SUSPENDED)</span>;
      case "archived":
        return <span className="badge badge-archived">OFFBOARDED (ARCHIVED)</span>;
      default:
        return <span className="badge badge-secondary">{st.toUpperCase()}</span>;
    }
  };

  // Count metrics
  const countBench = employees.filter(e => (e.status || (e.is_on_bench ? "on_bench" : "assigned")) === "on_bench").length;
  const countAssigned = employees.filter(e => e.status === "assigned").length;
  const countSuspended = employees.filter(e => e.status === "suspended").length;
  const countArchived = employees.filter(e => e.status === "archived").length;

  const PREVIEW_LIMIT = 140;

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4 flex-wrap gap-4">
        <div>
          <h1>Talent Pool & Bench Management</h1>
          <p className="text-muted">Lifecycle tracking for internal staffing and candidate availability.</p>
        </div>
        <button 
          className="btn btn-primary flex items-center gap-4"
          onClick={() => {
            setName("");
            setResumeText("");
            setShowAddModal(true);
          }}
        >
          <IconPlus size={18} />
          <span>Add New Talent</span>
        </button>
      </header>

      {/* Controls: Search & Tabs */}
      <div className="flex justify-between items-center gap-4 flex-wrap mb-4">
        {/* Tabs */}
        <div className="flex gap-4" style={{ borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
          <button 
            className={`btn ${activeTab === 'on_bench' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('on_bench')}
          >
            Bench ({countBench})
          </button>
          <button 
            className={`btn ${activeTab === 'assigned' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('assigned')}
          >
            Assigned ({countAssigned})
          </button>
          <button 
            className={`btn ${activeTab === 'suspended' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('suspended')}
          >
            Suspended ({countSuspended})
          </button>
          <button 
            className={`btn ${activeTab === 'archived' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('archived')}
          >
            Archived ({countArchived})
          </button>
          <button 
            className={`btn ${activeTab === 'all' ? 'btn-primary' : 'btn-outline'}`}
            onClick={() => setActiveTab('all')}
          >
            All ({employees.length})
          </button>
        </div>

        {/* Search */}
        <div style={{ position: 'relative', width: '280px' }}>
          <span style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }}>
            <IconSearch size={16} />
          </span>
          <input 
            type="text"
            className="input-field"
            placeholder="Search by name or skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{ paddingLeft: '34px' }}
          />
        </div>
      </div>

      {/* Candidate List */}
      <div className="flex-col gap-4">
        {loading ? (
          <p>Loading talent pool...</p>
        ) : filteredEmployees.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
            <p className="text-muted">No candidates found in this view.</p>
          </div>
        ) : (
          filteredEmployees.map((emp) => {
            const currentStatus = emp.status || (emp.is_on_bench ? "on_bench" : "assigned");
            const isExpanded = !!expandedIds[emp.id];
            const fullResume = emp.resume_text || "";
            const isLong = fullResume.length > PREVIEW_LIMIT;
            const textToShow = isLong && !isExpanded ? fullResume.slice(0, PREVIEW_LIMIT) + "..." : fullResume;

            return (
              <div key={emp.id} className="card flex justify-between items-start gap-4">
                {/* Candidate Content Info */}
                <div style={{ flex: 1 }}>
                  <div className="flex items-center gap-4 mb-4">
                    <h3>{emp.name}</h3>
                    {getStatusBadge(emp.status, emp.is_on_bench)}
                  </div>
                  <p className="text-muted" style={{ whiteSpace: 'pre-line' }}>{textToShow}</p>
                  
                  {isLong && (
                    <button 
                      onClick={() => toggleExpand(emp.id)}
                      style={{
                        background: 'none',
                        border: 'none',
                        padding: '4px 0',
                        color: 'var(--text-muted)',
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '4px',
                        marginTop: '6px'
                      }}
                    >
                      {isExpanded ? "Show Less ▲" : "Show More ▼"}
                    </button>
                  )}
                </div>

                {/* Fluent Pipe Toolbar (Top-Anchored Fixed Slot) */}
                <div className="toolbar-group" style={{ alignSelf: 'flex-start', flexShrink: 0 }}>
                  <div className="tooltip-wrapper">
                    <button 
                      className="toolbar-icon-btn toolbar-icon-btn-primary"
                      onClick={() => openEdit(emp)}
                      aria-label="Edit Profile"
                    >
                      <IconEdit size={18} />
                    </button>
                    <span className="fluent-tooltip">Edit Profile</span>
                  </div>

                  <div className="pipe-divider" />

                  {currentStatus !== "assigned" && (
                    <div className="tooltip-wrapper">
                      <button 
                        className="toolbar-icon-btn toolbar-icon-btn-primary"
                        onClick={() => handleStatusChange(emp.id, "assigned")}
                        aria-label="Deploy to Project"
                      >
                        <IconCheck size={18} />
                      </button>
                      <span className="fluent-tooltip">Deploy / Onboard</span>
                    </div>
                  )}

                  {currentStatus !== "on_bench" && (
                    <div className="tooltip-wrapper">
                      <button 
                        className="toolbar-icon-btn toolbar-icon-btn-success"
                        onClick={() => handleStatusChange(emp.id, "on_bench")}
                        aria-label="Move to Bench"
                      >
                        <IconUsers size={18} />
                      </button>
                      <span className="fluent-tooltip">Move to Bench</span>
                    </div>
                  )}

                  {currentStatus !== "suspended" && (
                    <div className="tooltip-wrapper">
                      <button 
                        className="toolbar-icon-btn toolbar-icon-btn-archive"
                        onClick={() => handleStatusChange(emp.id, "suspended")}
                        aria-label="Suspend Candidate"
                      >
                        <IconPause size={18} />
                      </button>
                      <span className="fluent-tooltip">Suspend Hold</span>
                    </div>
                  )}

                  <div className="pipe-divider" />

                  {currentStatus !== "archived" ? (
                    <div className="tooltip-wrapper">
                      <button 
                        className="toolbar-icon-btn toolbar-icon-btn-danger"
                        onClick={() => handleStatusChange(emp.id, "archived")}
                        aria-label="Archive Candidate"
                      >
                        <IconArchive size={18} />
                      </button>
                      <span className="fluent-tooltip">Archive / Offboard</span>
                    </div>
                  ) : (
                    <div className="tooltip-wrapper">
                      <button 
                        className="toolbar-icon-btn toolbar-icon-btn-success"
                        onClick={() => handleStatusChange(emp.id, "on_bench")}
                        aria-label="Restore Candidate"
                      >
                        <IconRestore size={18} />
                      </button>
                      <span className="fluent-tooltip">Restore to Bench</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h2 className="mb-4">Add New Candidate</h2>
            <form onSubmit={handleCreate} className="flex-col gap-4">
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Candidate Name</label>
                <input 
                  type="text"
                  className="input-field mt-4"
                  placeholder="e.g. Sarah Jenkins"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Resume & Skills Summary</label>
                <textarea 
                  className="input-field mt-4"
                  rows={5}
                  placeholder="Paste candidate skills, background, and experience summary..."
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  required
                />
              </div>
              <div className="flex justify-between items-center mt-4">
                <button 
                  type="button" 
                  className="btn btn-outline" 
                  onClick={() => setShowAddModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? "Saving..." : "Add Talent"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && selectedEmp && (
        <div className="modal-overlay">
          <div className="modal-card">
            <h2 className="mb-4">Edit Candidate Profile</h2>
            <form onSubmit={handleEditSubmit} className="flex-col gap-4">
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Candidate Name</label>
                <input 
                  type="text"
                  className="input-field mt-4"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 600 }}>Resume & Skills Summary</label>
                <textarea 
                  className="input-field mt-4"
                  rows={5}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  required
                />
              </div>
              <div className="flex justify-between items-center mt-4">
                <button 
                  type="button" 
                  className="btn btn-outline" 
                  onClick={() => setShowEditModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting ? "Updating..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
