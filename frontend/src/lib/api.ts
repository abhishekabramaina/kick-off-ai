const API_BASE = "http://localhost:8000";

export async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || res.statusText);
  }
  return res.json();
}

export const projectsApi = {
  list: () => fetchAPI("/projects/"),
  get: (id: string) => fetchAPI(`/projects/${id}`),
  create: (data: { name: string; raw_input: string }) => 
    fetchAPI("/projects/", { method: "POST", body: JSON.stringify(data) }),
  analyze: (id: string) => fetchAPI(`/projects/${id}/analyze`, { method: "POST" }),
  finalize: (id: string, clarifications: string) => 
    fetchAPI(`/projects/${id}/finalize?clarifications=${encodeURIComponent(clarifications)}`, { method: "POST" }),
  roles: (id: string) => fetchAPI(`/resourcing/extract-roles/${id}`, { method: "POST" }),
  matches: (roleId: string) => fetchAPI(`/resourcing/match/${roleId}`, { method: "POST" }),
  getRoleMatches: (roleId: string) => fetchAPI(`/resourcing/matches/${roleId}`),
};

export const employeesApi = {
  list: () => fetchAPI("/employees/"),
  bench: () => fetchAPI("/employees/bench"),
};
