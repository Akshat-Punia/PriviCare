/**
 * HealthGuard AI — Electron Preload Script.
 * Secure context isolation bridge.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('healthGuardDesktop', {
  platform: process.platform,
  isElectron: true,
  appVersion: '1.0.0',
});
