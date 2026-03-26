const API = 'http://localhost:5000';
const TMDB_IMG = 'https://image.tmdb.org/t/p/w300';

let token = localStorage.getItem('token');
let currentUser = localStorage.getItem('username');
let rateTarget = null;
let selectedRating = 0;

// ── API helper ──────────────────────────────────────────────────────────────

async function api(method, path, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API}${path}`, opts);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
}

// ── Auth ────────────────────────────────────────────────────────────────────

function updateAuthUI() {
    const loggedIn = !!token;
    document.getElementById('login-btn').classList.toggle('hidden', loggedIn);
    document.getElementById('register-btn').classList.toggle('hidden', loggedIn);
    document.getElementById('logout-btn').classList.toggle('hidden', !loggedIn);
    document.getElementById('username-display').textContent = loggedIn ? currentUser : '';
}

function saveAuth(data) {
    token = data.token;
    currentUser = data.username;
    localStorage.setItem('token', token);
    localStorage.setItem('username', currentUser);
    updateAuthUI();
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    updateAuthUI();
}

// ── Tabs ────────────────────────────────────────────────────────────────────

function showTab(name) {
    document.querySelectorAll('.tab').forEach(t =>
        t.classList.toggle('active', t.dataset.tab === name)
    );
    document.querySelectorAll('.tab-content').forEach(s => {
        const active = s.id === `tab-${name}`;
        s.classList.toggle('hidden', !active);
    });
    if (name === 'watchlist') loadWatchlist();
    if (name === 'history')   loadHistory();
    if (name === 'ratings')   loadRatings();
}

// ── Search ──────────────────────────────────────────────────────────────────

async function doSearch() {
    const q = document.getElementById('search-input').value.trim();
    if (!q) return;
    const container = document.getElementById('search-results');
    container.innerHTML = '<p class="empty-msg">Searching…</p>';
    try {
        const results = await api('GET', `/api/media/search?q=${encodeURIComponent(q)}`);
        if (!results.length) {
            container.innerHTML = '<p class="empty-msg">No results found.</p>';
            return;
        }
        container.innerHTML = results.map(mediaCard).join('');
    } catch (e) {
        container.innerHTML = `<p class="empty-msg">${e.message}</p>`;
    }
}

function esc(str) {
    return (str || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
}

function posterImg(posterPath, title) {
    return posterPath
        ? `<img src="${TMDB_IMG}${posterPath}" alt="${title}" loading="lazy">`
        : `<div class="no-poster">${title}</div>`;
}

function mediaCard(m) {
    const year = (m.release_date || '').slice(0, 4);
    const typeLabel = m.media_type === 'tv' ? 'TV' : 'Movie';
    return `
        <div class="media-card">
            ${posterImg(m.poster_path, m.title)}
            <div class="card-info">
                <div class="card-title">${m.title}</div>
                <div class="card-meta">
                    <span class="badge ${m.media_type}">${typeLabel}</span>${year}
                </div>
                <div class="card-actions">
                    <button class="btn-primary"
                        onclick="addToWatchlist(${m.tmdb_id},'${m.media_type}','${esc(m.title)}')">
                        + Watchlist
                    </button>
                    <button onclick="addToHistory(${m.tmdb_id},'${m.media_type}','${esc(m.title)}')">
                        Mark Watched
                    </button>
                    <button onclick="openRateModal(${m.tmdb_id},'${m.media_type}','${esc(m.title)}')">
                        Rate
                    </button>
                </div>
            </div>
        </div>`;
}

// ── Watchlist ───────────────────────────────────────────────────────────────

async function addToWatchlist(tmdb_id, media_type, title) {
    if (!token) { alert('Please log in first.'); return; }
    try {
        await api('POST', '/api/watchlist', { tmdb_id, media_type, status: 'plan_to_watch' });
        alert(`"${title}" added to watchlist.`);
    } catch (e) {
        alert(e.message);
    }
}

async function loadWatchlist() {
    const container = document.getElementById('watchlist-content');
    if (!token) {
        container.innerHTML = '<p class="empty-msg">Log in to view your watchlist.</p>';
        return;
    }
    try {
        const entries = await api('GET', '/api/watchlist');
        container.innerHTML = entries.length
            ? entries.map(watchlistItem).join('')
            : '<p class="empty-msg">Your watchlist is empty.</p>';
    } catch (e) {
        container.innerHTML = `<p class="empty-msg">${e.message}</p>`;
    }
}

function watchlistItem(e) {
    const m = e.media;
    const statuses = ['plan_to_watch', 'watching', 'completed', 'on_hold', 'dropped'];
    const opts = statuses
        .map(s => `<option value="${s}"${s === e.status ? ' selected' : ''}>${s.replace(/_/g, ' ')}</option>`)
        .join('');
    return `
        <div class="list-item" id="wl-${e.id}">
            ${posterImg(m.poster_path, m.title)}
            <div class="item-info">
                <div class="item-title">${m.title}</div>
                <div class="item-meta"><span class="badge ${m.media_type}">${m.media_type === 'tv' ? 'TV' : 'Movie'}</span></div>
                <div class="item-actions">
                    <select onchange="updateWatchlistStatus(${e.id}, this.value)">${opts}</select>
                    <button class="btn-rate" onclick="openRateModal(${m.tmdb_id},'${m.media_type}','${esc(m.title)}')">Rate</button>
                    <button class="btn-remove" onclick="removeFromWatchlist(${e.id})">Remove</button>
                </div>
            </div>
        </div>`;
}

async function updateWatchlistStatus(id, status) {
    try {
        await api('PUT', `/api/watchlist/${id}`, { status });
    } catch (e) {
        alert(e.message);
    }
}

async function removeFromWatchlist(id) {
    try {
        await api('DELETE', `/api/watchlist/${id}`);
        document.getElementById(`wl-${id}`)?.remove();
    } catch (e) {
        alert(e.message);
    }
}

// ── History ─────────────────────────────────────────────────────────────────

async function addToHistory(tmdb_id, media_type, title) {
    if (!token) { alert('Please log in first.'); return; }
    try {
        await api('POST', '/api/history', { tmdb_id, media_type });
        alert(`"${title}" added to history.`);
    } catch (e) {
        alert(e.message);
    }
}

async function loadHistory() {
    const container = document.getElementById('history-content');
    if (!token) {
        container.innerHTML = '<p class="empty-msg">Log in to view your history.</p>';
        return;
    }
    try {
        const entries = await api('GET', '/api/history');
        container.innerHTML = entries.length
            ? entries.map(historyItem).join('')
            : '<p class="empty-msg">No watch history yet.</p>';
    } catch (e) {
        container.innerHTML = `<p class="empty-msg">${e.message}</p>`;
    }
}

function historyItem(e) {
    const m = e.media;
    const date = new Date(e.watched_at).toLocaleDateString();
    return `
        <div class="list-item" id="hist-${e.id}">
            ${posterImg(m.poster_path, m.title)}
            <div class="item-info">
                <div class="item-title">${m.title}</div>
                <div class="item-meta">
                    <span class="badge ${m.media_type}">${m.media_type === 'tv' ? 'TV' : 'Movie'}</span>
                    Watched ${date}
                </div>
                <div class="item-actions">
                    <button class="btn-rate" onclick="openRateModal(${m.tmdb_id},'${m.media_type}','${esc(m.title)}')">Rate</button>
                    <button class="btn-remove" onclick="removeFromHistory(${e.id})">Remove</button>
                </div>
            </div>
        </div>`;
}

async function removeFromHistory(id) {
    try {
        await api('DELETE', `/api/history/${id}`);
        document.getElementById(`hist-${id}`)?.remove();
    } catch (e) {
        alert(e.message);
    }
}

// ── Ratings ─────────────────────────────────────────────────────────────────

function openRateModal(tmdb_id, media_type, title) {
    if (!token) { alert('Please log in first.'); return; }
    rateTarget = { tmdb_id, media_type };
    selectedRating = 0;
    document.getElementById('rate-title').textContent = title;
    document.getElementById('rate-review').value = '';
    document.getElementById('rate-error').classList.add('hidden');
    document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
    document.getElementById('rate-modal').classList.remove('hidden');
}

async function submitRating() {
    if (!selectedRating) {
        showError('rate-error', 'Please select a star rating.');
        return;
    }
    const review = document.getElementById('rate-review').value.trim();
    try {
        await api('POST', '/api/ratings', { ...rateTarget, rating: selectedRating, review });
        document.getElementById('rate-modal').classList.add('hidden');
        alert('Rating submitted!');
    } catch (e) {
        showError('rate-error', e.message);
    }
}

async function loadRatings() {
    const container = document.getElementById('ratings-content');
    if (!token) {
        container.innerHTML = '<p class="empty-msg">Log in to view your ratings.</p>';
        return;
    }
    try {
        const entries = await api('GET', '/api/ratings');
        container.innerHTML = entries.length
            ? entries.map(ratingItem).join('')
            : '<p class="empty-msg">No ratings yet.</p>';
    } catch (e) {
        container.innerHTML = `<p class="empty-msg">${e.message}</p>`;
    }
}

function ratingItem(e) {
    const m = e.media;
    const stars = '★'.repeat(e.rating) + '☆'.repeat(5 - e.rating);
    return `
        <div class="list-item" id="rat-${e.id}">
            ${posterImg(m.poster_path, m.title)}
            <div class="item-info">
                <div class="item-title">${m.title}</div>
                <div class="item-meta"><span class="badge ${m.media_type}">${m.media_type === 'tv' ? 'TV' : 'Movie'}</span></div>
                <div class="stars">${stars}</div>
                ${e.review ? `<div class="review-text">${e.review}</div>` : ''}
                <div class="item-actions" style="margin-top:0.5rem">
                    <button class="btn-remove" onclick="deleteRating(${e.id})">Delete</button>
                </div>
            </div>
        </div>`;
}

async function deleteRating(id) {
    try {
        await api('DELETE', `/api/ratings/${id}`);
        document.getElementById(`rat-${id}`)?.remove();
    } catch (e) {
        alert(e.message);
    }
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function showError(id, msg) {
    const el = document.getElementById(id);
    el.textContent = msg;
    el.classList.remove('hidden');
}

function closeModal(modal) {
    modal.classList.add('hidden');
}

// ── Bootstrap ────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();

    // Tabs
    document.querySelectorAll('.tab').forEach(t =>
        t.addEventListener('click', () => showTab(t.dataset.tab))
    );

    // Search
    document.getElementById('search-btn').addEventListener('click', doSearch);
    document.getElementById('search-input').addEventListener('keydown', e => {
        if (e.key === 'Enter') doSearch();
    });

    // Auth buttons
    document.getElementById('login-btn').addEventListener('click', () =>
        document.getElementById('login-modal').classList.remove('hidden')
    );
    document.getElementById('register-btn').addEventListener('click', () =>
        document.getElementById('register-modal').classList.remove('hidden')
    );
    document.getElementById('logout-btn').addEventListener('click', logout);

    // Login submit
    document.getElementById('login-submit').addEventListener('click', async () => {
        const username = document.getElementById('login-username').value.trim();
        const password = document.getElementById('login-password').value;
        try {
            const data = await api('POST', '/api/auth/login', { username, password });
            saveAuth(data);
            closeModal(document.getElementById('login-modal'));
        } catch (e) {
            showError('login-error', e.message);
        }
    });

    // Register submit
    document.getElementById('reg-submit').addEventListener('click', async () => {
        const username = document.getElementById('reg-username').value.trim();
        const email    = document.getElementById('reg-email').value.trim();
        const password = document.getElementById('reg-password').value;
        try {
            const data = await api('POST', '/api/auth/register', { username, email, password });
            saveAuth(data);
            closeModal(document.getElementById('register-modal'));
        } catch (e) {
            showError('reg-error', e.message);
        }
    });

    // Close modals
    document.querySelectorAll('.modal-close').forEach(btn =>
        btn.addEventListener('click', () => closeModal(btn.closest('.modal')))
    );

    // Close modal on backdrop click
    document.querySelectorAll('.modal').forEach(modal =>
        modal.addEventListener('click', e => { if (e.target === modal) closeModal(modal); })
    );

    // Star rating
    document.querySelectorAll('.star').forEach(star =>
        star.addEventListener('click', () => {
            selectedRating = parseInt(star.dataset.value);
            document.querySelectorAll('.star').forEach(s =>
                s.classList.toggle('active', parseInt(s.dataset.value) <= selectedRating)
            );
        })
    );

    // Rate submit
    document.getElementById('rate-submit').addEventListener('click', submitRating);
});
