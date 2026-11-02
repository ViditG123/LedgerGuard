import test from "node:test";
import assert from "node:assert/strict";
import { toCents, money } from "../src/ledger.js";

test("converts exact decimal amounts to integer cents", () => {
  assert.equal(toCents("100.00"), 10000);
  assert.equal(toCents("-15.25"), -1525);
  assert.equal(toCents("0.01"), 1);
  assert.equal(money(8475), "84.75");
});
test("rejects excess precision and non-decimal values", () => {
  assert.throws(() => toCents("1.234"));
  assert.throws(() => toCents("1e3"));
  assert.throws(() => toCents(12));
});
