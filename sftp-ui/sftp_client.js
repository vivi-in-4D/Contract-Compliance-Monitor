// constants
const SFTP_IP = '0.0.0.0';
const SFTP_PORT = 22

async function connectSFTP(event) {
    event.preventDefault();
    const statusElement = document.getElementById('connection_status');
    statusElement.textContent = "Connecting...";
    statusElement.style.color = "blue";

    try {
        const response = await fetch('/sftp_connect', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                host: SFTP_IP,
                // port: SFTP_PORT,
                username: document.getElementById('sftp_username').value,
                password: document.getElementById('sftp_password').value
            })
        });

        const responseText = await response.text();
        
        if (!response.ok) {
            // try to parse as JSON, but fall back to raw text if it fails
            let errorMsg = responseText;
            try {
                const errorData = JSON.parse(responseText);
                errorMsg = errorData.message || errorMsg;
            } catch (e) {
                // not JSON, use the raw text
            }
            throw new Error(errorMsg);
        }

        const result = JSON.parse(responseText);
        
        if (result.success) {
            statusElement.textContent = "Connected successfully!";
            statusElement.style.color = "green";
            window.location.href = '/sftp_browser';
        } else {
            throw new Error(result.message || "Connection failed");
        }
    } catch (error) {
        statusElement.textContent = "Error: " + error.message;
        statusElement.style.color = "red";
        console.error("Connection failed:", error);
    }
}

uploadBtn.addEventListener('click', async () => {
  const groupPass = document.getElementById('group-password').value.trim();
  const errorEl = document.getElementById('auth-error');
  
  // input sanitization
  if (!groupPass) {
    errorEl.textContent = "Group password is required";
    return;
  }
  
  if (!/^[\w-]{8,64}$/.test(groupPass)) {
    errorEl.textContent = "Invalid characters in password";
    return;
  }

  if (!selectedUploadDir || !selectedFile) {
    errorEl.textContent = "Please select both a directory and file";
    return;
  }

  try {
    errorEl.textContent = "";
    uploadBtn.disabled = true;
    
    // sanitize filename
    const safeFilename = selectedFile.name.replace(/[^a-zA-Z0-9\-._]/g, '');
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('groupPass', groupPass);
    formData.append('directory', selectedUploadDir);

    const response = await fetch(`/sftp_upload`, {
      method: 'POST',
      body: formData
    });

    if (!response.ok) throw new Error(await response.text());
    
    alert("File uploaded successfully!");
  } catch (err) {
    errorEl.textContent = `Upload failed: ${err.message}`;
    console.error("Upload error:", err);
  } finally {
    uploadBtn.disabled = false;
  }
});
