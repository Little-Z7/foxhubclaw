export type Platform = {
  id: string;
  name: string;
  name_en: string;
  post: boolean;
  comment: boolean;
  comment_note: string;
};

export type Meta = {
  name: string;
  mode: string;
  auth_required: boolean;
  platforms: Platform[];
  default_prompts: string[];
};

const tokenKey = "foxhubclaw.token";

export function getToken(): string {
  return localStorage.getItem(tokenKey) || "";
}

export function setToken(token: string): void {
  if (token) localStorage.setItem(tokenKey, token);
  else localStorage.removeItem(tokenKey);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type") && init.body) headers.set("Content-Type", "application/json");
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(path, { ...init, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "请求失败");
  }
  if (response.headers.get("content-type")?.includes("application/json")) {
    return response.json() as Promise<T>;
  }
  return undefined as T;
}

export const api = {
  meta: () => request<Meta>("/api/meta"),
  register: (body: { username: string; password: string; email?: string }) =>
    request<{ token: string; username: string; is_admin: boolean }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: (body: { login: string; password: string }) =>
    request<{ token: string; username: string; is_admin: boolean }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  me: () => request<{ id: number; username: string; is_admin: boolean }>("/api/me"),
  settings: () =>
    request<{
      api_key_masked: string;
      has_key: boolean;
      limit_per_platform: number;
      comment_depth: number;
      prompts: string[];
    }>("/api/settings"),
  saveSettings: (body: Record<string, unknown>) =>
    request<{
      api_key_masked: string;
      has_key: boolean;
      limit_per_platform: number;
      comment_depth: number;
      prompts: string[];
    }>("/api/settings", { method: "PUT", body: JSON.stringify(body) }),
  search: (body: { keyword: string; platforms: string[]; kinds: string[] }) =>
    request<{
      run_id: number;
      report_id: number;
      status: string;
      items: Array<Record<string, unknown>>;
      failures: Array<{ platform: string; kind: string; message: string }>;
    }>("/api/search", { method: "POST", body: JSON.stringify(body) }),
  tasks: () => request<Array<Record<string, unknown>>>("/api/tasks"),
  createTask: (body: Record<string, unknown>) => request("/api/tasks", { method: "POST", body: JSON.stringify(body) }),
  toggleTask: (id: number) => request(`/api/tasks/${id}/toggle`, { method: "POST" }),
  reports: () => request<Array<Record<string, unknown>>>("/api/reports"),
  runs: () => request<Array<Record<string, unknown>>>("/api/runs"),
  adminUsers: () => request<Array<Record<string, unknown>>>("/api/admin/users"),
  setActive: (id: number, is_active: boolean) =>
    request(`/api/admin/users/${id}`, { method: "PATCH", body: JSON.stringify({ is_active }) }),
};

export function fileUrl(reportId: number, kind: "xlsx" | "html" | "pdf"): string {
  const token = getToken();
  const path = `/api/reports/${reportId}/file/${kind}`;
  return token ? `${path}?token=${encodeURIComponent(token)}` : path;
}

export async function downloadReportFile(reportId: number, kind: "xlsx" | "html" | "pdf"): Promise<string> {
  const response = await fetch(fileUrl(reportId, kind));
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : "下载失败");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `FoxHubClaw-${reportId}.${kind}`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 30_000);
  return link.download;
}
