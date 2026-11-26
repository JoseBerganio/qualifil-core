import { describe, expect, it, vi } from "vitest";

import { apiGet } from "./client";
import { getAppStatus } from "./status";

vi.mock("./client", () => ({
  apiGet: vi.fn(),
}));

const mockedApiGet = vi.mocked(apiGet);

describe("getAppStatus", () => {
  it("requests the Django health endpoint", async () => {
    const data = { status: "ok", environment: "development", version: "0.1.0" };
    mockedApiGet.mockResolvedValue(data);

    await expect(getAppStatus()).resolves.toEqual(data);
    expect(mockedApiGet).toHaveBeenCalledWith("/api/v1/health/");
  });
});
