const http  = require('http');
const fs    = require('fs');
const path  = require('path');
const Client = require('ssh2-sftp-client');

const HOME_PAGE = 'home.html';

const server = http.createServer((req, res) => {
    console.log(`Request for ${req.url} received`);

    if (req.method === 'POST' && req.url === '/sftp_connect') {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', async () => {
            try {
                const { host, username, password } = JSON.parse(body);
                const sftp = new Client();
                await sftp.connect({ host, username, password });
                const cwd = await sftp.cwd();
                await sftp.end();

                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: true, cwd }));
            } catch (err) {
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, message: err.message }));
            }
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
