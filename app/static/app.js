function apiHeaders() {
  const token = localStorage.getItem('apiToken');
  return token ? { 'X-API-Key': token, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' };
}

function setupLogin() {
  const form = document.getElementById('login-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    const res = await fetch('/auth/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (res.ok) {
      const json = await res.json();
      localStorage.setItem('apiToken', json.token);
      window.location.href = '/board';
    } else {
      document.getElementById('login-error').textContent = 'Login failed';
    }
  });
}

async function loadBoard() {
  const board = document.getElementById('board');
  const plRes = await fetch('/pipelines', { headers: apiHeaders() });
  if (!plRes.ok) return (board.textContent = 'Failed to load');
  const pipelines = await plRes.json();
  board.innerHTML = '';
  for (const p of pipelines) {
    const col = document.createElement('div');
    col.className = 'column';
    col.innerHTML = `<h3>${p.name}</h3>`;
    const stRes = await fetch(`/pipelines/${p.id}/stages`, { headers: apiHeaders() });
    if (stRes.ok) {
      const stages = await stRes.json();
      for (const s of stages) {
        const stageDiv = document.createElement('div');
        stageDiv.innerHTML = `<strong>${s.name}</strong>`;
        col.appendChild(stageDiv);
        const nRes = await fetch(`/pipelines/${p.id}/stages/${s.id}/negotiations`, { headers: apiHeaders() });
        if (nRes.ok) {
          const negotiations = await nRes.json();
          for (const n of negotiations) {
            const card = document.createElement('div');
            card.className = 'card';
            card.textContent = n.title;
            col.appendChild(card);
          }
        }
      }
    }
    board.appendChild(col);
  }
}

async function loadPipelines() {
  const container = document.getElementById('pipelines');
  const res = await fetch('/pipelines', { headers: apiHeaders() });
  if (!res.ok) return (container.textContent = 'Failed to load');
  const pipelines = await res.json();
  container.innerHTML = pipelines.map(p => `<div>${p.name}</div>`).join('');
}

function showCreatePipeline() {
  const name = prompt('Pipeline name');
  if (!name) return;
  fetch('/pipelines', {
    method: 'POST',
    headers: apiHeaders(),
    body: JSON.stringify({ name })
  }).then(() => loadPipelines());
}

async function loadDashboard() {
  const container = document.getElementById('dashboard');
  const plRes = await fetch('/pipelines', { headers: apiHeaders() });
  if (!plRes.ok) return (container.textContent = 'Failed to load');
  const pipelines = await plRes.json();
  container.innerHTML = `<pre>${JSON.stringify(pipelines, null, 2)}</pre>`;
}

async function loadAdmin() {
  const container = document.getElementById('admin');
  const res = await fetch('/admin/users', { headers: apiHeaders() });
  if (!res.ok) return (container.textContent = 'Failed to load');
  const users = await res.json();
  container.innerHTML = `<pre>${JSON.stringify(users, null, 2)}</pre>`;
}
