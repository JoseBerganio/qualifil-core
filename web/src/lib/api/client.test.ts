import { afterEach, describe, expect, it, vi } from "vitest";

import { apiGet, apiPost } from "./client";

function jsonResponse(data: unknown, ok = true): Response {
  return {
    ok,
    status: ok ? 200 : 500,
    text: async () => (data === undefined ? "" : JSON.stringify(data)),
    json: async () => data,
  } as Response;
}

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  describe("apiGet", () => {
    it("uses a same-origin URL so the dev proxy and browser CORS rules apply", async () => {
      const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ status: "ok" }));
      vi.stubGlobal("fetch", fetchMock);

      const data = await apiGet<{ status: string }>("/api/v1/health/");

      expect(fetchMock).toHaveBeenCalledWith(
        "/api/v1/health/",
        expect.objectContaining({ method: "GET" }),
      );
      expect(data).toEqual({ status: "ok" });
    });

    it("throws when the response is not ok", async () => {
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(null, false)));
      await expect(apiGet("/missing")).rejects.toThrow(/500/);
    });
  });

  describe("apiPost", () => {
    it("primes CSRF, posts JSON, and sends cookies", async () => {
      const fetchMock = vi.fn().mockImplementation((url: string) => {
        if (url === "/api/v1/auth/csrf/") {
          return Promise.resolve(jsonResponse({ csrfToken: "csrf-token" }));
        }
        return Promise.resolve(jsonResponse({ created: true }));
      });
      vi.stubGlobal("fetch", fetchMock);

      const data = await apiPost("/api/v1/residents/", { name: "Jose" });

      expect(data).toEqual({ created: true });
      const postCall = fetchMock.mock.calls.find(([url]) => url === "/api/v1/residents/") as [
        string,
        RequestInit,
      ];
      const [, init] = postCall;
      expect(init.method).toBe("POST");
      expect(init.body).toBe(JSON.stringify({ name: "Jose" }));
      expect(init.credentials).toBe("include");
      expect((init.headers as Record<string, string>)["X-CSRFToken"]).toBe("csrf-token");
    });
  });
});
