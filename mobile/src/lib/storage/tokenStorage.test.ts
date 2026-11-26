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
    const storage = createMemoryTokenStorage("existing");
    expect(await storage.getAccessToken()).toBe("existing");
  });
});
