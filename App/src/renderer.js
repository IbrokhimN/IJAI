async function renderSystemCard() {
  if (!window.ijai) return;

  const info = await window.ijai.getSystemInfo();
  const models = await window.ijai.getModels();

  const modelCount = models && models.models ? Object.keys(models.models).length : 0;

  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <div class="card-header">
      <div class="card-title">🖥 IJAI System Status</div>
      <button class="btn btn-outlined" id="ijai-repo-btn">GitHub</button>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-card-value">${info.platform} / ${info.arch}</div>
        <div class="stat-card-label">Platform</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-value">${info.cpus} cores</div>
        <div class="stat-card-label">CPU</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-value">${info.totalMemGB} GB</div>
        <div class="stat-card-label">RAM</div>
      </div>
      <div class="stat-card">
        <div class="stat-card-value">${modelCount}</div>
        <div class="stat-card-label">Registered models</div>
      </div>
    </div>
  `;

  document.getElementById("main").appendChild(card);

  const repoBtn = document.getElementById("ijai-repo-btn");
  if (repoBtn) {
    repoBtn.addEventListener("click", () => {
      window.ijai.openExternal("https://github.com/IbrokhimN/IJAI");
    });
  }
}

document.addEventListener("DOMContentLoaded", renderSystemCard);
