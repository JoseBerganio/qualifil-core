import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, beforeEach } from "vitest";

import { I18nProvider, useTranslation } from "./index";

function Probe() {
  const { locale, setLocale, t } = useTranslation();
  return (
    <div>
      <span data-testid="locale">{locale}</span>
      <span data-testid="pageTitle">{t("appStatus.pageTitle")}</span>
      <span data-testid="environment">{t("appStatus.environment")}</span>
      <button type="button" onClick={() => setLocale("fil")}>
        Switch
      </button>
    </div>
  );
}

describe("i18n", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("defaults to English when no locale is stored", () => {
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByTestId("locale")).toHaveTextContent("en");
    expect(screen.getByTestId("pageTitle")).toHaveTextContent("Application status");
  });

  it("uses the stored locale", () => {
    window.localStorage.setItem("qualifil.locale", "hil");
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByTestId("locale")).toHaveTextContent("hil");
  });

  it("switches to a new locale and persists it", () => {
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    fireEvent.click(screen.getByRole("button", { name: "Switch" }));
    expect(screen.getByTestId("locale")).toHaveTextContent("fil");
    expect(screen.getByTestId("pageTitle")).toHaveTextContent("Katayuan ng application");
    expect(window.localStorage.getItem("qualifil.locale")).toBe("fil");
  });

  it("ignores an unknown stored locale", () => {
    window.localStorage.setItem("qualifil.locale", "zz");
    render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );
    expect(screen.getByTestId("locale")).toHaveTextContent("en");
  });
});
