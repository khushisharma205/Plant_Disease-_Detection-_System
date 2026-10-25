// ══════════════════════════════════════
//  PlantGuard AI — Frontend JS
// ══════════════════════════════════════

// ── Upload ──
const uploadBox   = document.getElementById('uploadBox');
const fileInput   = document.getElementById('fileInput');
const uploadInner = document.getElementById('uploadInner');
const previewArea = document.getElementById('previewArea');
const previewImg  = document.getElementById('previewImg');
const removeBtn   = document.getElementById('removeBtn');
const detectBtn   = document.getElementById('detectBtn');
const resultSec   = document.getElementById('resultSection');

let selectedFile = null;

if (uploadBox) {
  uploadBox.addEventListener('click', () => {
    if (previewArea.style.display === 'none' || !previewArea.style.display) fileInput.click();
  });
  uploadBox.addEventListener('dragover', e => { e.preventDefault(); uploadBox.classList.add('drag-over'); });
  uploadBox.addEventListener('dragleave', () => uploadBox.classList.remove('drag-over'));
  uploadBox.addEventListener('drop', e => {
    e.preventDefault(); uploadBox.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener('change', () => { if (fileInput.files[0]) handleFile(fileInput.files[0]); });
  removeBtn.addEventListener('click', e => { e.stopPropagation(); resetUpload(); });
}

function handleFile(file) {
  const allowed = ['image/png','image/jpeg','image/webp'];
  if (!allowed.includes(file.type)) { alert('Please upload PNG, JPG or WEBP only!'); return; }
  selectedFile = file;
  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    uploadInner.style.display = 'none';
    previewArea.style.display = 'block';
    detectBtn.disabled = false;
    if (resultSec) resultSec.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

function resetUpload() {
  selectedFile = null; fileInput.value = '';
  previewImg.src = '';
  uploadInner.style.display = 'block';
  previewArea.style.display = 'none';
  detectBtn.disabled = true;
  if (resultSec) resultSec.style.display = 'none';
}

// ── Detect ──
if (detectBtn) {
  detectBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    document.getElementById('btnText').style.display   = 'none';
    document.getElementById('btnLoader').style.display = 'inline';
    detectBtn.disabled = true;

    const fd = new FormData();
    fd.append('file', selectedFile);

    try {
      const res  = await fetch('/predict', { method: 'POST', body: fd });
      const data = await res.json();
      if (data.error) { alert('Error: ' + data.error); return; }
      renderResult(data);
    } catch (err) {
      alert('Connection error — make sure Flask is running!');
    } finally {
      document.getElementById('btnText').style.display   = 'inline';
      document.getElementById('btnLoader').style.display = 'none';
      detectBtn.disabled = false;
    }
  });
}

function renderResult(d) {
  resultSec.style.display = 'block';

  const hdr = document.getElementById('resultHeader');
  hdr.className = 'result-header ' + (d.is_healthy ? 'healthy' : 'diseased');
  const stText = document.getElementById('resStatusText');
  stText.textContent  = d.is_healthy ? '✅ Plant is Healthy!' : '⚠️ Disease Detected!';
  stText.className    = 'res-status-text ' + (d.is_healthy ? '' : 'diseased');

  const badge = document.getElementById('resModeBadge');
  badge.textContent = d.mode === 'demo' ? '🔶 Demo Mode' : '✅ Real AI Model';
  badge.className   = 'mode-badge ' + d.mode;

  document.getElementById('resPlant').textContent      = d.plant;
  document.getElementById('resDisease').textContent    = d.disease;
  document.getElementById('resResolution').textContent = `${d.width} × ${d.height} px`;
  document.getElementById('resFileSize').textContent   = `${d.file_size_kb} KB`;

  const pc = document.getElementById('resPlantConf');
  pc.textContent = d.plant_confidence + '%';
  pc.className   = d.plant_confidence >= 85 ? 'conf-high' : 'conf-mid';

  const dc = document.getElementById('resDiseaseConf');
  dc.textContent = d.disease_confidence + '%';
  dc.className   = d.disease_confidence >= 85 ? 'conf-high' : 'conf-mid';

  document.getElementById('resDesc').textContent = d.description;

  const sl = document.getElementById('symList');
  sl.innerHTML = '';
  d.symptoms.forEach(s => {
    sl.innerHTML += `<li><span class="sym-dot"></span>${s}</li>`;
  });

  document.getElementById('prevText').textContent = d.prevention;
  resultSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ══════════════════════════════════════
//  HISTORY PAGE — FIXED (delete button added)
// ══════════════════════════════════════
const historySec = document.getElementById('historySection');
if (historySec) {
  loadHistory();
}

function loadHistory() {
  fetch('/api/history').then(r => r.json()).then(data => {
    if (!data.length) {
      historySec.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📭</div>
          <h3>No predictions yet</h3>
          <p>Go to Detect page and upload a leaf image to get started!</p>
        </div>`;
      return;
    }

    const rows = data.map((r, i) => `
      <tr id="row-${r.id}">
        <td>${i + 1}</td>
        <td><img class="thumb" src="/static/uploads/${r.image_path}" width="40" height="40" onerror="this.src=''" alt=""></td>
        <td title="${r.plant}">${r.plant}</td>
        <td title="${r.disease}">${r.disease}</td>
        <td>
          <div class="conf-bar"><div class="conf-bar-fill" style="width:${Math.round(r.plant_confidence)}%"></div></div>
          <span style="font-size:0.8rem;font-weight:600;">${Math.round(r.plant_confidence)}%</span>
        </td>
        <td>
          <div class="conf-bar"><div class="conf-bar-fill" style="width:${Math.round(r.disease_confidence)}%"></div></div>
          <span style="font-size:0.8rem;font-weight:600;">${Math.round(r.disease_confidence)}%</span>
        </td>
        <td><span class="tag ${r.is_healthy ? 'tag-healthy' : 'tag-diseased'}">${r.is_healthy ? '✅ Healthy' : '⚠️ Diseased'}</span></td>
        <td><span class="tag tag-${r.mode}">${r.mode}</span></td>
        <td style="font-size:0.78rem;">${r.timestamp.slice(0, 16).replace('T', ' ')}</td>
        <td class="action-cell">
          <button class="delete-btn" onclick="deleteItem(${r.id}, this)">🗑️ Delete</button>
        </td>
      </tr>`).join('');

    historySec.innerHTML = `
      <div class="history-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Image</th>
              <th>Plant</th>
              <th>Disease</th>
              <th>Plant Conf</th>
              <th>Disease Conf</th>
              <th>Status</th>
              <th>Mode</th>
              <th>Time</th>
              <th class="action-head">Action</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>`;
  }).catch(() => {
    historySec.innerHTML = '<div class="loading-state">Failed to load history.</div>';
  });
}

async function deleteItem(id, btn) {
  if (!confirm('Delete this record?')) return;
  btn.disabled = true;
  btn.textContent = '⏳...';
  try {
    const res = await fetch(`/api/history/${id}`, { method: 'DELETE' });
    if (res.ok) {
      const row = document.getElementById(`row-${id}`);
      row.style.transition = 'opacity 0.3s';
      row.style.opacity = '0';
      setTimeout(() => row.remove(), 300);
    } else {
      alert('Delete failed!');
      btn.disabled = false;
      btn.textContent = '🗑️ Delete';
    }
  } catch (e) {
    alert('Network error!');
    btn.disabled = false;
    btn.textContent = '🗑️ Delete';
  }
}

// ══════════════════════════════════════
//  DASHBOARD PAGE
// ══════════════════════════════════════
const statTotal = document.getElementById('statTotal');
if (statTotal) {
  fetch('/api/stats').then(r => r.json()).then(d => {
    document.getElementById('statTotal').textContent    = d.total;
    document.getElementById('statHealthy').textContent  = d.healthy;
    document.getElementById('statDiseased').textContent = d.diseased;

    const maxP = Math.max(...d.plant_counts.map(p => p.count), 1);
    document.getElementById('plantBars').innerHTML = d.plant_counts.length
      ? d.plant_counts.map(p => `
          <div class="bar-row">
            <div class="bar-label">${p.plant}</div>
            <div class="bar-track"><div class="bar-fill green" style="width:${(p.count/maxP)*100}%"></div></div>
            <div class="bar-val">${p.count}</div>
          </div>`).join('')
      : '<p style="color:var(--text-light);font-size:.9rem">No data yet</p>';

    const maxD = Math.max(...d.top_diseases.map(x => x.count), 1);
    document.getElementById('diseaseBars').innerHTML = d.top_diseases.length
      ? d.top_diseases.map(x => `
          <div class="bar-row">
            <div class="bar-label">${x.disease}</div>
            <div class="bar-track"><div class="bar-fill red" style="width:${(x.count/maxD)*100}%"></div></div>
            <div class="bar-val">${x.count}</div>
          </div>`).join('')
      : '<p style="color:var(--text-light);font-size:.9rem">No data yet</p>';
  });
}