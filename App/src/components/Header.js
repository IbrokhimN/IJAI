
export function Header() {
  return `
    <div class="top">
      <div>
        <h2 style="margin:0">AI on this PC — Live</h2>
        <div class="small">Realtime overview of usage, requests and past activity</div>
      </div>
      <div class="controls">
        <div class="stat-row">
          <div class="chip" id="uptimeChip">Uptime: 0h</div>
          <div class="chip" id="reqChip">Requests: 0</div>
        </div>
        <button class="btn" id="exportCsv">Export CSV</button>
        <button class="btn ghost" id="simulate">Simulate +</button>
      </div>
    </div>
  `;
}
