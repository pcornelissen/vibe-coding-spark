import type { ConsolidationResult, Project, ProjectDetail, ResultType } from "./types";

const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(detail.detail || response.statusText);
  }
  return response.json();
}

export const api = {
  listProjects: () => request<Project[]>("/projects"),

  createProject: (name: string, description?: string) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name, description }),
    }),

  getProject: (id: string) => request<ProjectDetail>(`/projects/${id}`),

  uploadDocuments: async (projectId: string, files: File[]) => {
    const results = [];
    for (const file of files) {
      const form = new FormData();
      form.append("file", file);
      const response = await fetch(`${BASE}/projects/${projectId}/documents`, {
        method: "POST",
        body: form,
      });
      if (!response.ok) throw new Error(`Upload failed: ${file.name}`);
      results.push(await response.json());
    }
    return results;
  },

  startProcessing: (projectId: string) =>
    request<void>(`/projects/${projectId}/process`, { method: "POST" }),

  getResults: (projectId: string) =>
    request<ConsolidationResult[]>(`/projects/${projectId}/results`),

  streamChat: (projectId: string, question: string): EventSource => {
    const params = new URLSearchParams({ question });
    return new EventSource(`${BASE}/projects/${projectId}/chat?${params}`);
  },

  streamConsolidate: (projectId: string, resultType: ResultType, query: string): EventSource => {
    const params = new URLSearchParams({ result_type: resultType, query });
    return new EventSource(`${BASE}/projects/${projectId}/consolidate?${params}`);
  },

  workflowStatus: (projectId: string): EventSource => {
    return new EventSource(`${BASE}/projects/${projectId}/workflow-status`);
  },
};
