import { createApiClient } from "@qualifil/api-client";

// Empty by default so the Vite dev proxy keeps browser requests same-origin.
// Production builds set VITE_API_BASE_URL to the public API origin.
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

const client = createApiClient({ baseUrl });

export function apiGet<T = unknown>(path: string): Promise<T> {
  return client.get<T>(path);
}

export function apiPost<T = unknown>(path: string, body?: unknown): Promise<T> {
  return client.post<T>(path, body);
}

export { ApiError } from "@qualifil/api-client";
