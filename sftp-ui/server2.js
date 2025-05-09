const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const crypto = require('crypto');

const HOME_PAGE = 'home.html';

// SSL certificate config
const sslOptions = {
    key: fs.readFileSync('server.key'),    // Path to your private key
    cert: fs.readFileSync('server.cert')  // Path to your certificate
};

const requestHandler = (req, res) => {
    console.log(`Request for ${req.url} received`);

    if (req.method === 'POST' && req.url === '/sendGroupPass') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            const { group_pass, group_name, file_name } = JSON.parse(body);
            const hashedPassphrase = crypto.createHash('sha3-256').update(group_pass).digest('hex');
            
            const pythonGen = spawn('python3', ['keygen.py', group_pass]);
            let pythonKey = '';

            pythonGen.stdout.on('data', (data) => {
                pythonKey += data.toString();
            });

            pythonGen.on('close', (code) => {
                const scriptPath = path.resolve(__dirname, 'Encrypt.sh');
                const child = spawn('bash', [scriptPath, hashedPassphrase, file_name, group_name, pythonKey]);

                child.stdout.on('data', (data) => {
                    console.log(`Bash stdout: ${data.toString().trim()}`);
                });

                child.stderr.on('data', (data) => {
                    console.error(`Bash stderr: ${data.toString().trim()}`);
                });

                child.on('close', (code) => {
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ success: true, code }));
                });
            });
        });
        return;
    }

    // static file handling
    let filepath = '.' + req.url;
    if (filepath === './') filepath = './' + HOME_PAGE;

    const extname = path.extname(filepath);
    let contentType = 'text/html';
    switch (extname) {
        case '.js': contentType = 'text/javascript'; break;
        case '.css': contentType = 'text/css'; break;
        case '.json': contentType = 'application/json'; break;
        case '.png': contentType = 'image/png'; break;
        case '.jpg': contentType = 'image/jpg'; break;
    }

    fs.readFile(filepath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                fs.readFile('./404.html', (err404, content404) => {
                    res.writeHead(404, { 'Content-Type': 'text/html' });
                    res.end(content404, 'utf-8');
                });
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${err.code}`);
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content, 'utf-8');
        }
    });
};

// create both http and https servers
const httpServer = http.createServer(requestHandler);
const httpsServer = https.createServer(sslOptions, requestHandler);

const HTTP_PORT = process.env.HTTP_PORT || 3000;
const HTTPS_PORT = process.env.HTTPS_PORT || 3443;

httpServer.listen(HTTP_PORT, () => {
    console.log(`HTTP server running on port ${HTTP_PORT}`);
});

httpsServer.listen(HTTPS_PORT, () => {
    console.log(`HTTPS server running on port ${HTTPS_PORT}`);
});
