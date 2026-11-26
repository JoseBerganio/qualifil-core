import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";

import { I18nProvider, useTranslation } from "../lib/i18n";
import { ConnectivityScreen } from "../screens/ConnectivityScreen";
import { SettingsScreen } from "../screens/SettingsScreen";
import { colors } from "../theme";
import type { RootStackParamList } from "./navigation";

const Stack = createNativeStackNavigator<RootStackParamList>();

function RootNavigator() {
  const { t } = useTranslation();

  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: colors.surface },
          headerTintColor: colors.primary,
          headerTitleStyle: { fontWeight: "600" },
        }}
      >
        <Stack.Screen
          name="Connectivity"
          component={ConnectivityScreen}
          options={{ title: t("nav.connectivity") }}
        />
        <Stack.Screen
          name="Settings"
          component={SettingsScreen}
          options={{ title: t("nav.settings") }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <StatusBar style="dark" />
      <RootNavigator />
    </I18nProvider>
  );
}
