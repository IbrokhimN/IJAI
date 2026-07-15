const { app, BrowserWindow, ipcMain, Menu } = require("electron");
const path = require("path");
const os = require("os");
const fs = require("fs");

const CONFIG_PATH = path.join(__dirname, "..", "IJAI-configs", "models.conf.json");

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: "#f5f5f5",
    autoHideMenuBar: true,
    icon: path.join(__dirname, "src", "assets", "IJAI-logo.png"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  });

  win.loadFile(path.join(__dirname, "src", "index.html"));

  if (!app.isPackaged && process.argv.includes("--dev")) {
    win.webContents.openDevTools();
  }

  win.on("unresponsive", () => {
    win.reload();
  });

  return win;
}

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);

  ipcMain.handle("ijai:get-system-info", () => ({
    platform: process.platform,
    arch: process.arch,
    appVersion: app.getVersion(),
    electronVersion: process.versions.electron,
    nodeVersion: process.versions.node,
    chromeVersion: process.versions.chrome,
    hostname: os.hostname(),
    cpus: os.cpus().length,
    totalMemGB: Math.round(os.totalmem() / 1024 / 1024 / 1024)
  }));

  ipcMain.handle("ijai:get-models", () => {
    try {
      const raw = fs.readFileSync(CONFIG_PATH, "utf-8");
      return JSON.parse(raw);
    } catch (err) {
      return { error: err.message };
    }
  });

  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
