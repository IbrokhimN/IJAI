const { contextBridge, ipcRenderer, shell } = require("electron");

contextBridge.exposeInMainWorld("ijai", {
  getSystemInfo: () => ipcRenderer.invoke("ijai:get-system-info"),
  getModels: () => ipcRenderer.invoke("ijai:get-models"),
  openExternal: (url) => shell.openExternal(url)
});
