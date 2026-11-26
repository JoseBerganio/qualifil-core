import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useCallback, useEffect, useRef, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import type { RootStackParamList } from "../app/navigation";
import { Button } from "../components/Button";
import { Screen } from "../components/Screen";
import { StatusCard } from "../components/StatusCard";
import { getAppStatus } from "../lib/api/status";
import type { AppStatus } from "../lib/api/types";
import { useTranslation } from "../lib/i18n";
import { colors, radius, spacing, typography } from "../theme";

type Props = NativeStackScreenProps<RootStackParamList, "Connectivity">;

export function ConnectivityScreen({ navigation }: Props) {
  const [status, setStatus] = useState<AppStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const mounted = useRef(true);
  const { t } = useTranslation();

  const load = useCallback(async () => {
    try {
      const nextStatus = await getAppStatus();
      if (mounted.current) {
        setStatus(nextStatus);
        setError(null);
      }
    } catch (err) {
      if (mounted.current) {
        setError(err instanceof Error ? err.message : String(err));
      }
    }
  }, []);

  useEffect(() => {
    mounted.current = true;
    // Initial fetch: state updates happen after the awaited request, so this
    // does not cause a synchronous cascading render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load().finally(() => {
      if (mounted.current) {
        setLoading(false);
      }
    });
    return () => {
      mounted.current = false;
    };
  }, [load]);

  const retry = useCallback(() => {
    setError(null);
    setLoading(true);
    void load().finally(() => {
      if (mounted.current) {
        setLoading(false);
      }
    });
  }, [load]);

  return (
    <Screen>
      <Text style={styles.title}>{t("connectivity.title")}</Text>
      <Text style={styles.description}>{t("connectivity.description")}</Text>

      {error ? (
        <View style={styles.errorBox}>
          <Text style={styles.errorText}>{t("connectivity.error")}</Text>
          <Text style={styles.errorDetail}>{error}</Text>
        </View>
      ) : loading ? (
        <View style={styles.loadingBox}>
          <ActivityIndicator
            color={colors.primary}
            accessibilityLabel={t("connectivity.loading")}
          />
          <Text style={styles.loadingText}>{t("connectivity.loading")}</Text>
        </View>
      ) : status ? (
        <StatusCard
          tone={status.status === "ok" ? "default" : "warning"}
          rows={[
            {
              label: t("connectivity.statusLabel"),
              value: t(`connectivity.status.${status.status}`),
              testID: "connectivity-status",
            },
            {
              label: t("connectivity.environment"),
              value: status.environment,
              testID: "connectivity-environment",
            },
            {
              label: t("connectivity.version"),
              value: status.version,
              testID: "connectivity-version",
            },
          ]}
        />
      ) : null}

      <View style={styles.actions}>
        <Button label={t("connectivity.retry")} onPress={retry} disabled={loading} />
        <Button
          label={t("connectivity.openSettings")}
          variant="outline"
          onPress={() => navigation.navigate("Settings")}
        />
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
  loadingBox: {
    flexDirection: "row",
    alignItems: "center",
    gap: spacing.sm,
    paddingVertical: spacing.md,
  },
  loadingText: {
    color: colors.mutedText,
    fontSize: typography.body,
  },
  errorBox: {
    borderWidth: 1,
    borderColor: colors.danger,
    backgroundColor: colors.dangerSurface,
    borderRadius: radius.lg,
    padding: spacing.md,
    gap: spacing.xs,
  },
  errorText: {
    color: colors.danger,
    fontSize: typography.subtitle,
    fontWeight: "600",
  },
  errorDetail: {
    color: colors.danger,
    fontSize: typography.caption,
  },
  actions: {
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
});
