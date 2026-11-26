import { useCallback, useEffect, useState } from "react";

import { Button } from "../components/Button";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { getAppStatus } from "../lib/api/status";
import type { AppStatus } from "../lib/api/types";
import { useTranslation } from "../lib/i18n";

export function AppStatusPage() {
  const [status, setStatus] = useState<AppStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const { t } = useTranslation();

  const refresh = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await getAppStatus();
      setStatus(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col px-4 py-16">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{t("appStatus.pageTitle")}</h1>
        <LanguageSwitcher />
      </header>

      <p className="mb-8 text-muted-foreground">{t("appStatus.pageDescription")}</p>

      {error ? (
        <div className="rounded-md border border-destructive bg-destructive/10 p-4">
          <p className="mb-4">{t("appStatus.error")}</p>
          <Button onClick={() => void refresh()}>{t("appStatus.retry")}</Button>
        </div>
      ) : loading ? (
        <p role="status">{t("appStatus.loading")}</p>
      ) : status ? (
        <dl className="rounded-md border bg-card p-4">
          <div className="flex gap-4 py-2">
            <dt className="w-28 text-muted-foreground">{t("appStatus.environment")}</dt>
            <dd data-testid="environment">{status.environment}</dd>
          </div>
          <div className="flex gap-4 py-2">
            <dt className="w-28 text-muted-foreground">{t("appStatus.version")}</dt>
            <dd data-testid="version">{status.version}</dd>
          </div>
          <div className="flex gap-4 py-2">
            <dt className="w-28 text-muted-foreground">{t("appStatus.statusLabel")}</dt>
            <dd data-testid="status" className="font-medium">
              {t(`appStatus.status.${status.status}`)}
            </dd>
          </div>
        </dl>
      ) : null}
    </main>
  );
}
