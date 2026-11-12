/**
 * DocuVault AI — App Utilities
 * Shared helpers: toast, confirm modal, auth, sidebar, formatters.
 */

/* ── Toast ───────────────────────────────────────────────────── */
const Toast = {
  icons: { success:'fa-circle-check', error:'fa-circle-exclamation', warning:'fa-triangle-exclamation', info:'fa-circle-info' },
  show(title, message = '', type = 'info', duration = 4000) {
    const c = document.getElementById('toastContainer');
    if (!c) return;
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<i class="fa-solid ${this.icons[type]||this.icons.info} toast-icon"></i>
      <div class="toast-content"><div class="toast-title">${title}</div>${message?`<div class="toast-message">${message}</div>`:''}</div>
      <button class="toast-close"><i class="fa-solid fa-xmark"></i></button>`;
    c.appendChild(t);
    t.querySelector('.toast-close').onclick = () => this.dismiss(t);
    if (duration > 0) setTimeout(() => this.dismiss(t), duration);
  },
  dismiss(t) { t.style.animation = 'slideIn .3s ease reverse'; setTimeout(() => t.remove(), 280); },
  success(title, msg='') { this.show(title, msg, 'success'); },
  error(title, msg='')   { this.show(title, msg, 'error', 6000); },
  warning(title, msg='') { this.show(title, msg, 'warning'); },
  info(title, msg='')    { this.show(title, msg, 'info'); },
};

/* ── Confirm Modal ───────────────────────────────────────────── */
const Confirm = {
  show(title, message, onConfirm, danger = true) {
    const m = document.getElementById('confirmModal');
    document.getElementById('confirmTitle').textContent = title;
    document.getElementById('confirmMessage').textContent = message;
    const ok = document.getElementById('confirmOk');
    ok.className = danger ? 'btn btn-danger' : 'btn btn-primary';
    m.style.display = 'flex';
    const close = () => { m.style.display = 'none'; };
    document.getElementById('confirmClose').onclick = close;
    document.getElementById('confirmCancel').onclick = close;
    ok.onclick = () => { close(); onConfirm(); };
    m.onclick = e => { if (e.target === m) close(); };
  },
};

/* ── Auth guard ──────────────────────────────────────────────── */
function requireAuth() {
  if (!API.getToken()) { window.location.href = '/login/'; return false; }
  return true;
}

/* ── Current user ────────────────────────────────────────────── */
let _currentUser = null;
async function getCurrentUser(forceRefresh = false) {
  if (_currentUser && !forceRefresh) return _currentUser;
  const cached = localStorage.getItem('current_user');
  if (cached && !forceRefresh) { try { _currentUser = JSON.parse(cached); return _currentUser; } catch {} }
  const r = await API.me();
  if (r && r.ok) { _currentUser = r.data; localStorage.setItem('current_user', JSON.stringify(r.data)); return r.data; }
  return null;
}

/* ── Sidebar hydration ───────────────────────────────────────── */
async function hydrateSidebar() {
  const user = await getCurrentUser();
  if (!user) return;
  const nameEl   = document.getElementById('sidebarUsername');
  const roleEl   = document.getElementById('sidebarRole');
  const avatarEl = document.getElementById('sidebarAvatar');
  if (nameEl)   nameEl.textContent = user.first_name || user.username;
  if (avatarEl) avatarEl.textContent = (user.first_name || user.username || 'U')[0].toUpperCase();
  if (roleEl) {
    roleEl.textContent = user.role;
    const colors = { admin:'badge-danger', manager:'badge-warning', employee:'badge-primary' };
    roleEl.className = `user-role badge ${colors[user.role]||'badge-secondary'}`;
  }
  const navUsers = document.getElementById('navUsers');
  if (navUsers && (user.role === 'admin' || user.role === 'manager')) navUsers.style.display = 'flex';
}

/* ── Logout ──────────────────────────────────────────────────── */
function initLogout() {
  const btn = document.getElementById('logoutBtn');
  if (!btn) return;
  btn.addEventListener('click', async () => { await API.logout(); window.location.href = '/login/'; });
}

/* ── Sidebar toggle ──────────────────────────────────────────── */
function initSidebar() {
  const sidebar   = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  const mobileBtn = document.getElementById('mobileMenuBtn');
  if (!sidebar) return;
  if (localStorage.getItem('sidebar_collapsed') === '1') sidebar.classList.add('collapsed');
  toggleBtn?.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebar_collapsed', sidebar.classList.contains('collapsed') ? '1' : '0');
  });
  mobileBtn?.addEventListener('click', () => sidebar.classList.toggle('mobile-open'));
  document.addEventListener('click', e => {
    if (window.innerWidth <= 768 && !sidebar.contains(e.target) && e.target !== mobileBtn)
      sidebar.classList.remove('mobile-open');
  });
}

/* ── Helpers ─────────────────────────────────────────────────── */
function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric' });
}
function formatSize(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024*1024) return `${(bytes/1024).toFixed(1)} KB`;
  return `${(bytes/(1024*1024)).toFixed(1)} MB`;
}
function fileIconClass(type) {
  return { pdf:'pdf', docx:'docx', txt:'txt', png:'png', jpg:'jpg', jpeg:'jpg' }[type] || 'txt';
}
function fileIconLabel(type) {
  return { pdf:'PDF', docx:'DOC', txt:'TXT', png:'PNG', jpg:'JPG', jpeg:'JPG' }[type] || (type||'?').toUpperCase();
}
function statusBadge(status) {
  const cls  = { pending:'status-pending', processing:'status-processing', completed:'status-completed', failed:'status-failed' };
  const icon = { pending:'fa-clock', processing:'fa-spinner fa-spin', completed:'fa-check', failed:'fa-xmark' };
  return `<span class="badge ${cls[status]||'badge-secondary'}"><i class="fa-solid ${icon[status]||'fa-circle'}"></i> ${status||'—'}</span>`;
}
function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function setLoading(el, loading, text = '') {
  if (!el) return;
  if (loading) { el.dataset.origHtml = el.innerHTML; el.disabled = true; el.innerHTML = `<span class="spinner"></span> ${text||'Loading…'}`; }
  else          { el.disabled = false; el.innerHTML = el.dataset.origHtml || 'Submit'; }
}
function showFormError(fieldId, msg) {
  const e = document.getElementById(`${fieldId}Error`);
  if (e) { e.textContent = msg; e.classList.add('visible'); }
  const i = document.getElementById(fieldId);
  if (i) i.classList.add('error');
}
function clearFormErrors(formEl) {
  formEl?.querySelectorAll('.form-error').forEach(e => { e.textContent = ''; e.classList.remove('visible'); });
  formEl?.querySelectorAll('.form-control.error').forEach(e => e.classList.remove('error'));
}
function buildDocCard(doc) {
  const cls   = fileIconClass(doc.file_type);
  const label = fileIconLabel(doc.file_type);
  return `<div class="doc-card" onclick="window.location.href='/documents/${doc.id}/'">
    <div class="doc-card-header">
      <div class="file-icon ${cls}">${label}</div>
      <div style="flex:1">
        <div class="doc-card-title">${escHtml(doc.title)}</div>
        <div class="doc-card-meta">
          ${statusBadge(doc.processing_status)}
          ${doc.category_name?`<span class="badge badge-secondary">${escHtml(doc.category_name)}</span>`:''}
        </div>
      </div>
    </div>
    ${doc.description?`<div class="doc-card-desc">${escHtml(doc.description)}</div>`:''}
    ${doc.tags&&doc.tags.length?`<div class="tag-list">${doc.tags.slice(0,4).map(t=>`<span class="tag-chip">${escHtml(t.name)}</span>`).join('')}</div>`:''}
    <div class="doc-card-footer">
      <span class="doc-date"><i class="fa-regular fa-calendar"></i> ${formatDate(doc.upload_date)}</span>
      <span class="text-muted text-sm">${doc.file_size_display||''}</span>
    </div>
  </div>`;
}

/* ── Global init ─────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  initLogout();
  if (document.getElementById('sidebar')) hydrateSidebar();
});
