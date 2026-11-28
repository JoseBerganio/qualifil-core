import { describe, expect, it, vi } from "vitest";

import { ApiError, createApiClient } from "./index";

function jsonResponse(
  data: unknown,
  { ok = true, status = ok ? 200 : 500 }: { ok?: boolean; status?: number } = {},
): Response {
  return {
    ok,
    status,
    text: async () => (data === undefined ? "" : JSON.stringify(data)),
    json: async () => data,
  } as Response;
}

describe("createApiClient", () => {
  it("uses a same-origin relative URL by default", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ status: "ok" }));
    const client = createApiClient({
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    const data = await client.get<{ status: string }>("/api/v1/health/");

    expect(data).toEqual({ status: "ok" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/health/",
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("joins an origin with API paths without duplicating slashes", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
    const client = createApiClient({
      baseUrl: "http://localhost:8000/",
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    await client.get("api/v1/health/");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/health/",
      expect.any(Object),
    );
  });

  it("adds a bearer token from the token provider", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({}));
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      fetchImpl: fetchMock as unknown as typeof fetch,
      getAccessToken: () => "access-token",
    });

    await client.get("/api/v1/health/");

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer access-token");
  });

  it("serializes JSON request bodies", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ created: true }));
    const client = createApiClient({
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    const data = await client.post<{ created: boolean }>("/api/v1/probe/", {
      name: "test",
    });

    expect(data).toEqual({ created: true });
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("POST");
    expect(init.body).toBe(JSON.stringify({ name: "test" }));
    expect((init.headers as Record<string, string>)["Content-Type"]).toBe("application/json");
  });

  it("maps the standardized error envelope to ApiError", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse(
        {
          error: {
            code: "FORBIDDEN",
            message: "You do not have permission.",
            status: 403,
            details: [{ field: "role", message: "Not allowed." }],
          },
        },
        { ok: false, status: 403 },
      ),
    );
    const client = createApiClient({
      fetchImpl: fetchMock as unknown as typeof fetch,
    });

    await expect(client.get("/api/v1/private/")).rejects.toMatchObject({
      name: "ApiError",
      status: 403,
      code: "FORBIDDEN",
      message: "You do not have permission.",
      details: [{ field: "role", message: "Not allowed." }],
    });
  });

  it("exposes typed auth login and stores returned tokens", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ access: "new-access", refresh: "new-refresh" }));
    const setTokens = vi.fn();
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      fetchImpl: fetchMock as unknown as typeof fetch,
      setTokens,
    });

    await client.auth.login({ email: "user@example.test", password: "secret" });

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://localhost:8000/api/v1/auth/login/");
    expect(init.method).toBe("POST");
    expect((init.headers as Record<string, string>)["X-Auth-Mode"]).toBe("bearer");
    expect(setTokens).toHaveBeenCalledWith({ access: "new-access", refresh: "new-refresh" });
  });

  it("uses cookies and includes credentials in cookie auth mode", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ user: { email: "user@example.test" } }));
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      fetchImpl: fetchMock as unknown as typeof fetch,
      authMode: "cookie",
      getCsrfToken: () => "csrf-token",
    });

    await client.auth.login({ email: "user@example.test", password: "secret" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.credentials).toBe("include");
    expect((init.headers as Record<string, string>)["X-Auth-Mode"]).toBe("cookie");
    expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBe("csrf-token");
    expect((init.headers as Record<string, string>).Authorization).toBeUndefined();
  });

  it("refreshes an expired bearer token once and retries the request", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse(
          {
            error: {
              code: "UNAUTHENTICATED",
              message: "Authentication credentials were not provided.",
              status: 401,
            },
          },
          { ok: false, status: 401 },
        ),
      )
      .mockResolvedValueOnce(jsonResponse({ access: "fresh-access", refresh: "fresh-refresh" }))
      .mockResolvedValueOnce(jsonResponse({ id: "user-1", email: "user@example.test" }));

    const setTokens = vi.fn();
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      fetchImpl: fetchMock as unknown as typeof fetch,
      getAccessToken: () => "expired-access",
      getRefreshToken: () => "old-refresh",
      setTokens,
    });

    await expect(client.auth.getMe()).resolves.toMatchObject({ id: "user-1" });

    expect(fetchMock).toHaveBeenCalledTimes(3);
    const [refreshUrl, refreshInit] = fetchMock.mock.calls[1] as [string, RequestInit];
    expect(refreshUrl).toBe("http://localhost:8000/api/v1/auth/refresh/");
    expect(refreshInit.body).toBe(JSON.stringify({ refresh: "old-refresh" }));
    expect(setTokens).toHaveBeenCalledWith({
      access: "fresh-access",
      refresh: "fresh-refresh",
    });

    const [, retryInit] = fetchMock.mock.calls[2] as [string, RequestInit];
    expect((retryInit.headers as Record<string, string>).Authorization).toBe("Bearer fresh-access");
  });

  it("refreshes a 401 through the cookie endpoint when using cookie mode", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse(
          { error: { code: "UNAUTHENTICATED", message: "Expired.", status: 401 } },
          { ok: false, status: 401 },
        ),
      )
      .mockResolvedValueOnce(jsonResponse({ user: { email: "user@example.test" } }))
      .mockResolvedValueOnce(jsonResponse({ email: "user@example.test" }));

    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      fetchImpl: fetchMock as unknown as typeof fetch,
      authMode: "cookie",
      getCsrfToken: () => "csrf-token",
    });

    await expect(client.auth.getMe()).resolves.toMatchObject({ email: "user@example.test" });

    expect(fetchMock).toHaveBeenCalledTimes(3);
    const [, refreshInit] = fetchMock.mock.calls[1] as [string, RequestInit];
    expect(refreshInit.credentials).toBe("include");
    expect((refreshInit.headers as Record<string, string>)["X-Auth-Mode"]).toBe("cookie");
    expect((refreshInit.headers as Record<string, string>)["X-CSRFToken"]).toBe("csrf-token");
  });

  it("clears stored tokens on logout", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204, text: async () => "" });
    const clearTokens = vi.fn();
    const client = createApiClient({
      baseUrl: "http://localhost:8000",
      fetchImpl: fetchMock as unknown as typeof fetch,
      getRefreshToken: () => "refresh-token",
      clearTokens,
    });

    await client.auth.logout();

    expect(clearTokens).toHaveBeenCalled();
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.body).toBe(JSON.stringify({ refresh: "refresh-token" }));
  });

  it("times out slow requests with a TIMEOUT error", async () => {
    const fetchMock = vi.fn(
      (_url: string, init: RequestInit) =>
        new Promise<Response>((_resolve, reject) => {
          init.signal?.addEventListener("abort", () => {
            const error = new Error("aborted");
            error.name = "AbortError";
            reject(error);
          });
        }),
    );
    const client = createApiClient({
      fetchImpl: fetchMock as unknown as typeof fetch,
      timeoutMs: 5,
    });

    await expect(client.get("/slow")).rejects.toBeInstanceOf(ApiError);
    await expect(client.get("/slow")).rejects.toMatchObject({
      code: "TIMEOUT",
      status: 0,
    });
  });
});
