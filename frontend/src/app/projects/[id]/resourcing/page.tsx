"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { projectsApi, employeesApi } from "@/lib/api";

function RoleCard({ role, employees }: { role: any, employees: any[] }) {
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchMatches() {
      try {
        // Trigger matching if it hasn't happened
        await projectsApi.matches(role.id);
        // Get the results
        const m = await projectsApi.getRoleMatches(role.id);
        setMatches(m);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchMatches();
  }, [role.id]);

  const getEmployeeName = (id: number) => employees.find(e => e.id === id)?.name || "Unknown";

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h3>{role.title}</h3>
        <div className={`badge ${matches.length > 0 ? 'badge-success' : 'badge-warning'}`}>
          {matches.length > 0 ? 'MATCHES FOUND' : 'ANALYZING...'}
        </div>
      </div>
      <p className="mb-4"><strong>Requirement:</strong> {role.draft_jd}</p>
      
      <div className="mt-4">
        <h4>Candidate Matches</h4>
        <div className="flex-col gap-4 mt-4">
          {loading ? (
            <p className="text-muted">AI is calculating match scores...</p>
          ) : matches.length === 0 ? (
            <p className="text-muted">No suitable internal matches found above threshold.</p>
          ) : (
            matches.map((match: any) => (
              <div key={match.id} className="card" style={{ 
                borderLeft: `4px solid ${match.score > 70 ? 'var(--success)' : 'var(--warning)'}`,
                background: '#fcfcfc'
              }}>
                <div className="flex justify-between items-center">
                  <strong>{getEmployeeName(match.employee_id)}</strong>
                  <span className={`badge ${match.score > 70 ? 'badge-success' : 'badge-warning'}`}>
                    {Math.round(match.score)}% Match
                  </span>
                </div>
                <p className="mt-4" style={{ fontSize: '0.9rem' }}>{match.justification}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default function Resourcing() {
  const { id } = useParams();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [roles, setRoles] = useState<any[]>([]);
  const [project, setProject] = useState<any>(null);
  const [employees, setEmployees] = useState<any[]>([]);

  useEffect(() => {
    async function init() {
      try {
        const [p, emps] = await Promise.all([
          projectsApi.get(id as string),
          employeesApi.list()
        ]);
        setProject(p);
        setEmployees(emps);
        
        const extractedRoles = await projectsApi.roles(id as string);
        setRoles(extractedRoles);
      } catch (err) {
        alert("Failed to load resourcing data");
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [id]);

  if (loading) return <div>Loading resourcing data...</div>;

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4">
        <div>
          <h1>Resourcing: {project?.name}</h1>
          <p className="text-muted">AI-identified roles and best-fit bench employees.</p>
        </div>
        <button className="btn btn-outline" onClick={() => router.push(`/projects/${id}`)}>
          View PRD
        </button>
      </header>

      <div className="flex-col gap-4">
        {roles.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
             <p className="text-muted">No roles extracted yet.</p>
          </div>
        ) : (
          roles.map((role: any) => (
            <RoleCard key={role.id} role={role} employees={employees} />
          ))
        )}
      </div>
    </div>
  );
}
