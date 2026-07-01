/* ═══════════════════════════════════════════════════
   MOOD RECOMMENDER — Frontend Application
   ═══════════════════════════════════════════════════ */

// ── Theme Management ──
class ThemeManager {
  constructor() {
    this.storageKey = 'mood-recommender-theme';
    this.darkMode = localStorage.getItem(this.storageKey) === 'true';
    this.init();
  }

  init() {
    if (this.darkMode) document.body.classList.add('dark-mode');
    document.getElementById('themeToggle').addEventListener('click', () => this.toggle());
  }

  toggle() {
    this.darkMode = !this.darkMode;
    document.body.classList.toggle('dark-mode');
    localStorage.setItem(this.storageKey, this.darkMode);
    document.dispatchEvent(new CustomEvent('themechange', { detail: { dark: this.darkMode } }));
  }
}

// ── API Service ──
class APIService {
  constructor(baseURL = '') {
    this.baseURL = baseURL || '';
  }

  async analyze(text, model) {
    const body = { text: text.trim() };
    if (model) body.model = model;
    const res = await fetch(`${this.baseURL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || 'Analysis failed');
    }
    return res.json();
  }

  async getHealth() {
    try {
      const res = await fetch(`${this.baseURL}/api/health`);
      return res.ok;
    } catch { return false; }
  }

  async getMoodHistory() {
    try {
      const res = await fetch(`${this.baseURL}/api/mood-history`);
      if (!res.ok) throw new Error();
      return res.json();
    } catch { return { success: false, history: [] }; }
  }
}

// ── Mood Color Map ──
const MOOD_COLORS = {
  'Happy':     { accent: '#f59e0b', glow: 'rgba(245,158,11,0.25)' },
  'Joyful':    { accent: '#10b981', glow: 'rgba(16,185,129,0.25)' },
  'Neutral':   { accent: '#6366f1', glow: 'rgba(99,102,241,0.25)' },
  'Sad':       { accent: '#8b5cf6', glow: 'rgba(139,92,246,0.25)' },
  'Depressed': { accent: '#e11d48', glow: 'rgba(225,29,72,0.25)' },
};

// ── Recommendation Renderer ──
class RecommendationRenderer {

  static renderMoodCard(data) {
    // Content
    document.getElementById('moodEmoji').textContent = data.emoji;
    document.getElementById('moodTitle').textContent = data.mood;
    document.getElementById('moodDescription').textContent = data.description;
    document.getElementById('sentimentScore').textContent = data.sentiment_score.toFixed(2);
    document.getElementById('confidence').textContent = Math.round(data.confidence * 100) + '%';

    const badge = document.getElementById('modelBadge');
    badge.textContent = data.model || 'VADER';

    // Mood-reactive background
    const card = document.getElementById('moodCard');
    const mood = data.mood;
    card.className = 'mood-result mood-bg-' + mood + ' mood-glow-' + mood;

    // Set ambient body glow
    const color = MOOD_COLORS[mood] || MOOD_COLORS['Neutral'];
    document.body.style.setProperty('--mood-glow', color.accent);
    document.body.classList.add('has-mood');
  }

  static renderSongs(songs) {
    const container = document.getElementById('songsContainer');
    container.innerHTML = '';
    const filterBar = document.getElementById('songsFilterBar');
    filterBar.innerHTML = '';

    if (songs.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);font-size:0.9rem;">No songs available for this mood.</p>';
      return;
    }

    const genres = [...new Set(songs.map(s => s.genre).filter(Boolean))];
    if (genres.length > 1) filterBar.appendChild(this.createFilterBar(genres, 'song'));

    songs.forEach((song, i) => {
      const card = this.createSongCard(song);
      card.style.animationDelay = (i * 80) + 'ms';
      container.appendChild(card);
    });
  }

  static renderMovies(movies) {
    const container = document.getElementById('moviesContainer');
    container.innerHTML = '';
    const filterBar = document.getElementById('moviesFilterBar');
    filterBar.innerHTML = '';

    if (movies.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);font-size:0.9rem;">No movies available for this mood.</p>';
      return;
    }

    const genres = [...new Set(movies.map(m => m.genre).filter(Boolean))];
    if (genres.length > 1) filterBar.appendChild(this.createFilterBar(genres, 'movie'));

    movies.forEach((movie, i) => {
      const card = this.createMovieCard(movie);
      card.style.animationDelay = (i * 80) + 'ms';
      container.appendChild(card);
    });
  }

  static createFilterBar(genres, type) {
    const bar = document.createElement('div');
    bar.className = 'genre-filter-bar';

    const allBtn = document.createElement('button');
    allBtn.className = 'genre-chip active';
    allBtn.textContent = 'All';
    allBtn.dataset.genre = 'all';
    allBtn.dataset.type = type;
    bar.appendChild(allBtn);

    genres.forEach(g => {
      const btn = document.createElement('button');
      btn.className = 'genre-chip';
      btn.textContent = g;
      btn.dataset.genre = g;
      btn.dataset.type = type;
      bar.appendChild(btn);
    });

    bar.addEventListener('click', e => {
      const chip = e.target.closest('.genre-chip');
      if (!chip) return;
      bar.querySelectorAll('.genre-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      const sel = chip.dataset.genre;
      const ctr = document.getElementById(type === 'song' ? 'songsContainer' : 'moviesContainer');
      ctr.querySelectorAll('[data-genre]').forEach(c => {
        c.style.display = (sel === 'all' || c.dataset.genre === sel) ? '' : 'none';
      });
    });

    return bar;
  }

  static createSongCard(song) {
    const div = document.createElement('div');
    div.className = 'col-6';
    div.dataset.genre = song.genre || 'Other';

    const spotifyLink = song.spotify_link
      ? `<a href="${song.spotify_link}" target="_blank" class="btn-spotify"><i class="fab fa-spotify"></i> Spotify</a>`
      : '';

    div.innerHTML = `
      <div class="rec-card song-card">
        <div class="card-head mood-bg-${song.mood}">
          <i class="fas fa-music"></i>
          <span class="text-truncate">${this.esc(song.title)}</span>
        </div>
        <div class="card-body">
          <h6 title="${this.esc(song.artist)}">${this.esc(song.artist)}</h6>
          <div class="sub">${this.esc(song.genre || '')}</div>
          <div class="card-actions">
            <span class="badge-mood mood-bg-${song.mood}">${song.mood}</span>
            ${spotifyLink}
          </div>
        </div>
      </div>`;
    return div;
  }

  static createMovieCard(movie) {
    const div = document.createElement('div');
    div.className = 'col-6';
    div.dataset.genre = movie.genre || 'Other';

    const poster = movie.poster_url
      ? `<div class="movie-poster-wrap"><img src="${movie.poster_url}" alt="${this.esc(movie.title)}" class="movie-poster" loading="lazy"></div>`
      : '';

    const rating = movie.imdb_rating
      ? `<span class="rating-star"><i class="fas fa-star"></i> ${movie.imdb_rating}</span>`
      : '';

    const trailerBtn = movie.trailer_url
      ? `<a href="${this.esc(movie.trailer_url)}" target="_blank" class="btn-trailer-movie"><i class="fab fa-youtube"></i> Trailer</a>`
      : `<button class="btn-trailer-movie trailer-loading" data-movie-id="${movie.id}" data-movie-title="${this.esc(movie.title)}"><i class="fab fa-youtube"></i> Trailer</button>`;

    div.innerHTML = `
      <div class="rec-card movie-card">
        ${poster}
        <div class="card-body">
          <h6 title="${this.esc(movie.title)}">${this.esc(movie.title)}</h6>
          <div class="sub">${this.esc(movie.genre)} ${rating ? '· ' + rating : ''}</div>
          <div class="card-actions">
            <span class="badge-mood mood-bg-${movie.mood}">${movie.mood}</span>
            ${trailerBtn}
          </div>
        </div>
      </div>`;
    return div;
  }

  static showResults() {
    const section = document.getElementById('resultsSection');
    section.classList.remove('d-none');
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  static hideResults() {
    document.getElementById('resultsSection').classList.add('d-none');
    document.body.classList.remove('has-mood');
  }

  static esc(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }
}

// ── UI Controller ──
class UIController {
  constructor(api) {
    this.api = api;
    this._moodChart = null;
    this.init();
  }

  init() {
    document.getElementById('moodForm').addEventListener('submit', e => this.handleSubmit(e));
    document.getElementById('searchAgainBtn').addEventListener('click', () => this.handleSearchAgain());
    document.getElementById('shareResultsBtn').addEventListener('click', () => this.handleShare());
    document.getElementById('moodInput').addEventListener('input', e => this.updateCharCount(e));

    document.querySelectorAll('.chip').forEach(chip => {
      chip.addEventListener('click', () => this.handleChipClick(chip));
    });

    document.getElementById('modelSwitch').addEventListener('change', e => {
      document.getElementById('vaderLabel').classList.toggle('active', !e.target.checked);
      document.getElementById('hfLabel').classList.toggle('active', e.target.checked);
    });

    document.addEventListener('themechange', () => {
      if (this._moodChart) this.renderMoodChart();
    });

    // Trailer delegation
    document.addEventListener('click', async e => {
      const btn = e.target.closest('.trailer-loading');
      if (!btn) return;
      btn.disabled = true;
      btn.innerHTML = '<i class="fas fa-circle-notch fa-spin"></i> Loading...';
      try {
        const res = await fetch(`/api/trailer/${btn.dataset.movieId}`);
        const data = await res.json();
        if (data.success && data.trailer_url) {
          window.open(data.trailer_url, '_blank');
          btn.outerHTML = `<a href="${data.trailer_url}" target="_blank" class="btn-trailer-movie"><i class="fab fa-youtube"></i> Trailer</a>`;
        } else {
          btn.textContent = 'Not found';
        }
      } catch { btn.textContent = 'Error'; }
    });
  }

  getModel() {
    return document.getElementById('modelSwitch').checked ? 'huggingface' : 'vader';
  }

  updateCharCount(e) {
    document.getElementById('charCount').textContent = e.target.value.length;
  }

  async handleChipClick(chip) {
    const input = document.getElementById('moodInput');
    input.value = chip.dataset.text;
    this.updateCharCount({ target: input });
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    chip.disabled = true;
    try { await this.handleSubmit(new Event('submit', { cancelable: true })); }
    finally { chip.disabled = false; }
  }

  async handleSubmit(e) {
    e.preventDefault();
    const text = document.getElementById('moodInput').value.trim();
    if (!text) {
      this.showError('Write how you feel, or pick a quick mood above.');
      return;
    }
    this.setLoading(true);
    this.clearError();
    try {
      const result = await this.api.analyze(text, this.getModel());
      if (result.success) {
        RecommendationRenderer.renderMoodCard(result);
        RecommendationRenderer.renderSongs(result.songs);
        RecommendationRenderer.renderMovies(result.movies);
        RecommendationRenderer.showResults();
        this.renderMoodChart();
      } else {
        this.showError(result.error || 'Analysis failed.');
      }
    } catch (err) {
      this.showError(err.message || 'Something went wrong.');
    } finally {
      this.setLoading(false);
    }
  }

  handleSearchAgain() {
    document.getElementById('moodInput').value = '';
    document.getElementById('charCount').textContent = '0';
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    if (this._moodChart) { this._moodChart.destroy(); this._moodChart = null; }
    RecommendationRenderer.hideResults();
    document.getElementById('moodInput').focus();
  }

  handleShare() {
    const mood = document.getElementById('moodTitle').textContent;
    const score = document.getElementById('sentimentScore').textContent;
    const text = `I just checked my mood and I'm feeling ${mood} (${score})! 🎵🎬`;
    if (navigator.share) {
      navigator.share({ title: 'My Mood', text, url: window.location.href }).catch(() => {});
    } else {
      navigator.clipboard.writeText(text).then(() => alert('Copied to clipboard!')).catch(() => {});
    }
  }

  async renderMoodChart() {
    const result = await this.api.getMoodHistory();
    const el = document.getElementById('historyCount');
    if (!result.success || !result.history || result.history.length === 0) {
      el.textContent = 'No entries yet';
      return;
    }
    const canvas = document.getElementById('moodChart');
    if (this._moodChart) this._moodChart.destroy();

    const dates = result.history.map(h => h.date).reverse();
    const moods = ['Happy', 'Joyful', 'Neutral', 'Sad', 'Depressed'];
    const colors = { 'Happy': '#f59e0b', 'Joyful': '#10b981', 'Neutral': '#6366f1', 'Sad': '#8b5cf6', 'Depressed': '#e11d48' };
    const datasets = moods.map(m => ({
      label: m,
      data: result.history.map(h => h.moods[m] || 0).reverse(),
      backgroundColor: colors[m],
      borderColor: colors[m],
      borderWidth: 1,
      borderRadius: 3,
    }));

    el.textContent = result.history.reduce((s, d) => s + d.total, 0) + ' total entries';

    const isDark = document.body.classList.contains('dark-mode');
    const tc = isDark ? '#94a3b8' : '#64748b';
    const gc = isDark ? 'rgba(148,163,184,0.1)' : 'rgba(0,0,0,0.06)';

    this._moodChart = new Chart(canvas, {
      type: 'bar',
      data: { labels: dates, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12, font: { size: 11, color: tc }, color: tc } },
        },
        scales: {
          x: { stacked: true, ticks: { font: { size: 10, color: tc }, maxTicksLimit: 8, color: tc }, grid: { display: false } },
          y: { stacked: true, beginAtZero: true, ticks: { font: { size: 10, color: tc }, stepSize: 1, precision: 0, color: tc }, grid: { color: gc } },
        },
      },
    });
  }

  setLoading(on) {
    document.getElementById('loadingAnimation').classList.toggle('d-none', !on);
    document.getElementById('analyzeBtn').disabled = on;
  }

  showError(msg) {
    const alert = document.getElementById('errorAlert');
    document.getElementById('errorMessage').textContent = msg;
    alert.classList.remove('d-none');
    alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  clearError() {
    document.getElementById('errorAlert').classList.add('d-none');
  }
}

// ── Init ──
document.addEventListener('DOMContentLoaded', async () => {
  console.log('Initializing Mood Recommender...');
  new ThemeManager();
  const api = new APIService();
  const healthy = await api.getHealth();
  if (!healthy) console.warn('API health check failed');
  new UIController(api);
  console.log('Ready.');
});
