import { createApiClient } from "@qualifil/api-client";

import { API_BASE_URL } from "../../config";
import { tokenStorage } from "../storage/tokenStorage";

export const apiClient = createApiClient({
  baseUrl: API_BASE_URL,
  authMode: "bearer",
  getAccessToken: () => tokenStorage.getAccessToken(),
  getRefreshToken: () => tokenStorage.getRefreshToken(),
  setTokens: (tokens) => tokenStorage.setTokens(tokens),
  clearTokens: () => tokenStorage.clear(),
  timeoutMs: 15000,
});
