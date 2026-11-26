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
    it("posts JSON and returns the parsed body", async () => {
      const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ created: true }));
      vi.stubGlobal("fetch", fetchMock);

      const data = await apiPost("/api/v1/residents/", { name: "Jose" });

      expect(data).toEqual({ created: true });
      const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
      expect(init.method).toBe("POST");
      expect(init.body).toBe(JSON.stringify({ name: "Jose" }));
    });
  });
});
