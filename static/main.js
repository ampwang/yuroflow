document.addEventListener('DOMContentLoaded', () => {
  const authStatus = document.getElementById('auth-status');
  const authBtn = document.getElementById('auth-btn');
  const fetchBtn = document.getElementById('fetch-btn');
  const fetchStatus = document.getElementById('fetch-status');
  const sheetRowsTbody = document.getElementById('sheet-rows');
  const scanBtn = document.getElementById('scan-btn');
  const scanStatus = document.getElementById('scan-status');
  const matchTable = document.getElementById('match-table');
  const matchRows = document.getElementById('match-rows');
  const processBtn = document.getElementById('process-btn');
  const uploadBtn = document.getElementById('upload-btn');
  const progress = document.getElementById('progress');

  let sheetRows = [];

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
  scanBtn.addEventListener('click', scanImages);

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
        scanImages();
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
    sheetRowsTbody.innerHTML = '';
    sheetRows = [];
    try {
      const res = await fetch('/api/sheet-rows');
      const data = await res.json();
      if (!data.ok) {
        fetchStatus.textContent = 'Error: ' + data.error;
        return;
      }
      sheetRows = data.rows;
      if (sheetRows.length === 0) {
        fetchStatus.textContent = 'No pending rows found.';
        return;
      }
      sheetRows.forEach(row => {
        const tr = document.createElement('tr');
        tr.dataset.date = row.date;
        tr.innerHTML = `
          <td>${row.date}</td>
          <td><input type="text" value="${escHtml(row.line1)}" data-field="line1" /></td>
          <td><input type="text" value="${escHtml(row.line2)}" data-field="line2" /></td>
          <td class="row-status">—</td>
        `;
        sheetRowsTbody.appendChild(tr);
      });
      fetchStatus.textContent = `${sheetRows.length} row${sheetRows.length !== 1 ? 's' : ''} loaded.`;
    } catch {
      fetchStatus.textContent = 'Request failed.';
    } finally {
      fetchBtn.disabled = false;
    }
  }

  async function scanImages() {
    scanBtn.disabled = true;
    scanStatus.textContent = 'Scanning…';
    matchRows.innerHTML = '';
    matchTable.style.display = 'none';
    try {
      const res = await fetch('/api/images');
      const data = await res.json();
      if (!data.ok) {
        scanStatus.textContent = 'Error: ' + data.error;
        return;
      }
      if (data.images.length === 0) {
        scanStatus.textContent = 'No images found in ~/Downloads/CoWork.';
        return;
      }
      data.images.forEach((filename, i) => {
        const date = sheetRows[i] ? sheetRows[i].date : '(no matching row)';
        const tr = document.createElement('tr');
        tr.dataset.image = filename;
        tr.dataset.date = sheetRows[i] ? sheetRows[i].date : '';
        tr.innerHTML = `
          <td>${i + 1}</td>
          <td>${escHtml(filename)}</td>
          <td>→</td>
          <td>${date}</td>
        `;
        if (!sheetRows[i]) tr.classList.add('unmatched');
        matchRows.appendChild(tr);
      });
      matchTable.style.display = '';
      scanStatus.textContent = `${data.images.length} image${data.images.length !== 1 ? 's' : ''} found.`;
    } catch {
      scanStatus.textContent = 'Request failed.';
    } finally {
      scanBtn.disabled = false;
    }
  }

  function escHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
});
