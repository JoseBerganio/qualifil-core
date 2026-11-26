import { Pressable, StyleSheet, Text, View } from "react-native";

import { useTranslation, type Locale } from "../lib/i18n";
import { colors, radius, spacing, typography } from "../theme";

const locales: Locale[] = ["en", "fil", "hil"];

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useTranslation();

  return (
    <View
      style={styles.row}
      accessibilityRole="radiogroup"
      accessibilityLabel={t("language-group-label")}
    >
      {locales.map((code) => {
        const active = locale === code;
        return (
          <Pressable
            key={code}
            accessibilityRole="radio"
            accessibilityState={{ selected: active }}
            onPress={() => setLocale(code)}
            style={[styles.option, active ? styles.active : null]}
          >
            <Text style={[styles.label, active ? styles.activeLabel : null]}>
              {t(`language.${code}`)}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    gap: spacing.sm,
    flexWrap: "wrap",
  },
  option: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
  },
  active: {
    borderColor: colors.primary,
    backgroundColor: colors.accent,
  },
  label: {
    color: colors.mutedText,
    fontSize: typography.body,
    fontWeight: "500",
  },
  activeLabel: {
    color: colors.primary,
    fontWeight: "700",
  },
});
