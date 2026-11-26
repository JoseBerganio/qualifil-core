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

export interface ApiClientOptions {
  /** API origin. Leave empty to use same-origin relative requests. */
  baseUrl?: string;
  /** Injectable fetch implementation, primarily for tests. */
  fetchImpl?: typeof fetch;
  /** Returns the current access token, if any. */
  getAccessToken?: () => string | null | Promise<string | null>;
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
}

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

export function createApiClient(options: ApiClientOptions = {}): ApiClient {
  const {
    baseUrl = "",
    fetchImpl,
    getAccessToken,
    timeoutMs,
    headers: defaultHeaders = {},
  } = options;

  async function request<T>(
    method: string,
    path: string,
    body?: unknown,
    requestOptions: ApiRequestOptions = {},
  ): Promise<T> {
    const doFetch = fetchImpl ?? globalThis.fetch;
    if (!doFetch) {
      throw new ApiError("No fetch implementation is available.", 0, "FETCH_UNAVAILABLE");
    }

    const headers: Record<string, string> = {
      Accept: "application/json",
      ...defaultHeaders,
      ...requestOptions.headers,
    };

    if (body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    const token = await getAccessToken?.();
    if (token && !headers.Authorization) {
      headers.Authorization = `Bearer ${token}`;
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
      });

      if (!response.ok) {
        throw await parseErrorResponse(response);
      }

      if (response.status === 204) {
        return undefined as T;
      }

      const text = await response.text();
      if (!text) {
        return undefined as T;
      }
      return JSON.parse(text) as T;
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

  return {
    request,
    get: (path, requestOptions) => request("GET", path, undefined, requestOptions),
    post: (path, body, requestOptions) => request("POST", path, body, requestOptions),
    put: (path, body, requestOptions) => request("PUT", path, body, requestOptions),
    patch: (path, body, requestOptions) => request("PATCH", path, body, requestOptions),
    delete: (path, requestOptions) => request("DELETE", path, undefined, requestOptions),
  };
}
