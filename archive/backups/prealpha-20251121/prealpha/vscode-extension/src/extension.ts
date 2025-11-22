import * as vscode from 'vscode';
import axios from 'axios';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

let statusBarItem: vscode.StatusBarItem;
let autoClipTimer: NodeJS.Timeout | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Crecall extension activated');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'crecall.showStatus';
    statusBarItem.text = '$(history) Crecall';
    statusBarItem.tooltip = 'Last clip: Never | Click for status';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('crecall.createClip', createClip),
        vscode.commands.registerCommand('crecall.addMemory', addMemory),
        vscode.commands.registerCommand('crecall.listClips', listClips),
        vscode.commands.registerCommand('crecall.listMemories', listMemories),
        vscode.commands.registerCommand('crecall.showStatus', showStatus)
    );

    // Check API connection and update status
    updateStatusBar();
    setInterval(updateStatusBar, 60000); // Update every minute

    // Setup auto-clip if enabled
    const config = vscode.workspace.getConfiguration('crecall');
    if (config.get('enableAutoClip')) {
        setupAutoClip(config.get('autoClipInterval', 300000));
    }

    // Watch for config changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('crecall')) {
                const newConfig = vscode.workspace.getConfiguration('crecall');
                if (newConfig.get('enableAutoClip')) {
                    setupAutoClip(newConfig.get('autoClipInterval', 300000));
                } else if (autoClipTimer) {
                    clearInterval(autoClipTimer);
                    autoClipTimer = undefined;
                }
            }
        })
    );
}

function setupAutoClip(interval: number) {
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
        
        const response = await axios.get(`${apiUrl}/health`, { timeout: 2000 });
        
        if (response.data.status === 'healthy') {
            // Get last clip time
            const clipsResponse = await axios.get(`${apiUrl}/api/clips/?limit=1`);
            if (clipsResponse.data && clipsResponse.data.length > 0) {
                const lastClip = clipsResponse.data[0];
                const clipTime = new Date(lastClip.created_at);
                const now = new Date();
                const diffMinutes = Math.floor((now.getTime() - clipTime.getTime()) / 60000);
                
                statusBarItem.text = `$(history) ${diffMinutes}m ago`;
                statusBarItem.tooltip = `Last clip: ${diffMinutes} minutes ago\\nClick for details`;
                statusBarItem.backgroundColor = undefined;
            } else {
                statusBarItem.text = '$(history) No clips';
                statusBarItem.tooltip = 'No clips yet';
            }
        }
    } catch (error) {
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
        } else {
            vscode.window.showInformationMessage('✓ Clip created');
            updateStatusBar();
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create clip: ${error.message}`);
    }
}

async function createClipSilent() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const cliPath = config.get('cliPath', 'crecall');
        await execAsync(`${cliPath} -c add "Auto-clip from VS Code"`);
        updateStatusBar();
    } catch (error) {
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
        } else {
            vscode.window.showInformationMessage('✓ Memory added');
        }
    } catch (error: any) {
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
    } catch (error: any) {
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
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list memories: ${error.message}`);
    }
}

async function showStatus() {
    try {
        const config = vscode.workspace.getConfiguration('crecall');
        const apiUrl = config.get('apiUrl', 'http://localhost:8000');
        
        const healthResponse = await axios.get(`${apiUrl}/health`);
        const clipsResponse = await axios.get(`${apiUrl}/api/clips/?limit=1`);
        const sessionsResponse = await axios.get(`${apiUrl}/api/sessions/`);
        const memoriesResponse = await axios.get(`${apiUrl}/api/memories/`);
        
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
        } else {
            status.push('  No clips yet');
        }
        
        const channel = vscode.window.createOutputChannel('Crecall Status');
        channel.clear();
        channel.appendLine(status.join('\\n'));
        channel.show();
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to get status: ${error.message}`);
    }
}

export function deactivate() {
    if (autoClipTimer) {
        clearInterval(autoClipTimer);
    }
}
