import { createApiClient } from "@qualifil/api-client";

import { API_BASE_URL } from "../../config";
import { tokenStorage } from "../storage/tokenStorage";

export const apiClient = createApiClient({
  baseUrl: API_BASE_URL,
  getAccessToken: () => tokenStorage.getAccessToken(),
  timeoutMs: 15000,
});
