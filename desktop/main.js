const { app, BrowserWindow, globalShortcut, Tray, Menu, nativeImage, ipcMain } = require('electron');
const path = require('path');

let mainWindow;
let tray = null;

// Window state persistence
const stateFile = path.join(app.getPath('userData'), 'window-state.json');
function loadWindowState() {
  try { return require(stateFile); } catch { return null; }
}
function saveWindowState() {
  if (!mainWindow) return;
  const bounds = mainWindow.getBounds();
  const fs = require('fs');
  fs.writeFileSync(stateFile, JSON.stringify({
    x: bounds.x, y: bounds.y,
    width: bounds.width, height: bounds.height,
    isMaximized: mainWindow.isMaximized(),
    isFullScreen: mainWindow.isFullScreen()
  }));
}

function createWindow() {
  const saved = loadWindowState();

  mainWindow = new BrowserWindow({
    width: saved?.width || 1920,
    height: saved?.height || 1080,
    x: saved?.x,
    y: saved?.y,
    minWidth: 1280,
    minHeight: 720,
    frame: false,
    transparent: false,
    backgroundColor: '#000a0f',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
    },
    icon: path.join(__dirname, 'icon.png'),
    title: 'ULTRON EMPIRE',
  });

  if (saved?.isMaximized) mainWindow.maximize();
  if (saved?.isFullScreen) mainWindow.setFullScreen(true);

  mainWindow.loadFile('index.html');

  // Build application menu
  const menuTemplate = [
    {
      label: 'File',
      submenu: [
        { label: 'Quit Ultron', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Toggle Fullscreen', accelerator: 'F11', click: () => mainWindow.setFullScreen(!mainWindow.isFullScreen()) },
        { label: 'Toggle DevTools', accelerator: 'F12', click: () => mainWindow.webContents.toggleDevTools() },
        { type: 'separator' },
        { role: 'reload' },
        { role: 'forceReload' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Ultron Empire',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About Ultron Empire',
              message: 'Ultron Empire v3.0.0',
              detail: 'AI-Powered Wealth Management OS\nBuilt with Electron + Claude API\n\npms sahi hai.'
            });
          }
        }
      ]
    }
  ];
  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  // F11 fullscreen toggle
  globalShortcut.register('F11', () => {
    mainWindow.setFullScreen(!mainWindow.isFullScreen());
  });

  // F12 DevTools toggle
  globalShortcut.register('F12', () => {
    mainWindow.webContents.toggleDevTools();
  });

  // Escape to exit fullscreen
  globalShortcut.register('Escape', () => {
    if (mainWindow.isFullScreen()) mainWindow.setFullScreen(false);
  });

  // Save window state on move/resize
  mainWindow.on('resize', saveWindowState);
  mainWindow.on('move', saveWindowState);
  mainWindow.on('close', saveWindowState);

  mainWindow.on('closed', () => { mainWindow = null; });
}

function createTray() {
  // Create a simple 16x16 tray icon (fallback if icon.png doesn't exist)
  let iconPath = path.join(__dirname, 'icon.png');
  let trayIcon;
  try {
    trayIcon = nativeImage.createFromPath(iconPath);
    if (trayIcon.isEmpty()) throw new Error('empty');
    trayIcon = trayIcon.resize({ width: 16, height: 16 });
  } catch {
    // Create a minimal fallback icon
    trayIcon = nativeImage.createEmpty();
  }

  tray = new Tray(trayIcon);
  tray.setToolTip('Ultron Empire v3.0');

  const contextMenu = Menu.buildFromTemplate([
    { label: 'Show Ultron', click: () => { mainWindow?.show(); mainWindow?.focus(); } },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() }
  ]);
  tray.setContextMenu(contextMenu);

  tray.on('double-click', () => {
    mainWindow?.show();
    mainWindow?.focus();
  });
}

// Auto-updater stub (activate when electron-updater is properly configured with a publish target)
function initAutoUpdater() {
  try {
    const { autoUpdater } = require('electron-updater');
    autoUpdater.logger = require('electron-log');
    autoUpdater.logger.transports.file.level = 'info';

    autoUpdater.on('update-available', () => {
      mainWindow?.webContents.send('update-available');
    });
    autoUpdater.on('update-downloaded', () => {
      mainWindow?.webContents.send('update-downloaded');
    });

    // Check for updates after launch
    autoUpdater.checkForUpdatesAndNotify().catch(() => {});
  } catch {
    // electron-updater not installed or not configured — skip silently
    console.log('[updater] electron-updater not available, skipping auto-update check.');
  }
}

app.whenReady().then(() => {
  createWindow();
  createTray();
  initAutoUpdater();
});

app.on('window-all-closed', () => app.quit());
app.on('activate', () => { if (!mainWindow) createWindow(); });
app.on('will-quit', () => globalShortcut.unregisterAll());
