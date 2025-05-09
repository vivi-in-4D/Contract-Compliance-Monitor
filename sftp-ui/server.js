const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const crypto = require('crypto');

const HOME_PAGE = 'home.html';

const server = http.createServer((req, res) => {
    console.log(`Request for ${req.url} received`);

    if (req.method === 'POST' && req.url === '/sendGroupPass') {
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
        return;
    }

    // Static file handling
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
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});