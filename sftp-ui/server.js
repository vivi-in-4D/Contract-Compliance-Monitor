const HOME_PAGE = 'home.html'

const http  = require('http');
const fs    = require('fs');
const path  = require('path');

const server = http.createServer((req,res) => {
    console.log(`Request for ${req.url} received`);

    let filepath = '.' + req.url;
    if (filepath === './') {
        filepath = './' + HOME_PAGE;
    }

    const extname = path.extname(filepath);

    let contentType = 'text/html';
    switch (extname) {
        case '.js':
            contentType = 'text/javascript';
            break;
        case '.css':
            contentType = 'text/css';
            break;
        case '.json':
            contentType = 'application/json';
            break;
        case '.png':
            contentType = 'image/png';
            break;
        case '.jpg':
            contentType = 'image/jpg';
            break;
    }

        // Read the file
        fs.readFile(filepath, (err, content) => {
            if (err) {
                if (err.code == 'ENOENT') {
                    // File not found
                    fs.readFile('./404.html', (err, content) => {
                        res.writeHead(404, { 'Content-Type': 'text/html' });
                        res.end(content, 'utf-8');
                    });
                } else {
                    // Some server error
                    res.writeHead(500);
                    res.end(`Server Error: ${err.code}`);
                }
            } else {
                // Success - serve the file
                res.writeHead(200, { 'Content-Type': contentType });
                res.end(content, 'utf-8');
            }
        });
    });
    
    // Set the port number
    const PORT = process.env.PORT || 3000;
    
    // Start the server
    server.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
})
