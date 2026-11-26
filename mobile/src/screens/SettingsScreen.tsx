import { StyleSheet, Text, View } from "react-native";

import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { Screen } from "../components/Screen";
import { useTranslation } from "../lib/i18n";
import { colors, radius, spacing, typography } from "../theme";

export function SettingsScreen() {
  const { t } = useTranslation();

  return (
    <Screen>
      <Text style={styles.title}>{t("settings.title")}</Text>
      <Text style={styles.description}>{t("settings.description")}</Text>
      <LanguageSwitcher />
      <View style={styles.note}>
        <Text style={styles.noteText}>{t("settings.storageNote")}</Text>
      </View>
    </Screen>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: typography.title,
    fontWeight: "700",
    color: colors.text,
  },
  description: {
    fontSize: typography.body,
    color: colors.mutedText,
    lineHeight: 22,
  },
  note: {
    marginTop: spacing.md,
    padding: spacing.md,
    borderRadius: radius.md,
    backgroundColor: colors.accent,
  },
  noteText: {
    color: colors.mutedText,
    fontSize: typography.caption,
    lineHeight: 18,
  },
});
