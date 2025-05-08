// Constants
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
                'Content-Type': 'application/json'  // Fixed the header name
            },
            body: JSON.stringify({
                host: SFTP_IP,           // Added host information
                // port: SFTP_PORT,         // Added port information
                username: document.getElementById('sftp_username').value,
                password: document.getElementById('sftp_password').value
            })
        });

        const responseText = await response.text();
        
        if (!response.ok) {
            // Try to parse as JSON, but fall back to raw text if it fails
            let errorMsg = responseText;
            try {
                const errorData = JSON.parse(responseText);
                errorMsg = errorData.message || errorMsg;
            } catch (e) {
                // Not JSON, use the raw text
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
