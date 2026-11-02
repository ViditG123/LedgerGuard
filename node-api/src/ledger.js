export function toCents(amount) {
  if (typeof amount !== "string" || !/^-?\d+(\.\d{1,2})?$/.test(amount)) {
    throw new Error("Amount must be a decimal string with at most two places");
  }
  const negative = amount.startsWith("-");
  const normalized = negative ? amount.slice(1) : amount;
  const [whole, fraction = ""] = normalized.split(".");
  const cents = Number(whole) * 100 + Number(fraction.padEnd(2, "0"));
  if (!Number.isSafeInteger(cents) || cents > 1e12) throw new Error("Amount out of range");
  return negative ? -cents : cents;
}
export function money(cents) {
  return (cents / 100).toFixed(2);
}
