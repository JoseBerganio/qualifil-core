import type { NativeStackScreenProps } from "@react-navigation/native-stack";
import { fireEvent, render, screen } from "@testing-library/react-native";

import type { RootStackParamList } from "../app/navigation";
import { getAppStatus } from "../lib/api/status";
import { I18nProvider } from "../lib/i18n";
import { ConnectivityScreen } from "./ConnectivityScreen";

jest.mock("../lib/api/status", () => ({
  getAppStatus: jest.fn(),
}));

const mockedGetAppStatus = getAppStatus as jest.MockedFunction<typeof getAppStatus>;

type Navigation = NativeStackScreenProps<RootStackParamList, "Connectivity">["navigation"];

const navigation = { navigate: jest.fn() } as unknown as Navigation;
const route = { key: "Connectivity", name: "Connectivity" } as const;

function renderScreen() {
  return render(
    <I18nProvider>
      <ConnectivityScreen navigation={navigation} route={route as never} />
    </I18nProvider>,
  );
}

describe("ConnectivityScreen", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("shows a loading state and then the backend status", async () => {
    let resolveStatus!: (value: { status: string; environment: string; version: string }) => void;
    mockedGetAppStatus.mockReturnValue(
      new Promise((resolve) => {
        resolveStatus = resolve;
      }),
    );

    await renderScreen();

    expect(screen.getByText("Checking the backend...")).toBeTruthy();

    resolveStatus({
      status: "ok",
      environment: "development",
      version: "0.1.0",
    });

    expect(await screen.findByText("Operational")).toBeTruthy();
    expect(screen.getByText("development")).toBeTruthy();
    expect(screen.getByText("0.1.0")).toBeTruthy();
  });

  it("shows a localized error when the request fails", async () => {
    mockedGetAppStatus.mockRejectedValue(new Error("connection refused"));

    await renderScreen();

    expect(await screen.findByText("Could not reach the backend")).toBeTruthy();
  });

  it("navigates to the settings screen", async () => {
    mockedGetAppStatus.mockResolvedValue({
      status: "ok",
      environment: "development",
      version: "0.1.0",
    });

    await renderScreen();
    await screen.findByText("Operational");

    await fireEvent.press(screen.getByText("Language settings"));

    expect(navigation.navigate).toHaveBeenCalledWith("Settings");
  });
});
