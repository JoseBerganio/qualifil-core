import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
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

export function translate(map: MessageMap, key: string): string {
  const value = key
    .split(".")
    .reduce<unknown>((acc, part) => (acc as Record<string, unknown> | undefined)?.[part], map);
  return typeof value === "string" ? value : key;
}

interface I18nContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: PropsWithChildren) {
  const [locale, setLocaleState] = useState<Locale>(DEFAULT_LOCALE);

  useEffect(() => {
    let active = true;
    AsyncStorage.getItem(STORAGE_KEY)
      .then((stored) => {
        if (active && isLocale(stored)) {
          setLocaleState(stored);
        }
      })
      .catch(() => {
        /* Preferences are optional; keep the default locale. */
      });
    return () => {
      active = false;
    };
  }, []);

  const setLocale = useCallback((next: Locale) => {
    if (!messages[next]) {
      return;
    }
    setLocaleState(next);
    AsyncStorage.setItem(STORAGE_KEY, next).catch(() => {
      /* Persistence is best-effort. */
    });
  }, []);

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale,
      t: (key) => translate(messages[locale], key),
    }),
    [locale, setLocale],
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
