import { createApiClient } from "@qualifil/api-client";

// Empty by default so the Vite dev proxy keeps browser requests same-origin.
// Production builds set VITE_API_BASE_URL to the public API origin.
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

// Web authentication uses httpOnly cookies plus the CSRF double-submit token.
// Access and refresh JWTs are never exposed to JavaScript or localStorage.
const client = createApiClient({
  baseUrl,
  authMode: "cookie",
  credentials: "include",
});

export const authApi = client.auth;

export function apiGet<T = unknown>(path: string): Promise<T> {
  return client.get<T>(path);
}

export function apiPost<T = unknown>(path: string, body?: unknown): Promise<T> {
  return client.post<T>(path, body);
}

export function apiPatch<T = unknown>(path: string, body?: unknown): Promise<T> {
  return client.patch<T>(path, body);
}

export function apiDelete<T = unknown>(path: string): Promise<T> {
  return client.delete<T>(path);
}

export { ApiError } from "@qualifil/api-client";
