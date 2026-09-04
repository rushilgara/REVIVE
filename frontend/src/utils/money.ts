/**
 * Central frontend utility for formatted Indian Rupee (INR) display.
 * Strictly operates on integer minor units (paise).
 */

export function formatINR(amountMinor: number): string {
  if (amountMinor === undefined || amountMinor === null || isNaN(amountMinor)) {
    return '₹0';
  }
  const rupees = amountMinor / 100;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: rupees % 1 === 0 ? 0 : 2,
  }).format(rupees);
}

export function minorToRupees(amountMinor: number): number {
  return (amountMinor || 0) / 100;
}

export function rupeesToMinor(rupees: number): number {
  return Math.round((rupees || 0) * 100);
}

export function formatPercentage(value: number): string {
  if (value === undefined || value === null || isNaN(value)) {
    return '0.0%';
  }
  return `${value.toFixed(1)}%`;
}
