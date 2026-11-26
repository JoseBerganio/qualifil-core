import { apiClient } from "./client";
import type { AppStatus } from "./types";

export function getAppStatus(): Promise<AppStatus> {
  return apiClient.get<AppStatus>("/api/v1/health/");
}
