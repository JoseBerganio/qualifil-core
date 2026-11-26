import { StyleSheet, Text, View } from "react-native";

import { colors, radius, spacing, typography } from "../theme";

export interface StatusRow {
  label: string;
  value: string;
  testID?: string;
}

export interface StatusCardProps {
  rows: StatusRow[];
  tone?: "default" | "warning";
}

export function StatusCard({ rows, tone = "default" }: StatusCardProps) {
  return (
    <View style={[styles.card, tone === "warning" ? styles.warning : null]} testID="status-card">
      {rows.map((row) => (
        <View key={row.label} style={styles.row}>
          <Text style={styles.label}>{row.label}</Text>
          <Text style={styles.value} testID={row.testID}>
            {row.value}
          </Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: spacing.md,
    gap: spacing.sm,
  },
  warning: {
    borderColor: colors.warning,
    backgroundColor: "#FFFBEB",
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: spacing.md,
  },
  label: {
    color: colors.mutedText,
    fontSize: typography.body,
  },
  value: {
    color: colors.text,
    fontSize: typography.body,
    fontWeight: "600",
    flexShrink: 1,
    textAlign: "right",
  },
});
