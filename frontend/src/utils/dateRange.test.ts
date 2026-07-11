import { describe, expect, it } from "vitest";

import { getDateRangeParams } from "./dateRange";

const fixedNow = new Date("2026-07-11T15:30:00");

describe("getDateRangeParams", () => {
  it("returns local day bounds for today", () => {
    const range = getDateRangeParams("today", undefined, undefined, fixedNow);
    expect(range.start_date).toBe(new Date("2026-07-11T00:00:00").toISOString());
    expect(range.end_date).toBe(new Date("2026-07-11T23:59:59.999").toISOString());
  });

  it("returns yesterday bounds", () => {
    const range = getDateRangeParams("yesterday", undefined, undefined, fixedNow);
    expect(range.start_date).toBe(new Date("2026-07-10T00:00:00").toISOString());
    expect(range.end_date).toBe(new Date("2026-07-10T23:59:59.999").toISOString());
  });

  it("returns last 7 days including today", () => {
    const range = getDateRangeParams("7d", undefined, undefined, fixedNow);
    expect(range.start_date).toBe(new Date("2026-07-05T00:00:00").toISOString());
    expect(range.end_date).toBe(new Date("2026-07-11T23:59:59.999").toISOString());
  });

  it("returns empty params for all", () => {
    expect(getDateRangeParams("all")).toEqual({});
  });

  it("returns custom range when both dates are valid", () => {
    const range = getDateRangeParams("custom", "2026-07-01", "2026-07-05", fixedNow);
    expect(range.start_date).toBe(new Date("2026-07-01T00:00:00").toISOString());
    expect(range.end_date).toBe(new Date("2026-07-05T23:59:59.999").toISOString());
  });

  it("returns empty params for invalid custom range", () => {
    expect(getDateRangeParams("custom", "2026-07-05", "2026-07-01", fixedNow)).toEqual({});
    expect(getDateRangeParams("custom", "", "2026-07-01", fixedNow)).toEqual({});
  });
});
