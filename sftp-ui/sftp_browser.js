window.onload = async function () {
  let currentPath = '/';
  
  // Function to list files in current directory
  async function listFiles(path = currentPath) {
      try {
          const response = await fetch('/sftp_list', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ path })
          });
          
          const result = await response.json();
          
          if (result.success) {
              displayFiles(result.files);
              currentPath = path;
              document.getElementById('current-path').textContent = currentPath;
          } else {
              alert('Error: ' + result.message);
          }
      } catch (error) {
          alert('Error: ' + error.message);
      }
  }
  
  // Function to display files in the UI
  function displayFiles(files) {
      const fileList = document.getElementById('file-list');
      fileList.innerHTML = '';
      
      // Add parent directory link (except for root)
      if (currentPath !== '/') {
          const parentItem = document.createElement('div');
          parentItem.className = 'file-item directory';
          parentItem.innerHTML = '📁 ..';
          parentItem.onclick = () => {
              const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
              listFiles(parentPath);
          };
          fileList.appendChild(parentItem);
      }
      
      // Add each file/directory
      files.forEach(file => {
          const item = document.createElement('div');
          item.className = `file-item ${file.type === 'd' ? 'directory' : 'file'}`;
          
          const icon = file.type === 'd' ? '📁' : '📄';
          item.innerHTML = `${icon} ${file.name}`;
          
          if (file.type === 'd') {
              item.onclick = () => {
                  const newPath = currentPath === '/' 
                      ? `/${file.name}` 
                      : `${currentPath}/${file.name}`;
                  listFiles(newPath);
              };
          } else {
              item.onclick = () => {
                  alert(`File clicked: ${file.name}`);
                  // You could add download functionality here
              };
          }
          
          fileList.appendChild(item);
      });
  }
  
  // Initial file listing
  listFiles();
  
  // Change directory button
  document.getElementById('change-dir-button').addEventListener('click', () => {
      const newPath = prompt('Enter directory path:', currentPath);
      if (newPath) {
          listFiles(newPath);
      }
  });
  
  // Upload button
  document.getElementById('upload-button').addEventListener('click', () => {
      alert('Upload functionality would go here');
  });
  
  // Disconnect button
  document.getElementById('disconnect-button').addEventListener('click', async () => {
      try {
          await fetch('/sftp_disconnect', { method: 'POST' });
          window.location.href = '/';
      } catch (error) {
          alert('Error disconnecting: ' + error.message);
      }
  });
};
