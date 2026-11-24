import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AppStatusPage } from "./AppStatusPage";
import { getAppStatus } from "../lib/api/status";
import type { AppStatus } from "../lib/api/types";
import { I18nProvider } from "../lib/i18n";

vi.mock("../lib/api/status", () => ({
  getAppStatus: vi.fn(),
}));

const mockedGetAppStatus = vi.mocked(getAppStatus);

describe("AppStatusPage", () => {
  const healthyStatus: AppStatus = {
    status: "ok",
    environment: "development",
    version: "0.1.0",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it("renders the backend status, environment, and version", async () => {
    mockedGetAppStatus.mockResolvedValue(healthyStatus);
    render(
      <I18nProvider>
        <AppStatusPage />
      </I18nProvider>,
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(await screen.findByText("Operational")).toBeInTheDocument();
    expect(screen.getByText("development")).toBeInTheDocument();
    expect(screen.getByText("0.1.0")).toBeInTheDocument();
    expect(mockedGetAppStatus).toHaveBeenCalledTimes(1);
  });

  it("shows the localized error when the status request fails", async () => {
    mockedGetAppStatus.mockRejectedValue(new Error("connection refused"));
    render(
      <I18nProvider>
        <AppStatusPage />
      </I18nProvider>,
    );

    expect(
      await screen.findByText(/could not load application status/i),
    ).toBeInTheDocument();
  });
});
