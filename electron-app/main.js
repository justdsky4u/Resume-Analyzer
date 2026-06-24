const { app, BrowserWindow } = require('electron')
const path = require('path')

function createWindow() {
    const win = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
        }
    })

    // Support dev server (ELECTRON_DEV_URL) or production build
    const devUrl = process.env.ELECTRON_DEV_URL || 'http://127.0.0.1:5173'
    if (process.env.ELECTRON_PROD === '1') {
        // load built index.html from frontend dist
        const indexPath = path.join(__dirname, '..', 'app-frontend', 'dist', 'index.html')
        win.loadFile(indexPath)
    } else {
        win.loadURL(devUrl)
    }
}

app.whenReady().then(createWindow)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit()
})
