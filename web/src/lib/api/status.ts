import { apiGet } from "./client";
import type { AppStatus } from "./types";

export function getAppStatus(): Promise<AppStatus> {
  return apiGet<AppStatus>("/api/v1/health/");
}
