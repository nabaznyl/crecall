"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const axios_1 = __importDefault(require("axios"));
const child_process_1 = require("child_process");
const util_1 = require("util");
const execAsync = (0, util_1.promisify)(child_process_1.exec);
let statusBarItem;
let autoClipTimer;
function activate(context) {
    console.log('Crecall extension activated');
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'crecall.showStatus';
    statusBarItem.text = '$(history) Crecall';
    statusBarItem.tooltip = 'Last clip: Never | Click for status';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    // Register commands
    context.subscriptions.push(vscode.commands.registerCommand('crecall.createClip', createClip), vscode.commands.registerCommand('crecall.addMemory', addMemory), vscode.commands.registerCommand('crecall.listClips', listClips), vscode.commands.registerCommand('crecall.listMemories', listMemories), vscode.commands.registerCommand('crecall.showStatus', showStatus));
    // Check API connection and update status
    updateStatusBar();
    setInterval(updateStatusBar, 60000); // Update every minute
    // Setup auto-clip if enabled
    const config = vscode.workspace.getConfiguration('crecall');
    if (config.get('enableAutoClip')) {
        setupAutoClip(config.get('autoClipInterval', 300000));
    }
    // Watch for config changes
    context.subscriptions.push(vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('crecall')) {
            const newConfig = vscode.workspace.getConfiguration('crecall');
            if (newConfig.get('enableAutoClip')) {
                setupAutoClip(newConfig.get('autoClipInterval', 300000));
            }
            else if (autoClipTimer) {
                clearInterval(autoClipTimer);
                autoClipTimer = undefined;
            }
        }
    }));
}
function setupAutoClip(interval) {
    if (autoClipTimer) {
        clearInterval(autoClipTimer);
    }
    autoClipTimer = setInterval(async () => {
        await createClipSilent();
    }, interval);
}
async function updateStatusBar() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const apiUrl = config.get('apiUrl', 'http://localhost:8000');
        const response = await axios_1.default.get(`${apiUrl}/health`, { timeout: 2000 });
        if (response.data.status === 'healthy') {
            // Get last clip time
            const clipsResponse = await axios_1.default.get(`${apiUrl}/api/clips/?limit=1`);
            if (clipsResponse.data && clipsResponse.data.length > 0) {
                const lastClip = clipsResponse.data[0];
                const clipTime = new Date(lastClip.created_at);
                const now = new Date();
                const diffMinutes = Math.floor((now.getTime() - clipTime.getTime()) / 60000);
                statusBarItem.text = `$(history) ${diffMinutes}m ago`;
                statusBarItem.tooltip = `Last clip: ${diffMinutes} minutes ago\\nClick for details`;
                statusBarItem.backgroundColor = undefined;
            }
            else {
                statusBarItem.text = '$(history) No clips';
                statusBarItem.tooltip = 'No clips yet';
            }
        }
    }
    catch (error) {
        statusBarItem.text = '$(warning) Crecall';
        statusBarItem.tooltip = 'API not connected. Check if backend is running.';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
}
async function createClip() {
    const note = await vscode.window.showInputBox({
        prompt: 'Clip note (optional)',
        placeHolder: 'e.g., "Before refactoring auth module"'
    });
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const cliPath = config.get('cliPath', 'crecall');
        const cmd = note ? `${cliPath} -c add "${note}"` : `${cliPath} -c add`;
        const { stdout, stderr } = await execAsync(cmd);
        if (stderr) {
            vscode.window.showErrorMessage(`Crecall: ${stderr}`);
        }
        else {
            vscode.window.showInformationMessage('✓ Clip created');
            updateStatusBar();
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to create clip: ${error.message}`);
    }
}
async function createClipSilent() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const cliPath = config.get('cliPath', 'crecall');
        await execAsync(`${cliPath} -c add "Auto-clip from VS Code"`);
        updateStatusBar();
    }
    catch (error) {
        console.error('Auto-clip failed:', error);
    }
}
async function addMemory() {
    const memory = await vscode.window.showInputBox({
        prompt: 'Enter memory text',
        placeHolder: 'Important note to remember...'
    });
    if (!memory) {
        return;
    }
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const cliPath = config.get('cliPath', 'crecall');
        const { stdout, stderr } = await execAsync(`${cliPath} -m add "${memory}"`);
        if (stderr) {
            vscode.window.showErrorMessage(`Crecall: ${stderr}`);
        }
        else {
            vscode.window.showInformationMessage('✓ Memory added');
        }
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to add memory: ${error.message}`);
    }
}
async function listClips() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const cliPath = config.get('cliPath', 'crecall');
        const { stdout } = await execAsync(`${cliPath} -c list 10`);
        const channel = vscode.window.createOutputChannel('Crecall Clips');
        channel.clear();
        channel.appendLine(stdout);
        channel.show();
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to list clips: ${error.message}`);
    }
}
async function listMemories() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const cliPath = config.get('cliPath', 'crecall');
        const { stdout } = await execAsync(`${cliPath} -m list`);
        const channel = vscode.window.createOutputChannel('Crecall Memories');
        channel.clear();
        channel.appendLine(stdout);
        channel.show();
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to list memories: ${error.message}`);
    }
}
async function showStatus() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const apiUrl = config.get('apiUrl', 'http://localhost:8000');
        const healthResponse = await axios_1.default.get(`${apiUrl}/health`);
        const clipsResponse = await axios_1.default.get(`${apiUrl}/api/clips/?limit=1`);
        const sessionsResponse = await axios_1.default.get(`${apiUrl}/api/sessions/`);
        const memoriesResponse = await axios_1.default.get(`${apiUrl}/api/memories/`);
        const status = [
            '📊 Crecall Status',
            '',
            `API: ${healthResponse.data.status}`,
            `Total Sessions: ${sessionsResponse.data.length}`,
            `Total Clips: ${clipsResponse.data.length > 0 ? 'Available' : '0'}`,
            `Total Memories: ${memoriesResponse.data.length}`,
            '',
            'Recent Clip:',
        ];
        if (clipsResponse.data && clipsResponse.data.length > 0) {
            const lastClip = clipsResponse.data[0];
            status.push(`  ID: ${lastClip.clip_id}`);
            status.push(`  Created: ${lastClip.created_at}`);
        }
        else {
            status.push('  No clips yet');
        }
        const channel = vscode.window.createOutputChannel('Crecall Status');
        channel.clear();
        channel.appendLine(status.join('\\n'));
        channel.show();
    }
    catch (error) {
        vscode.window.showErrorMessage(`Failed to get status: ${error.message}`);
    }
}
function deactivate() {
    if (autoClipTimer) {
        clearInterval(autoClipTimer);
    }
}
//# sourceMappingURL=extension.js.map