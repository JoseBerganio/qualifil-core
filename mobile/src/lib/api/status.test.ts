import { getAppStatus } from "./status";

describe("getAppStatus", () => {
  const originalFetch = global.fetch;

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("requests the backend liveness endpoint and returns its payload", async () => {
    const payload = {
      status: "ok",
      environment: "development",
      version: "0.1.0",
    };
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      text: async () => JSON.stringify(payload),
      json: async () => payload,
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    await expect(getAppStatus()).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/health/"),
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("propagates API errors", async () => {
    const fetchMock = jest.fn().mockResolvedValue({
      ok: false,
      status: 503,
      text: async () => "{}",
      json: async () => ({
        error: {
          code: "SERVICE_UNAVAILABLE",
          message: "Backend unavailable.",
          status: 503,
        },
      }),
    });
    global.fetch = fetchMock as unknown as typeof fetch;

    await expect(getAppStatus()).rejects.toMatchObject({
      code: "SERVICE_UNAVAILABLE",
      status: 503,
    });
  });
});
