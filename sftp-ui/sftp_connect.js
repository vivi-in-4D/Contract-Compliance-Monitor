const express = require('express');
const Client = require('ssh2-sftp-client');
const app = express();
const bodyParser = require('body-parser');
const path = require('path');
const https = require('https');
const fs = require('fs');

const HTML_DIRECTORY = 'public'; // this directory houses our html files

// HTTPS configuration - replace with your actual certificate paths
const sslOptions = {
    key: fs.readFileSync('server.key'),
    cert: fs.readFileSync('server.cert')
};

app.use(bodyParser.json());
app.use(express.static(HTML_DIRECTORY));

// store SFTP connections
const connections = {};

// login endpoint
app.post('/sftp_connect', async (req, res) => {
    try {
        const { host, username, password } = req.body;
        
        const sftp = new Client();
        await sftp.connect({ host, username, password });
        
        // gen session ID
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

// list all files in /download recursively
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
                            // skip directories we can't access
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
                    return []; // return empty array for directories we cant access
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

// list upload subdirectories
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

// upload file to selected directory
app.post('/sftp_upload', express.raw({
    type: '*/*',
    limit: '100mb'
}), async (req, res) => {
    try {
        const { sessionId, directory, filename } = req.query;
        const sftp = connections[sessionId];
        
        if (!sftp) throw new Error("Not connected to SFTP server");
        
        // ensure the upload directory exists
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

// download file
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

// disconnect
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

// serve the browser page
app.get('/sftp_browser', (req, res) => {
    res.sendFile(path.join(__dirname, HTML_DIRECTORY, 'sftp_browser.html'));
});

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, HTML_DIRECTORY, 'index.html'));
});

const PORT = process.env.PORT || 3000;

// Create HTTPS server
https.createServer(sslOptions, app).listen(PORT, () => {
    console.log(`HTTPS Server running on https://localhost:${PORT}`);
});

// Optional: Create HTTP server that redirects to HTTPS
const http = require('http');
http.createServer((req, res) => {
    res.writeHead(301, { 'Location': `https://localhost:${PORT}${req.url}` });
    res.end();
}).listen(3001, () => {
    console.log(`HTTP redirect server running on http://localhost:3001`);
});
