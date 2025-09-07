
export function DataTable() {
  return `
    <div class="panel">
      <h3>Recent queries</h3>
      <div class="searchline">
        <input type="search" id="qSearch" placeholder="Search queries..." />
        <select id="filterModel">
          <option value="">All models</option>
          <option>gpt-local-1</option>
          <option>gpt-2mini</option>
        </select>
        <button class="btn ghost" id="anonToggle">Anonymize: OFF</button>
      </div>
      <div style="max-height:260px;overflow:auto">
        <table id="historyTable">
          <thead><tr><th>Time</th><th>Client</th><th>Query</th><th>Latency</th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
  `;
}
