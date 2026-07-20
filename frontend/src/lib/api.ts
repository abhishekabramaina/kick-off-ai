const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

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
  driveIngest: (projectId: string, data: { file_id: string, access_token: string, file_name: string, mime_type: string }) =>
    fetchAPI(`/projects/${projectId}/drive-ingest`, { method: "POST", body: JSON.stringify(data) }),
  localUpload: (projectId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return fetch(`${API_BASE}/projects/${projectId}/upload`, {
      method: "POST",
      body: formData,
    }).then(res => res.json());
  },
  ingestExisting: (projectId: string, fileName: string) =>
    fetchAPI(`/projects/${projectId}/ingest-existing?file_name=${encodeURIComponent(fileName)}`, { method: "POST" }),
  listAvailableFiles: () => fetchAPI("/projects/available-files"),
  roles: (id: string) => fetchAPI(`/resourcing/extract-roles/${id}`, { method: "POST" }),
  matches: (roleId: string) => fetchAPI(`/resourcing/match/${roleId}`, { method: "POST" }),
  getRoleMatches: (roleId: string) => fetchAPI(`/resourcing/matches/${roleId}`),
  archive: (id: string) => fetchAPI(`/projects/${id}/archive`, { method: "POST" }),
  unarchive: (id: string) => fetchAPI(`/projects/${id}/unarchive`, { method: "POST" }),
  delete: (id: string) => fetchAPI(`/projects/${id}`, { method: "DELETE" }),
};

export const employeesApi = {
  list: () => fetchAPI("/employees/"),
  bench: () => fetchAPI("/employees/bench"),
  create: (data: { name: string; resume_text: string; is_on_bench?: boolean; status?: string }) =>
    fetchAPI("/employees/", { method: "POST", body: JSON.stringify(data) }),
  updateStatus: (id: number | string, status: string) =>
    fetchAPI(`/employees/${id}/status?status=${encodeURIComponent(status)}`, { method: "PATCH" }),
  updateProfile: (id: number | string, data: { name?: string; resume_text?: string }) =>
    fetchAPI(`/employees/${id}`, { method: "PUT", body: JSON.stringify(data) }),
};
