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
  let matchedPairs = [];

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

  fetchBtn.addEventListener('click', async () => { await fetchSheet(); await scanImages(); });
  scanBtn.addEventListener('click', scanImages);

  processBtn.addEventListener('click', async () => {
    const pairs = buildPairs();
    if (pairs.length === 0) {
      progress.textContent = 'No matched pairs to process.';
      return;
    }
    processBtn.disabled = true;
    progress.textContent = 'Processing…';
    try {
      const res = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pairs),
      });
      const data = await res.json();
      const lines = data.results.map(r =>
        r.ok ? `✓ ${r.date}` : `✗ ${r.date}: ${r.error}`
      );
      progress.textContent = lines.join('\n');
      updateRowStatuses(data.results);
    } catch {
      progress.textContent = 'Process request failed.';
    } finally {
      processBtn.disabled = false;
    }
  });

  uploadBtn.addEventListener('click', async () => {
    const pairs = buildPairs();
    if (pairs.length === 0) {
      progress.textContent = 'No matched pairs to upload.';
      return;
    }
    uploadBtn.disabled = true;
    progress.textContent = 'Uploading to Drive…';
    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(pairs),
      });
      const data = await res.json();
      const lines = data.results.map(r =>
        r.ok ? `✓ ${r.date} — uploaded` : `✗ ${r.date}: ${r.error}`
      );
      progress.textContent = lines.join('\n');
      updateRowStatuses(data.results.map(r => ({ ...r, status: r.ok ? 'Uploaded' : 'Error' })));
      if (data.results.some(r => r.ok)) {
        await fetchSheet();
        await scanImages();
      }
    } catch {
      progress.textContent = 'Upload request failed.';
    } finally {
      uploadBtn.disabled = false;
    }
  });

  async function checkAuth() {
    try {
      const res = await fetch('/api/test-sheets');
      const data = await res.json();
      if (data.ok) {
        authStatus.textContent = `Connected — "${data.title}"`;
        await fetchSheet();
        await scanImages();
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
    matchedPairs = [];
    try {
      const res = await fetch('/api/images');
      const data = await res.json();
      if (!data.ok) {
        scanStatus.textContent = 'Error: ' + data.error;
        return;
      }
      if (data.matched.length === 0) {
        scanStatus.textContent = 'No images found in ~/Downloads/CoWork.';
        return;
      }
      matchedPairs = data.matched;
      let matchCount = 0;
      data.matched.forEach((pair, i) => {
        const tr = document.createElement('tr');
        tr.dataset.date = pair.date;
        tr.dataset.image = pair.image || '';
        tr.innerHTML = `
          <td>${i + 1}</td>
          <td>${pair.image ? escHtml(pair.image) : '<em>no image found</em>'}</td>
          <td>→</td>
          <td>${pair.date}</td>
        `;
        if (!pair.matched) tr.classList.add('unmatched');
        else matchCount++;
        matchRows.appendChild(tr);
      });
      matchTable.style.display = '';
      scanStatus.textContent = `${matchCount} of ${data.matched.length} rows matched.`;
    } catch {
      scanStatus.textContent = 'Request failed.';
    } finally {
      scanBtn.disabled = false;
    }
  }

  function buildPairs() {
    return matchedPairs
      .filter(p => p.matched)
      .map(p => {
        const sheetTr = sheetRowsTbody.querySelector(`tr[data-date="${p.date}"]`);
        const line1 = sheetTr ? sheetTr.querySelector('[data-field="line1"]').value : p.line1;
        const line2 = sheetTr ? sheetTr.querySelector('[data-field="line2"]').value : p.line2;
        return { image: p.image, date: p.date, line1, line2 };
      });
  }

  function updateRowStatuses(results, defaultOkLabel = 'Processed') {
    results.forEach(r => {
      const tr = sheetRowsTbody.querySelector(`tr[data-date="${r.date}"]`);
      if (tr) tr.querySelector('.row-status').textContent = r.ok ? (r.status || defaultOkLabel) : 'Error';
    });
  }

  function escHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }
});
