document.addEventListener('DOMContentLoaded', () => {
  const processBtn = document.getElementById('process-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const progress = document.getElementById('progress');
  const authStatus = document.getElementById('auth-status');
  const authBtn = document.getElementById('auth-btn');

  checkAuth();

  authBtn.addEventListener('click', async () => {
    authStatus.textContent = 'Opening browser for Google login…';
    authBtn.disabled = true;
    const res = await fetch('/auth');
    const data = await res.json();
    if (data.ok) {
      authStatus.textContent = 'Connected to Google.';
      authBtn.style.display = 'none';
    } else {
      authStatus.textContent = 'Auth failed: ' + data.error;
      authBtn.disabled = false;
    }
  });

  processBtn.addEventListener('click', () => {
    progress.textContent = 'Processing...';
  });

  uploadBtn.addEventListener('click', () => {
    progress.textContent = 'Uploading...';
  });

  async function checkAuth() {
    try {
      const res = await fetch('/api/test-sheets');
      const data = await res.json();
      if (data.ok) {
        authStatus.textContent = `Connected — "${data.title}"`;
      } else {
        authStatus.textContent = 'Not connected.';
        authBtn.style.display = 'inline-block';
      }
    } catch {
      authStatus.textContent = 'Not connected.';
      authBtn.style.display = 'inline-block';
    }
  }
});
