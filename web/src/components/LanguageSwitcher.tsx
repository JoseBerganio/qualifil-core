import { clsx } from "clsx";

import { useTranslation } from "../lib/i18n";

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useTranslation();

  return (
    <div
      className="flex items-center gap-1 text-sm"
      role="group"
      aria-label={t("language-group-label")}
    >
      {(["en", "fil", "hil"] as const).map((code) => (
        <button
          key={code}
          type="button"
          aria-pressed={locale === code}
          onClick={() => setLocale(code)}
          className={clsx(
            "rounded-md px-2 py-1",
            locale === code
              ? "font-semibold underline"
              : "text-muted-foreground",
          )}
        >
          {t(`language.${code}`)}
        </button>
      ))}
    </div>
  );
}
