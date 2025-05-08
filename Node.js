const { spawn } = require('child_process');
const path = require('path');

// Example input values
const passphrase = 'blue0214';
const filename = 'bluecui1';
const groupName = 'blueteam';

// Resolve the full path to the script
const scriptPath = path.resolve(__dirname, 'Encrypt.sh');

// Spawn the Bash script with three arguments
const child = spawn('bash', [scriptPath, passphrase, filename, groupName]);

// Handle output
child.stdout.on('data', (data) => {
  console.log(`stdout: ${data.toString().trim()}`);
});

child.stderr.on('data', (data) => {
  console.error(`stderr: ${data.toString().trim()}`);
});

child.on('close', (code) => {
  console.log(`Encrypt.sh exited with code ${code}`);
});