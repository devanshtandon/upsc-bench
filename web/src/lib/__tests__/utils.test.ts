import { describe, it, expect } from "vitest";
import { shuffle, getRankClass } from "../utils";

// ── shuffle ──────────────────────────────────────────────────

describe("shuffle", () => {
  it("returns a new array (original unchanged)", () => {
    const original = [1, 2, 3, 4, 5];
    const copy = [...original];
    const result = shuffle(original);
    expect(original).toEqual(copy); // original untouched
    expect(result).not.toBe(original); // different reference
  });

  it("preserves all elements", () => {
    const arr = [10, 20, 30, 40, 50];
    const result = shuffle(arr);
    expect(result).toHaveLength(arr.length);
    expect(result.sort((a, b) => a - b)).toEqual(arr.sort((a, b) => a - b));
  });

  it("handles empty array", () => {
    expect(shuffle([])).toEqual([]);
  });

  it("handles single element", () => {
    expect(shuffle([1])).toEqual([1]);
  });
});

// ── getRankClass ─────────────────────────────────────────────

describe("getRankClass", () => {
  it("returns gold for rank 1", () => {
    expect(getRankClass(1)).toBe("gold");
  });

  it("returns silver for rank 2", () => {
    expect(getRankClass(2)).toBe("silver");
  });

  it("returns bronze for rank 3", () => {
    expect(getRankClass(3)).toBe("bronze");
  });

  it("returns default for rank 99", () => {
    expect(getRankClass(99)).toBe("default");
  });
});
