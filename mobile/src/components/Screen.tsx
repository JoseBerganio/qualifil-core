import type { PropsWithChildren } from "react";
import { ScrollView, StyleSheet, View } from "react-native";

import { colors, spacing } from "../theme";

export function Screen({ children }: PropsWithChildren) {
  return (
    <View style={styles.root}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {children}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.lg,
    gap: spacing.md,
  },
});
