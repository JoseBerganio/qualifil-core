import {
  Pressable,
  StyleSheet,
  Text,
  type PressableProps,
  type StyleProp,
  type ViewStyle,
} from "react-native";

import { colors, radius, spacing, typography } from "../theme";

export interface ButtonProps extends Omit<PressableProps, "children" | "style"> {
  label: string;
  variant?: "primary" | "outline";
  style?: StyleProp<ViewStyle>;
}

export function Button({ label, variant = "primary", style, disabled, ...props }: ButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      style={({ pressed }) => [
        styles.base,
        variant === "primary" ? styles.primary : styles.outline,
        pressed && !disabled ? styles.pressed : null,
        disabled ? styles.disabled : null,
        style,
      ]}
      {...props}
    >
      <Text
        style={[styles.label, variant === "primary" ? styles.primaryLabel : styles.outlineLabel]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: 46,
    borderRadius: radius.md,
    paddingHorizontal: spacing.lg,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
  },
  primary: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  outline: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
  },
  pressed: {
    opacity: 0.8,
  },
  disabled: {
    opacity: 0.5,
  },
  label: {
    fontSize: typography.body,
    fontWeight: "600",
  },
  primaryLabel: {
    color: colors.primaryText,
  },
  outlineLabel: {
    color: colors.primary,
  },
});
