function navigate(page) {
    window.location.href = page
    console.log("moved to %s",page)
}


function sendGroupPass() {
    const pass = document.getElementById('group_pass').value;
    // Add your password handling logic here
    console.log("Password entered:", pass);
    
    // If you need to actually submit to a server:
    // fetch('/your-endpoint', { method: 'POST', body: pass });
    // return false; // Add this if using fetch
}