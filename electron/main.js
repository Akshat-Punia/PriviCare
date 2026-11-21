/**
 * HealthGuard AI — Electron Native Desktop Application Wrapper.
 *
 * Provides a dedicated native Windows application window (similar to Microsoft Word / Teams)
 * with system tray, custom title bar, native dialogs, and offline FastAPI backend integration.
 */

const { app, BrowserWindow, Menu, Tray, nativeImage, shell, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow = null;
let backendProcess = null;
let tray = null;

const PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${PORT}`;
const FRONTEND_URL = 'http://localhost:3000';

function startBackend() {
  const isDev = !app.isPackaged;
  const projectRoot = isDev ? path.join(__dirname, '..') : process.resourcesPath;
  const exePath = path.join(projectRoot, 'dist', 'HealthGuard-AI.exe');

  try {
    // If packaged exe exists, launch it as a child process
    if (require('fs').existsSync(exePath)) {
      backendProcess = spawn(exePath, [], { detached: false });
      backendProcess.stdout?.on('data', (data) => console.log(`[Backend] ${data}`));
      backendProcess.stderr?.on('data', (data) => console.error(`[Backend Err] ${data}`));
    }
  } catch (err) {
    console.warn('[Electron] Could not spawn standalone backend:', err.message);
  }
}

function createWindow() {
  const iconPath = path.join(__dirname, '..', 'assets', 'icon.png');

  mainWindow = new BrowserWindow({
    width: 1280,
    height: 840,
    minWidth: 960,
    minHeight: 640,
    title: 'HealthGuard AI — Healthcare Zero-Trust Clinical Workstation',
    icon: iconPath,
    backgroundColor: '#0b0f19',
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });

  // Try Next.js portal first, fallback to embedded backend SPA
  const checkUrl = async (url) => {
    try {
      const http = require('http');
      return new Promise((resolve) => {
        const req = http.get(url, (res) => resolve(res.statusCode === 200));
        req.on('error', () => resolve(false));
        req.setTimeout(800, () => resolve(false));
      });
    } catch {
      return false;
    }
  };

  setTimeout(async () => {
    const isFrontendUp = await checkUrl(FRONTEND_URL);
    const target = isFrontendUp ? FRONTEND_URL : BACKEND_URL;
    mainWindow.loadURL(target).catch(() => {
      mainWindow.loadURL(BACKEND_URL);
    });
  }, 1200);

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http:') || url.startsWith('https:')) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
