import { describe, expect, it, jest } from "@jest/globals";
import { fireEvent, render, screen } from "@testing-library/react-native";

import { Button } from "./Button";

describe("Button", () => {
  it("renders its label and calls onPress", async () => {
    const onPress = jest.fn();

    await render(<Button label="Try again" onPress={onPress} />);
    await fireEvent.press(screen.getByText("Try again"));

    expect(onPress).toHaveBeenCalledTimes(1);
  });

  it("does not call onPress when disabled", async () => {
    const onPress = jest.fn();

    await render(<Button label="Try again" onPress={onPress} disabled />);
    await fireEvent.press(screen.getByText("Try again"));

    expect(onPress).not.toHaveBeenCalled();
  });
});
