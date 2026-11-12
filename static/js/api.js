/**
 * DocuVault AI — API Client
 * All backend communication goes through this module.
 */
const API = {
  getToken()  { return localStorage.getItem('access_token'); },
  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    if (refresh) localStorage.setItem('refresh_token', refresh);
  },
  clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
  },
  headers(isFormData = false) {
    const h = {};
    const token = this.getToken();
    if (token) h['Authorization'] = `Bearer ${token}`;
    if (!isFormData) h['Content-Type'] = 'application/json';
    return h;
  },
  async request(method, url, body = null, isFormData = false) {
    const opts = { method, headers: this.headers(isFormData) };
    if (body) opts.body = isFormData ? body : JSON.stringify(body);
    let res = await fetch(url, opts);
    if (res.status === 401) {
      const refreshed = await this.refreshToken();
      if (refreshed) { opts.headers = this.headers(isFormData); res = await fetch(url, opts); }
      else { this.clearAuth(); window.location.href = '/login/'; return null; }
    }
    return res;
  },
  async refreshToken() {
    const refresh = localStorage.getItem('refresh_token');
    if (!refresh) return false;
    try {
      const res = await fetch('/api/auth/token/refresh/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (res.ok) { const d = await res.json(); localStorage.setItem('access_token', d.access); return true; }
    } catch {}
    return false;
  },
  async get(url)            { return this.request('GET', url); },
  async post(url, body)     { return this.request('POST', url, body); },
  async patch(url, body)    { return this.request('PATCH', url, body); },
  async del(url)            { return this.request('DELETE', url); },
  async upload(url, fd)     { return this.request('POST', url, fd, true); },
  async json(res) {
    if (!res) return null;
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  },

  /* Auth */
  async login(username, password)  { return this.json(await this.post('/api/auth/login/', { username, password })); },
  async register(payload)          { return this.json(await this.post('/api/auth/register/', payload)); },
  async logout()                   { const r = localStorage.getItem('refresh_token'); await this.post('/api/auth/logout/', { refresh: r }); this.clearAuth(); },
  async me()                       { return this.json(await this.get('/api/auth/me/')); },
  async updateProfile(payload)     { return this.json(await this.patch('/api/auth/me/', payload)); },
  async listUsers()                { return this.json(await this.get('/api/users/')); },

  /* Documents */
  async listDocuments(params = {}) { const qs = new URLSearchParams(params).toString(); return this.json(await this.get(`/api/documents/${qs ? '?' + qs : ''}`)); },
  async getDocument(id)            { return this.json(await this.get(`/api/documents/${id}/`)); },
  async uploadDocument(fd)         { return this.json(await this.upload('/api/documents/', fd)); },
  async updateDocument(id, p)      { return this.json(await this.patch(`/api/documents/${id}/`, p)); },
  async deleteDocument(id)         { const r = await this.del(`/api/documents/${id}/`); return { ok: r.ok, status: r.status }; },
  async downloadDocument(id)       { return this.get(`/api/documents/${id}/download/`); },
  async getDocumentText(id)        { return this.json(await this.get(`/api/documents/${id}/text/`)); },
  async processDocument(id)        { return this.json(await this.post(`/api/documents/${id}/process/`, {})); },
  async getDocumentStatus(id)      { return this.json(await this.get(`/api/documents/${id}/status/`)); },

  /* Categories & Tags */
  async listCategories()           { return this.json(await this.get('/api/categories/')); },
  async listTags()                 { return this.json(await this.get('/api/tags/')); },

  /* Search */
  async search(params = {})        { const qs = new URLSearchParams(params).toString(); return this.json(await this.get(`/api/search/?${qs}`)); },

  /* AI */
  async summarize(id, force = false) { return this.json(await this.post(`/api/documents/${id}/summarize/`, { force_regenerate: force })); },
  async getSummary(id)             { return this.json(await this.get(`/api/documents/${id}/summary/`)); },
  async generateTags(id)           { return this.json(await this.post(`/api/documents/${id}/generate-tags/`, {})); },

  /* Dashboard */
  async dashboardStats()           { return this.json(await this.get('/api/dashboard/stats/')); },
  async recentDocuments(limit = 8) { return this.json(await this.get(`/api/dashboard/recent-documents/?limit=${limit}`)); },
};
