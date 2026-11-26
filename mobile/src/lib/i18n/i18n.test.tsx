import { fireEvent, render, screen, waitFor } from "@testing-library/react-native";
import { Pressable, Text, View } from "react-native";

import { I18nProvider, useTranslation } from "./index";

function Probe() {
  const { locale, setLocale, t } = useTranslation();

  return (
    <View>
      <Text>{locale}</Text>
      <Text>{t("connectivity.title")}</Text>
      <Pressable onPress={() => setLocale("fil")}>
        <Text>switch</Text>
      </Pressable>
    </View>
  );
}

describe("I18nProvider", () => {
  it("defaults to English and switches to Filipino", async () => {
    await render(
      <I18nProvider>
        <Probe />
      </I18nProvider>,
    );

    await waitFor(() => expect(screen.getByText("en")).toBeTruthy());
    expect(screen.getByText("Backend connectivity")).toBeTruthy();

    await fireEvent.press(screen.getByText("switch"));

    await waitFor(() => expect(screen.getByText("fil")).toBeTruthy());
    expect(screen.getByText("Koneksyon sa backend")).toBeTruthy();
  });
});
