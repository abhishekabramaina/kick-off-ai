"use client";

import { useEffect, useState } from "react";
import { employeesApi } from "@/lib/api";

export default function Bench() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    employeesApi.bench().then(setEmployees).finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex-col gap-4">
      <header className="flex justify-between items-center mb-4">
        <h1>Internal Bench</h1>
        <div className="badge badge-success">{employees.length} Available</div>
      </header>

      <div className="flex-col gap-4">
        {loading ? (
          <p>Loading bench...</p>
        ) : (
          employees.map((emp) => (
            <div key={emp.id} className="card">
              <div className="flex justify-between items-center mb-4">
                <h3>{emp.name}</h3>
                <div className="badge badge-success">AVAILABLE</div>
              </div>
              <p className="text-muted">{emp.resume_text}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
