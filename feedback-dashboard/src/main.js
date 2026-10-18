import './style.css';

const list = document.querySelector('#submissions');
const notice = document.querySelector('#notice');
const updatedAt = document.querySelector('#updated-at');
const tabs = [...document.querySelectorAll('.tab')];
const refreshButton = document.querySelector('#refresh-button');

let activeType = 'bug_report';
let cachedSubmissions = { bug_report: [], suggestion: [] };

function setNotice(message = '', kind = '') {
  notice.textContent = message;
  notice.className = message ? `notice ${kind}` : 'notice hidden';
}

function renderSubmissions(items) {
  list.replaceChildren();
  if (items.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<span class="empty-icon">✦</span><h2>Nothing here yet</h2><p>New messages will show up here when players send them.</p>';
    list.append(empty);
    return;
  }

  for (const item of items) {
    const card = document.createElement('article');
    card.className = 'submission-card';

    const meta = document.createElement('div');
    meta.className = 'card-meta';
    const time = document.createElement('time');
    const date = new Date(item.created_at);
    time.dateTime = date.toISOString();
    time.textContent = new Intl.DateTimeFormat(undefined, {
      dateStyle: 'medium',
      timeStyle: 'short',
    }).format(date);
    const status = document.createElement('span');
    status.className = `status status-${item.status}`;
    status.textContent = item.status;
    meta.append(time, status);

    const message = document.createElement('p');
    message.className = 'message';
    message.textContent = item.message;
    card.append(meta, message);
    list.append(card);
  }
}

function setLoading() {
  list.replaceChildren();
  const loading = document.createElement('div');
  loading.className = 'loading-state';
  loading.textContent = 'Loading messages…';
  list.append(loading);
}

async function loadSubmissions() {
  setNotice();
  setLoading();
  refreshButton.disabled = true;
  try {
    const response = await fetch('/api/submissions?type=all');
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Request failed (HTTP ${response.status})`);
    const items = data.submissions || [];
    cachedSubmissions.bug_report = items.filter((item) => item.type === 'bug_report');
    cachedSubmissions.suggestion = items.filter((item) => item.type === 'suggestion');
    document.querySelector('#bug-count').textContent = cachedSubmissions.bug_report.length;
    document.querySelector('#suggestion-count').textContent = cachedSubmissions.suggestion.length;
    renderSubmissions(cachedSubmissions[activeType]);
    updatedAt.textContent = `Updated ${new Intl.DateTimeFormat(undefined, { timeStyle: 'short' }).format(new Date())}`;
  } catch (error) {
    list.replaceChildren();
    setNotice(`${error.message}. Check that the feedback API is available, then refresh.`, 'error');
  } finally {
    refreshButton.disabled = false;
  }
}

for (const tab of tabs) {
  tab.addEventListener('click', () => {
    activeType = tab.dataset.type;
    tabs.forEach((item) => item.classList.toggle('active', item === tab));
    renderSubmissions(cachedSubmissions[activeType]);
  });
}

refreshButton.addEventListener('click', loadSubmissions);
loadSubmissions();
