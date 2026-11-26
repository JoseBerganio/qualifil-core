import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Button } from "./Button";

describe("Button", () => {
  it("renders its label", () => {
    render(<Button>Save changes</Button>);
    expect(screen.getByRole("button", { name: /save changes/i })).toBeInTheDocument();
  });

  it("applies the default variant classes", () => {
    render(<Button>Save</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-primary");
  });

  it("supports alternative variants and sizes", () => {
    render(
      <Button variant="outline" size="sm">
        Small outline
      </Button>,
    );
    const button = screen.getByRole("button");
    expect(button.className).toContain("border");
    expect(button.className).toContain("text-xs");
  });

  it("merges custom classes", () => {
    render(<Button className="mt-4">Styled</Button>);
    expect(screen.getByRole("button").className).toContain("mt-4");
  });

  it("calls the onClick handler", () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    fireEvent.click(screen.getByRole("button"));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
