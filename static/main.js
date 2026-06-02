document.addEventListener('DOMContentLoaded', () => {
  const processBtn = document.getElementById('process-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const progress = document.getElementById('progress');
  const authStatus = document.getElementById('auth-status');
  const authBtn = document.getElementById('auth-btn');
  const fetchBtn = document.getElementById('fetch-btn');
  const fetchStatus = document.getElementById('fetch-status');
  const sheetRows = document.getElementById('sheet-rows');

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

  fetchBtn.addEventListener('click', fetchSheet);

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
        fetchSheet();
      } else {
        authStatus.textContent = 'Not connected.';
        authBtn.style.display = 'inline-block';
      }
    } catch {
      authStatus.textContent = 'Not connected.';
      authBtn.style.display = 'inline-block';
    }
  }

  async function fetchSheet() {
    fetchBtn.disabled = true;
    fetchStatus.textContent = 'Loading…';
    sheetRows.innerHTML = '';
    try {
      const res = await fetch('/api/sheet-rows');
      const data = await res.json();
      if (!data.ok) {
        fetchStatus.textContent = 'Error: ' + data.error;
        return;
      }
      if (data.rows.length === 0) {
        fetchStatus.textContent = 'No pending rows found.';
        return;
      }
      data.rows.forEach(row => {
        const tr = document.createElement('tr');
        tr.dataset.date = row.date;
        tr.innerHTML = `
          <td>${row.date}</td>
          <td><input type="text" value="${escHtml(row.line1)}" data-field="line1" /></td>
          <td><input type="text" value="${escHtml(row.line2)}" data-field="line2" /></td>
          <td class="row-status">—</td>
        `;
        sheetRows.appendChild(tr);
      });
      fetchStatus.textContent = `${data.rows.length} row${data.rows.length !== 1 ? 's' : ''} loaded.`;
    } catch (e) {
      fetchStatus.textContent = 'Request failed.';
    } finally {
      fetchBtn.disabled = false;
    }
  }

  function escHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
});
