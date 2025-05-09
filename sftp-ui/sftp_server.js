const express = require('express');
const http = require('http');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');
const crypto = require('crypto');
const Client = require('ssh2-sftp-client');
const { spawn } = require('child_process');

const app = express();
const HTML_DIRECTORY = 'public'; // Directory for static files
const connections = {}; // Store SFTP connections

app.use(bodyParser.json());
app.use(express.static(HTML_DIRECTORY));

// Serve the home page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'home.html'));
});

// Endpoint to handle sendGroupPass
app.post('/sendGroupPass', (req, res) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
        const { group_pass, group_name, file_name } = JSON.parse(body);

        // Hash the passphrase
        const hashedPassphrase = crypto.createHash('sha3-256').update(group_pass).digest('hex');

        // Spawn the Python script
        const pythonGen = spawn('python3', ['keygen.py', group_pass]);
        let pythonKey = '';

        pythonGen.stdout.on('data', (data) => {
            pythonKey += data.toString();
        });

        pythonGen.on('close', (code) => {
            console.log(`Python script exited with code ${code}`);

            // Spawn the Bash script
            const scriptPath = path.resolve(__dirname, 'Encrypt.sh');
            const child = spawn('bash', [scriptPath, hashedPassphrase, file_name, group_name, pythonKey]);

            child.stdout.on('data', (data) => {
                console.log(`Bash stdout: ${data.toString().trim()}`);
            });

            child.stderr.on('data', (data) => {
                console.error(`Bash stderr: ${data.toString().trim()}`);
            });

            child.on('close', (code) => {
                console.log(`Encrypt.sh exited with code ${code}`);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, code }));
            });
        });
    });
});

// SFTP login endpoint
app.post('/sftp_connect', async (req, res) => {
    try {
        const { host, username, password } = req.body;

        const sftp = new Client();
        await sftp.connect({ host, username, password });

        // Generate session ID
        const sessionId = Math.random().toString(36).substring(2);
        connections[sessionId] = sftp;

        res.json({
            success: true,
            sessionId
        });
    } catch (err) {
        res.status(500).json({
            success: false,
            message: err.message
        });
    }
});

// List all files in /download recursively
app.post('/sftp_list_downloads', async (req, res) => {
    try {
        const { sessionId } = req.body;
        const sftp = connections[sessionId];

        if (!sftp) throw new Error("Not connected to SFTP server");

        const listFilesRecursively = async (dir) => {
            let files = [];
            try {
                const items = await sftp.list(dir);

                for (const item of items) {
                    const fullPath = path.posix.join(dir, item.name);
                    if (item.type === 'd') {
                        try {
                            const subFiles = await listFilesRecursively(fullPath);
                            files = files.concat(subFiles);
                        } catch (err) {
                            console.log(`Skipping ${fullPath}: ${err.message}`);
                            continue;
                        }
                    } else {
                        files.push({
                            ...item,
                            fullPath,
                            dirPath: dir
                        });
                    }
                }
            } catch (err) {
                if (err.message.includes('Permission denied')) {
                    console.log(`No access to ${dir}, skipping`);
                    return [];
                }
                throw err;
            }
            return files;
        };

        const files = await listFilesRecursively('/download');
        res.json({ success: true, files });
    } catch (err) {
        res.status(500).json({
            success: false,
            message: err.message
        });
    }
});

// List upload subdirectories
app.post('/sftp_list_uploads', async (req, res) => {
    try {
        const { sessionId } = req.body;
        const sftp = connections[sessionId];

        if (!sftp) throw new Error("Not connected");

        const items = await sftp.list('/upload');
        const directories = items.filter(item => item.type === 'd');

        res.json({ success: true, directories });
    } catch (err) {
        res.status(500).json({
            success: false,
            message: err.message
        });
    }
});

// Upload file to selected directory
app.post('/sftp_upload', express.raw({
    type: '*/*',
    limit: '100mb'
}), async (req, res) => {
    try {
        const { sessionId, directory, filename } = req.query;
        const sftp = connections[sessionId];

        if (!sftp) throw new Error("Not connected to SFTP server");

        const uploadBase = '/upload';
        const targetDir = path.posix.join(uploadBase, directory);

        try {
            await sftp.stat(targetDir);
        } catch (err) {
            throw new Error(`Target directory ${targetDir} doesn't exist or you don't have permission`);
        }

        const remotePath = path.posix.join(targetDir, filename);
        await sftp.put(Buffer.from(req.body), remotePath);

        res.json({ success: true });
    } catch (err) {
        console.error('Upload error:', err);
        res.status(500).json({
            success: false,
            message: err.message
        });
    }
});

// Download file
app.post('/sftp_download', async (req, res) => {
    try {
        const { sessionId, filePath } = req.body;
        const sftp = connections[sessionId];

        if (!sftp) throw new Error("Not connected");

        const file = await sftp.get(filePath);
        const filename = path.basename(filePath);

        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.send(file);
    } catch (err) {
        res.status(500).json({
            success: false,
            message: err.message
        });
    }
});

// Disconnect
app.post('/sftp_disconnect', async (req, res) => {
    try {
        const { sessionId } = req.body;
        const sftp = connections[sessionId];

        if (sftp) {
            await sftp.end();
            delete connections[sessionId];
        }

        res.json({ success: true });
    } catch (err) {
        res.status(500).json({
            success: false,
            message: err.message
        });
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));