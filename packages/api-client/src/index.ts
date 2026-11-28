export interface ApiErrorDetail {
  field?: string;
  message: string;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    status: number;
    details?: ApiErrorDetail[];
  };
}

/**
 * Error raised for failed API requests. It preserves the standardized
 * QUALIFIL error envelope so web and mobile clients can react consistently.
 */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: ApiErrorDetail[];

  constructor(message: string, status: number, code = "ERROR", details: ApiErrorDetail[] = []) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export type AuthMode = "bearer" | "cookie";

export interface AuthUser {
  id: string;
  email: string;
  phone_number: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_staff: boolean;
  created_at: string;
}

export interface AuthTokenPair {
  access: string;
  refresh: string;
}

export interface AuthResponse {
  access?: string;
  refresh?: string;
  user?: AuthUser;
}

export interface RegisterInput {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
  phone_number?: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface ChangePasswordInput {
  current_password: string;
  new_password: string;
}

export interface AuthApi {
  register(input: RegisterInput): Promise<AuthResponse>;
  login(input: LoginInput): Promise<AuthResponse>;
  refresh(): Promise<AuthResponse>;
  logout(refreshToken?: string): Promise<void>;
  getMe(): Promise<AuthUser>;
  changePassword(input: ChangePasswordInput): Promise<void>;
}

export interface ApiClientOptions {
  /** API origin. Leave empty to use same-origin relative requests. */
  baseUrl?: string;
  /** Injectable fetch implementation, primarily for tests. */
  fetchImpl?: typeof fetch;
  /** Returns the current access token, if any. */
  getAccessToken?: () => string | null | Promise<string | null>;
  /** Returns the current refresh token for bearer-token clients. */
  getRefreshToken?: () => string | null | Promise<string | null>;
  /** Persists a rotated token pair after login or refresh. */
  setTokens?: (tokens: AuthTokenPair) => void | Promise<void>;
  /** Clears locally stored tokens after logout or an unrecoverable auth failure. */
  clearTokens?: () => void | Promise<void>;
  /** Called when a token refresh attempt fails. */
  onAuthFailure?: () => void | Promise<void>;
  /** Supplies a CSRF token for cookie-mode unsafe requests. Defaults to /auth/csrf/. */
  getCsrfToken?: () => string | null | Promise<string | null>;
  /** Bearer tokens for mobile/native, httpOnly cookies for the web. */
  authMode?: AuthMode;
  /** Fetch credentials mode. Defaults to "include" in cookie mode. */
  credentials?: RequestCredentials;
  /** Attempt a single refresh-and-retry when a request returns 401. */
  refreshOnUnauthorized?: boolean;
  /** Abort requests that exceed this duration. */
  timeoutMs?: number;
  /** Headers added to every request. */
  headers?: Record<string, string>;
}

export interface ApiRequestOptions {
  signal?: AbortSignal;
  headers?: Record<string, string>;
}

export interface ApiClient {
  get<T>(path: string, options?: ApiRequestOptions): Promise<T>;
  post<T>(path: string, body?: unknown, options?: ApiRequestOptions): Promise<T>;
  put<T>(path: string, body?: unknown, options?: ApiRequestOptions): Promise<T>;
  patch<T>(path: string, body?: unknown, options?: ApiRequestOptions): Promise<T>;
  delete<T>(path: string, options?: ApiRequestOptions): Promise<T>;
  request<T>(method: string, path: string, body?: unknown, options?: ApiRequestOptions): Promise<T>;
  auth: AuthApi;
}

const AUTH_PATHS = {
  csrf: "/api/v1/auth/csrf/",
  register: "/api/v1/auth/register/",
  login: "/api/v1/auth/login/",
  refresh: "/api/v1/auth/refresh/",
  logout: "/api/v1/auth/logout/",
  me: "/api/v1/auth/me/",
  changePassword: "/api/v1/auth/change-password/",
} as const;

const NON_REFRESHABLE_PATHS = new Set<string>([
  AUTH_PATHS.register,
  AUTH_PATHS.login,
  AUTH_PATHS.refresh,
  AUTH_PATHS.logout,
]);

function joinUrl(baseUrl: string, path: string): string {
  const normalizedBase = baseUrl.replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

function isErrorEnvelope(value: unknown): value is ApiErrorEnvelope {
  if (value === null || typeof value !== "object" || !("error" in value)) {
    return false;
  }
  const error = (value as { error?: unknown }).error;
  return error !== null && typeof error === "object";
}

async function parseErrorResponse(response: Response): Promise<ApiError> {
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    return new ApiError(`API request failed with status ${response.status}`, response.status);
  }

  if (isErrorEnvelope(body)) {
    return new ApiError(
      body.error.message || `API request failed with status ${response.status}`,
      response.status,
      body.error.code || "ERROR",
      body.error.details ?? [],
    );
  }

  return new ApiError(`API request failed with status ${response.status}`, response.status);
}

async function parseBody<T>(response: Response): Promise<T> {
  if (response.status === 204) {
    return undefined as T;
  }
  const text = await response.text();
  if (!text) {
    return undefined as T;
  }
  return JSON.parse(text) as T;
}

export function createApiClient(options: ApiClientOptions = {}): ApiClient {
  const {
    baseUrl = "",
    fetchImpl,
    getAccessToken,
    getRefreshToken,
    setTokens,
    clearTokens,
    onAuthFailure,
    getCsrfToken,
    authMode = "bearer",
    credentials,
    refreshOnUnauthorized = true,
    timeoutMs,
    headers: defaultHeaders = {},
  } = options;

  const credentialsMode = credentials ?? (authMode === "cookie" ? "include" : undefined);
  let refreshedAccessToken: string | null = null;
  let refreshPromise: Promise<boolean> | null = null;
  let csrfToken: string | null = null;
  let csrfPromise: Promise<string | null> | null = null;

  function getFetch(): typeof fetch {
    const doFetch = fetchImpl ?? globalThis.fetch;
    if (!doFetch) {
      throw new ApiError("No fetch implementation is available.", 0, "FETCH_UNAVAILABLE");
    }
    return doFetch;
  }

  async function persistTokens(data: AuthResponse): Promise<void> {
    if (data.access && data.refresh && setTokens) {
      await setTokens({ access: data.access, refresh: data.refresh });
    }
  }

  async function fetchCsrfToken(): Promise<string | null> {
    const doFetch = getFetch();
    const response = await doFetch(joinUrl(baseUrl, AUTH_PATHS.csrf), {
      method: "GET",
      headers: {
        Accept: "application/json",
        ...defaultHeaders,
        "X-Auth-Mode": authMode,
      },
      credentials: credentialsMode,
    });
    if (!response.ok) {
      return null;
    }
    const data = await parseBody<{ csrfToken?: string }>(response);
    return data?.csrfToken ?? null;
  }

  async function ensureCsrfToken(): Promise<string | null> {
    if (csrfToken) {
      return csrfToken;
    }
    if (csrfPromise) {
      return csrfPromise;
    }

    csrfPromise = (async () => {
      const provided = await getCsrfToken?.();
      const token = provided ?? (await fetchCsrfToken());
      csrfToken = token;
      return token;
    })();

    try {
      return await csrfPromise;
    } finally {
      csrfPromise = null;
    }
  }

  async function performRefresh(): Promise<boolean> {
    if (refreshPromise) {
      return refreshPromise;
    }

    refreshPromise = (async () => {
      const doFetch = getFetch();
      const headers: Record<string, string> = {
        Accept: "application/json",
        ...defaultHeaders,
        "X-Auth-Mode": authMode,
      };
      let body: string | undefined;
      if (authMode === "bearer") {
        const refreshToken = await getRefreshToken?.();
        if (!refreshToken) {
          return false;
        }
        headers["Content-Type"] = "application/json";
        body = JSON.stringify({ refresh: refreshToken });
      } else {
        const token = await ensureCsrfToken();
        if (token) {
          headers["X-CSRFToken"] = token;
        }
      }

      const response = await doFetch(joinUrl(baseUrl, AUTH_PATHS.refresh), {
        method: "POST",
        headers,
        body,
        credentials: credentialsMode,
      });

      if (!response.ok) {
        await onAuthFailure?.();
        return false;
      }

      const data = await parseBody<AuthResponse>(response);
      if (data?.access) {
        refreshedAccessToken = data.access;
        await persistTokens(data);
      }
      return Boolean(data?.access) || authMode === "cookie";
    })();

    try {
      return await refreshPromise;
    } finally {
      refreshPromise = null;
    }
  }

  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
    requestOptions: ApiRequestOptions = {},
    allowRefresh = true,
  ): Promise<T> {
    const doFetch = getFetch();

    const headers: Record<string, string> = {
      Accept: "application/json",
      ...defaultHeaders,
      ...requestOptions.headers,
    };

    if (body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    const token = refreshedAccessToken ?? (await getAccessToken?.());
    if (token && !headers.Authorization) {
      headers.Authorization = `Bearer ${token}`;
    }

    const unsafeMethod = !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method.toUpperCase());
    if (authMode === "cookie" && unsafeMethod && !headers["X-CSRFToken"]) {
      const csrf = await ensureCsrfToken();
      if (csrf) {
        headers["X-CSRFToken"] = csrf;
      }
    }

    const controller = new AbortController();
    const timeoutId =
      timeoutMs === undefined ? undefined : setTimeout(() => controller.abort(), timeoutMs);
    const signal = requestOptions.signal ?? controller.signal;

    try {
      const response = await doFetch(joinUrl(baseUrl, path), {
        method,
        headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        signal,
        credentials: credentialsMode,
      });

      if (
        response.status === 401 &&
        allowRefresh &&
        refreshOnUnauthorized &&
        !NON_REFRESHABLE_PATHS.has(path)
      ) {
        const refreshed = await performRefresh();
        if (refreshed) {
          return request<T>(method, path, body, requestOptions, false);
        }
      }

      if (!response.ok) {
        throw await parseErrorResponse(response);
      }

      return await parseBody<T>(response);
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      if (error instanceof Error && error.name === "AbortError") {
        throw new ApiError("The request was aborted or timed out.", 0, "TIMEOUT");
      }
      throw error;
    } finally {
      if (timeoutId !== undefined) {
        clearTimeout(timeoutId);
      }
    }
  }

