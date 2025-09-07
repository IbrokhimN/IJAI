
export function Sidebar() {
  return `
    <aside class="sidebar">
      <div class="brand">
        <img src="assets/icons/IJAI-logo.png" alt="logo" style="height:20px">
        Nexus Insights
      </div>
      <nav class="nav" id="nav">
        <button class="active" data-page="overview">Overview</button>
        <button data-page="history">Requests</button>
        <button data-page="resources">Resources</button>
        <button data-page="privacy">Privacy</button>
        <button data-page="settings">Settings</button>
      </nav>
      <div class="footer">Version <strong>0.9</strong> · Local demo</div>
    </aside>
  `;
}
