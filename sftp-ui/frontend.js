function navigate(page) {
    window.location.href = page;
    console.log("moved to %s", page);
}

function sendGroupPass() {
    const passphrase = document.getElementById('group_pass').value;
    const groupName = document.getElementById('group_name').value;
    const filename = document.getElementById('file_name').value;

    // Send the data to the Node.js server
    fetch('/sendGroupPass', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            group_pass: passphrase,
            group_name: groupName,
            file_name: filename,
        }),
    })
        .then((response) => response.json())
        .then((data) => {
            console.log('Response from server:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}