const { spawn } = require('child_process');
const path = require('path');
const crypto = require('crypto');

function navigate(page) {
    window.location.href = page
    console.log("moved to %s",page)
}


function sendGroupPass() {
    const passphrase = document.getElementById('group_pass').value;
    const groupName = document.getElementById('group_name').value;
    const filename = document.getElementById('file_name').value;

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
}