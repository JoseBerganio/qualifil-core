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
