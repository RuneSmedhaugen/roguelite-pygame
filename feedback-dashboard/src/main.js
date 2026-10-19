import './style.css';

const ticketsView = document.querySelector('#tickets-view');
const changelogView = document.querySelector('#changelog-view');
const list = document.querySelector('#submissions');
const changelogList = document.querySelector('#changelog-list');
const linkedTickets = document.querySelector('#linked-tickets');
const notice = document.querySelector('#notice');
const updatedAt = document.querySelector('#updated-at');
const tabs = [...document.querySelectorAll('.tab')];
const refreshButton = document.querySelector('#refresh-button');
const detailDialog = document.querySelector('#ticket-detail');
const detailContent = document.querySelector('#ticket-detail-content');
const changelogForm = document.querySelector('#changelog-form');

let activeType = 'bug_report';
let activeView = 'tickets';
let cachedSubmissions = { bug_report: [], feedback: [] };
let cachedChangelog = [];

function setNotice(message = '', kind = '') {
  notice.textContent = message;
  notice.className = message ? `notice ${kind}` : 'notice hidden';
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Date unavailable' : new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(date);
}

function allTickets() {
  return [...cachedSubmissions.bug_report, ...cachedSubmissions.feedback];
}

function showTicket(item) {
  detailContent.replaceChildren();
  const heading = document.createElement('h2');
  heading.textContent = item.title || `Ticket #${item.id}`;
  const meta = document.createElement('p');
  meta.className = 'detail-meta';
  const category = item.type === 'bug_report' ? 'Bug report' : 'Player feedback';
  const severity = item.type === 'bug_report' ? ` · ${item.severity === 'unspecified' ? 'Unrated' : item.severity}` : '';
  meta.textContent = `#${item.id} · ${category}${severity} · ${item.status} · ${formatDate(item.created_at)}`;
  const message = document.createElement('p');
  message.className = 'detail-message';
  message.textContent = item.message;
  detailContent.append(heading, meta, message);
  detailDialog.showModal();
}

function renderSubmissions(items) {
  list.replaceChildren();
  if (items.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<span class="empty-icon">✦</span><h2>Nothing here yet</h2><p>New player tickets will show up here.</p>';
    list.append(empty);
    return;
  }

  for (const item of items) {
    const card = document.createElement('article');
    card.className = 'submission-card';
    const top = document.createElement('div');
    top.className = 'ticket-topline';
    const title = document.createElement('button');
    title.className = 'ticket-title';
    title.type = 'button';
    title.textContent = item.title || `Ticket #${item.id}`;
    title.addEventListener('click', () => showTicket(item));
    const status = document.createElement('span');
    status.className = `status status-${item.status}`;
    status.textContent = item.status;
    top.append(title, status);

    const meta = document.createElement('div');
    meta.className = 'card-meta';
    const category = item.type === 'bug_report' ? 'Bug report' : 'Player feedback';
    const severity = item.type === 'bug_report'
      ? ` · ${item.severity === 'unspecified' ? 'Unrated' : (item.severity || 'Unrated')}`
      : '';
    meta.textContent = `#${item.id} · ${category}${severity} · ${formatDate(item.created_at)}`;
    const summary = document.createElement('p');
    summary.className = 'message ticket-summary';
    summary.textContent = item.message;
    card.append(top, meta, summary);
    list.append(card);
  }
}

function renderTicketLinks(selectedIds = new Set()) {
  linkedTickets.replaceChildren();
  const tickets = allTickets();
  if (tickets.length === 0) {
    const empty = document.createElement('p');
    empty.className = 'form-hint';
    empty.textContent = 'Load tickets first to link them to this update.';
    linkedTickets.append(empty);
    return;
  }
  for (const ticket of tickets) {
    const label = document.createElement('label');
    label.className = 'ticket-check';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.name = 'submissionIds';
    checkbox.value = ticket.id;
    checkbox.checked = selectedIds.has(String(ticket.id));
    const text = document.createElement('span');
    text.textContent = `#${ticket.id} · ${ticket.title || 'Untitled ticket'} (${ticket.type === 'bug_report' ? 'bug' : 'feedback'})`;
    label.append(checkbox, text);
    linkedTickets.append(label);
  }
}

