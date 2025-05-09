const { spawn } = require('child_process');
const path = require('path');
const crypto = require('crypto');

// Example input values
const passphrase = 'blue0214';
const filename = 'bluecui1';
const groupName = 'blueteam';

const hashedPassphrase = crypto.createHash('sha3-256').update(passphrase).digest('hex');

const pythonGen = spawn('python3', ['keygen.py', passphrase]);
let pythonKey = '';

pythonGen.stdout.on('data', (data) => {
  console.log(`stdout: ${data.toString().trim()}`);
  pythonKey += data.toString();
});

pythonGen.on('close', (code) => {

  // Resolve the full path to the script
  const scriptPath = path.resolve(__dirname, 'Encrypt.sh');

  // Spawn the Bash script with three arguments
  const child = spawn('bash', [scriptPath, hashedPassphrase, filename, groupName]);

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
});