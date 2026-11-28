import { describe, expect, it } from "@jest/globals";

import { createMemoryTokenStorage } from "./tokenStorage";

describe("createMemoryTokenStorage", () => {
  it("starts empty, stores a token, and clears it", async () => {
    const storage = createMemoryTokenStorage();

    expect(await storage.getAccessToken()).toBeNull();

    await storage.setAccessToken("access-token");
    expect(await storage.getAccessToken()).toBe("access-token");

    await storage.clear();
    expect(await storage.getAccessToken()).toBeNull();
  });

  it("can start with an existing token", async () => {
    const storage = createMemoryTokenStorage("existing", "existing-refresh");
    expect(await storage.getAccessToken()).toBe("existing");
    expect(await storage.getRefreshToken()).toBe("existing-refresh");
  });

  it("stores and clears an access/refresh token pair", async () => {
    const storage = createMemoryTokenStorage();

    await storage.setTokens({ access: "access-token", refresh: "refresh-token" });

    expect(await storage.getAccessToken()).toBe("access-token");
    expect(await storage.getRefreshToken()).toBe("refresh-token");

    await storage.clear();

    expect(await storage.getAccessToken()).toBeNull();
    expect(await storage.getRefreshToken()).toBeNull();
  });
});