  const auth: AuthApi = {
    async register(input) {
      const data = await request<AuthResponse>(
        "POST",
        AUTH_PATHS.register,
        input,
        { headers: { "X-Auth-Mode": authMode } },
        false,
      );
      await persistTokens(data);
      return data;
    },

    async login(input) {
      const data = await request<AuthResponse>(
        "POST",
        AUTH_PATHS.login,
        input,
        { headers: { "X-Auth-Mode": authMode } },
        false,
      );
      await persistTokens(data);
      return data;
    },

    async refresh() {
      const body =
        authMode === "bearer" ? { refresh: (await getRefreshToken?.()) ?? undefined } : undefined;
      const data = await request<AuthResponse>(
        "POST",
        AUTH_PATHS.refresh,
        body,
        { headers: { "X-Auth-Mode": authMode } },
        false,
      );
      if (data?.access) {
        refreshedAccessToken = data.access;
      }
      await persistTokens(data);
      return data;
    },

    async logout(refreshToken) {
      try {
        const body =
          authMode === "bearer"
            ? { refresh: refreshToken ?? (await getRefreshToken?.()) ?? undefined }
            : undefined;
        await request<void>(
          "POST",
          AUTH_PATHS.logout,
          body,
          { headers: { "X-Auth-Mode": authMode } },
          false,
        );
      } finally {
        refreshedAccessToken = null;
        await clearTokens?.();
      }
    },

    getMe() {
      return request<AuthUser>("GET", AUTH_PATHS.me);
    },

    async changePassword(input) {
      await request<void>(
        "POST",
        AUTH_PATHS.changePassword,
        input,
        { headers: { "X-Auth-Mode": authMode } },
        true,
      );
    },
  };

  return {
    request,
    get: (path, requestOptions) => request("GET", path, undefined, requestOptions),
    post: (path, body, requestOptions) => request("POST", path, body, requestOptions),
    put: (path, body, requestOptions) => request("PUT", path, body, requestOptions),
    patch: (path, body, requestOptions) => request("PATCH", path, body, requestOptions),
    delete: (path, requestOptions) => request("DELETE", path, undefined, requestOptions),
    auth,
  };
}