function renderChangelog(entries) {
  changelogList.replaceChildren();
  if (!entries.length) {
    const empty = document.createElement('div');
    empty.className = 'empty-state';
    empty.innerHTML = '<span class="empty-icon">✦</span><h2>No updates posted yet</h2><p>Publish a changelog entry above when you ship a change.</p>';
    changelogList.append(empty);
    return;
  }
  for (const entry of entries) {
    const card = document.createElement('article');
    card.className = 'submission-card changelog-card';
    const heading = document.createElement('div');
    heading.className = 'ticket-topline';
    const title = document.createElement('h2');
    title.className = 'changelog-title';
    title.textContent = entry.title;
    const date = document.createElement('time');
    date.className = 'card-meta';
    date.dateTime = entry.created_at;
    date.textContent = formatDate(entry.created_at);
    heading.append(title, date);
    const body = document.createElement('p');
    body.className = 'message';
    body.textContent = entry.body;
    card.append(heading, body);
    if (entry.tickets?.length) {
      const links = document.createElement('div');
      links.className = 'linked-ticket-list';
      for (const linked of entry.tickets) {
        const link = document.createElement('button');
        link.className = 'linked-ticket';
        link.type = 'button';
        link.textContent = `#${linked.id} · ${linked.title}`;
        link.addEventListener('click', () => {
          const ticket = allTickets().find((item) => String(item.id) === String(linked.id));
          if (ticket) showTicket(ticket);
        });
        links.append(link);
      }
      card.append(links);
    }
    changelogList.append(card);
  }
}

function setLoading(target, text) {
  target.replaceChildren();
  const loading = document.createElement('div');
  loading.className = 'loading-state';
  loading.textContent = text;
  target.append(loading);
}

async function loadSubmissions() {
  setNotice();
  setLoading(list, 'Loading tickets…');
  refreshButton.disabled = true;
  try {
    const response = await fetch('/api/submissions?type=all');
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Request failed (HTTP ${response.status})`);
    const items = data.submissions || [];
    cachedSubmissions.bug_report = items.filter((item) => item.type === 'bug_report');
    cachedSubmissions.feedback = items.filter((item) => item.type === 'feedback' || item.type === 'suggestion');
    document.querySelector('#bug-count').textContent = cachedSubmissions.bug_report.length;
    document.querySelector('#feedback-count').textContent = cachedSubmissions.feedback.length;
    renderSubmissions(cachedSubmissions[activeType]);
    renderTicketLinks();
    updatedAt.textContent = `Updated ${new Intl.DateTimeFormat(undefined, { timeStyle: 'short' }).format(new Date())}`;
  } catch (error) {
    list.replaceChildren();
    setNotice(`${error.message}. Check that the feedback API is available, then refresh.`, 'error');
  } finally {
    refreshButton.disabled = false;
  }
}

async function loadChangelog() {
  setLoading(changelogList, 'Loading changelog…');
  try {
    const response = await fetch('/api/changelog');
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Request failed (HTTP ${response.status})`);
    cachedChangelog = data.entries || [];
    renderChangelog(cachedChangelog);
  } catch (error) {
    changelogList.replaceChildren();
    setNotice(`${error.message}. Check the API, then refresh.`, 'error');
  }
}

function switchView(view) {
  activeView = view;
  ticketsView.classList.toggle('hidden', view !== 'tickets');
  changelogView.classList.toggle('hidden', view !== 'changelog');
  document.querySelector('#page-title').textContent = view === 'tickets' ? 'Player inbox' : 'Changelog';
  document.querySelector('#page-subtitle').textContent = view === 'tickets'
    ? 'Bug reports and player feedback sent from the game.'
    : 'Publish updates for players and link the tickets they address.';
  tabs.forEach((tab) => tab.classList.toggle('active', tab.dataset.view === view && (view === 'changelog' || tab.dataset.type === activeType)));
  if (view === 'changelog') loadChangelog();
}

for (const tab of tabs) {
  tab.addEventListener('click', () => {
    if (tab.dataset.view === 'changelog') {
      switchView('changelog');
      return;
    }
    activeType = tab.dataset.type;
    switchView('tickets');
    tabs.forEach((item) => item.classList.toggle('active', item === tab));
    renderSubmissions(cachedSubmissions[activeType]);
  });
}

refreshButton.addEventListener('click', () => activeView === 'tickets' ? loadSubmissions() : loadChangelog());
document.querySelector('#close-ticket-detail').addEventListener('click', () => detailDialog.close());
detailDialog.addEventListener('click', (event) => {
  if (event.target === detailDialog) detailDialog.close();
});

changelogForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  setNotice();
  const formData = new FormData(changelogForm);
  const submissionIds = formData.getAll('submissionIds');
  const submit = changelogForm.querySelector('button[type="submit"]');
  submit.disabled = true;
  try {
    const response = await fetch('/api/changelog', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: formData.get('title'),
        body: formData.get('body'),
        submissionIds,
      }),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || `Request failed (HTTP ${response.status})`);
    changelogForm.reset();
    setNotice('Changelog entry published.', 'success');
    await loadChangelog();
  } catch (error) {
    setNotice(error.message, 'error');
  } finally {
    submit.disabled = false;
  }
});

loadSubmissions();
