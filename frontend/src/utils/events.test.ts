import { describe, expect, it } from "vitest";

import {
  formatEventMetadata,
  formatEventType,
  formatSeverity,
} from "./events";

describe("formatEventType", () => {
  it("returns Spanish label for known event types", () => {
    expect(formatEventType("crowd_detected")).toBe("Aglomeración detectada");
    expect(formatEventType("vehicle_long_parking")).toBe(
      "Vehículo estacionado mucho tiempo",
    );
  });

  it("falls back to readable text for unknown types", () => {
    expect(formatEventType("custom_rule_event")).toBe("custom rule event");
  });
});

describe("formatSeverity", () => {
  it("returns Spanish severity labels", () => {
    expect(formatSeverity("high")).toBe("Alta");
    expect(formatSeverity("medium")).toBe("Media");
  });
});

describe("formatEventMetadata", () => {
  it("formats duration and object class in Spanish", () => {
    const rows = formatEventMetadata({
      duration_seconds: 120,
      object_class: "person",
      people_count: 8,
    });

    expect(rows.some((row) => row.label === "Duración" && row.value.includes("minuto"))).toBe(
      true,
    );
    expect(rows.some((row) => row.label === "Tipo de objeto" && row.value === "Persona")).toBe(
      true,
    );
  });
});
