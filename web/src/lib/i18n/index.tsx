import {
  createContext,
  useContext,
  useMemo,
  useState,
  type PropsWithChildren,
} from "react";

import en from "./locales/en.json";
import fil from "./locales/fil.json";
import hil from "./locales/hil.json";

export type Locale = "en" | "fil" | "hil";

export type MessageMap = typeof en;

const messages: Record<Locale, MessageMap> = { en, fil, hil };
const locales: Locale[] = ["en", "fil", "hil"];
const DEFAULT_LOCALE: Locale = "en";
const STORAGE_KEY = "qualifil.locale";

function isLocale(value: unknown): value is Locale {
  return typeof value === "string" && (locales as string[]).includes(value);
}

function readStoredLocale(): Locale {
  if (typeof window === "undefined") {
    return DEFAULT_LOCALE;
  }
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return isLocale(stored) ? stored : DEFAULT_LOCALE;
  } catch {
    return DEFAULT_LOCALE;
  }
}

function writeStoredLocale(locale: Locale): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(STORAGE_KEY, locale);
  } catch {
    /* Local storage can be unavailable; keep the in-memory locale. */
  }
}

function translate(map: MessageMap, key: string): string {
  const value = key.split(".").reduce<unknown>(
    (acc, part) => (acc as Record<string, unknown> | undefined)?.[part],
    map,
  );
  return typeof value === "string" ? value : key;
}

interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: PropsWithChildren) {
  const [locale, setLocaleState] = useState<Locale>(readStoredLocale);

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale: (next) => {
        if (messages[next]) {
          setLocaleState(next);
          writeStoredLocale(next);
        }
      },
      t: (key) => translate(messages[locale], key),
    }),
    [locale],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useTranslation(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useTranslation must be used within an I18nProvider");
  }
  return context;
}
