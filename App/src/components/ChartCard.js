
export function ChartCard(label, value, sub) {
  return `
    <div class="card">
      <div class="label">${label}</div>
      <div class="value">${value}</div>
      <div class="small">${sub}</div>
    </div>
  `;
}
