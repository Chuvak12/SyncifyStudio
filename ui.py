from config import CURRENT_VERSION

HTML_UI = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Syncify Studio</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #090A0E;
    --card: #12141C;
    --card-hover: #181B26;
    --border: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(255, 255, 255, 0.16);
    --text-main: #FFFFFF;
    --text-muted: #8E92A4;
    --text-dim: #515465;
    --accent: #1ED760;
    --accent-glow: rgba(30, 215, 96, 0.25);
    --danger: #EF4444;
  }}

  [data-theme="linear"] {{ --accent: #6366F1; --accent-glow: rgba(99, 102, 241, 0.25); }}
  [data-theme="cyberpunk"] {{ --accent: #F59E0B; --accent-glow: rgba(245, 158, 11, 0.25); }}
  [data-theme="cyan"] {{ --accent: #06B6D4; --accent-glow: rgba(6, 182, 212, 0.25); }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
  html, body {{ height: 100%; width: 100%; background-color: var(--bg); color: var(--text-main); font-family: 'Inter', sans-serif; overflow: hidden; }}
  ::-webkit-scrollbar {{ width: 6px; }}
  ::-webkit-scrollbar-track {{ background: transparent; }}
  ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.12); border-radius: 10px; }}
  ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.25); }}

  .app-layout {{ display: flex; flex-direction: column; height: 100vh; padding: 16px 22px; gap: 11px; max-width: 1400px; margin: 0 auto; width: 100%; }}
  .header {{ display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }}
  .brand {{ display: flex; align-items: center; gap: 10px; }}
  .brand-icon {{ width: 28px; height: 28px; background: linear-gradient(135deg, var(--accent), #108A3B); border-radius: 8px; display: grid; place-items: center; box-shadow: 0 0 16px var(--accent-glow); font-size: 14px; font-weight: 900; }}
  .brand-title {{ font-size: 18px; font-weight: 700; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; }}
  .brand-badge {{ font-size: 10px; background: rgba(255, 255, 255, 0.06); border: 1px solid var(--border); padding: 2px 6px; border-radius: 6px; color: var(--text-muted); font-weight: 600; }}
  .update-chip {{ display: none; align-items: center; gap: 6px; background: linear-gradient(135deg, #10B981, #059669); color: #FFF; font-size: 11px; font-weight: 700; padding: 6px 12px; border-radius: 20px; cursor: pointer; box-shadow: 0 0 16px rgba(16, 185, 129, 0.4); }}
  .header-actions {{ display: flex; align-items: center; gap: 8px; }}
  .status-pill {{ display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 20px; background: var(--card); border: 1px solid var(--border); }}
  .status-dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--text-dim); }}
  .status-pill.online .status-dot {{ background: var(--accent); box-shadow: 0 0 8px var(--accent); }}

  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 11px 15px; flex-shrink: 0; }}
  .input-row {{ display: flex; align-items: center; gap: 10px; background: rgba(0, 0, 0, 0.35); border: 1px solid var(--border); border-radius: 10px; padding: 4px 10px; margin-bottom: 6px; }}
  .input-row:last-child {{ margin-bottom: 0; }}
  .input-tag {{ font-size: 10px; font-weight: 700; color: var(--text-muted); width: 70px; }}
  .input-field {{ flex: 1; background: transparent; border: none; outline: none; color: #FFF; font-family: inherit; font-size: 13px; padding: 6px 0; }}

  .btn-open-link {{ font-size: 12px; padding: 4px 8px; background: rgba(255,255,255,0.05); border-radius: 6px; color: var(--text-muted); border: 1px solid var(--border); }}
  .btn-open-link:hover {{ color: var(--text-main); background: rgba(255,255,255,0.1); }}

  button {{ font-family: inherit; border: none; cursor: pointer; transition: all 0.15s cubic-bezier(0.16, 1, 0.3, 1); }}
  button:active {{ transform: scale(0.97); }}
  .btn-ghost {{ background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); color: var(--text-main); padding: 7px 13px; border-radius: 8px; font-size: 12px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
  .btn-ghost:hover {{ background: var(--card-hover); }}
  .btn-primary {{ background: var(--accent); color: #000; font-weight: 700; font-size: 13px; padding: 8px 16px; border-radius: 8px; box-shadow: 0 0 20px var(--accent-glow); }}
  .btn-primary:hover {{ filter: brightness(1.1); }}
  .btn-quick {{ background: linear-gradient(135deg, #F59E0B, #D97706); color: #000; font-weight: 700; font-size: 13px; padding: 11px 18px; border-radius: 10px; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 0 20px rgba(245, 158, 11, 0.25); flex: 1; }}
  .btn-sync {{ background: linear-gradient(135deg, var(--accent), #15803D); color: #000; font-weight: 700; font-size: 13px; padding: 11px 18px; border-radius: 10px; display: flex; align-items: center; justify-content: center; gap: 8px; box-shadow: 0 0 20px var(--accent-glow); flex: 1; }}

  .insights-banner {{ display: none; align-items: center; gap: 8px; background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border); border-radius: 8px; padding: 6px 12px; font-size: 11px; color: var(--text-muted); margin-bottom: 6px; }}
  .insights-accent {{ color: var(--accent); font-weight: 600; }}

  .tracklist-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 11px 15px; flex: 1; display: flex; flex-direction: column; min-height: 160px; overflow: hidden; }}
  .tracklist-toolbar {{ display: flex; align-items: center; gap: 8px; margin-bottom: 7px; flex-shrink: 0; }}
  .search-box {{ flex: 1; display: flex; align-items: center; background: rgba(0, 0, 0, 0.35); border: 1px solid var(--border); border-radius: 8px; padding: 2px 10px; }}
  .search-box input {{ width: 100%; background: transparent; border: none; outline: none; color: #FFF; font-size: 12px; padding: 5px 0; }}
  .counter-chip {{ font-size: 11px; font-weight: 600; color: var(--text-muted); background: rgba(255, 255, 255, 0.04); padding: 5px 10px; border-radius: 6px; border: 1px solid var(--border); }}

  .tracks-scroll {{ flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; padding-right: 4px; }}
  .track-row {{ display: flex; align-items: center; gap: 12px; padding: 5px 12px; border-radius: 8px; cursor: pointer; flex-shrink: 0; }}
  .track-row:hover {{ background: var(--card-hover); }}
  .track-num {{ font-size: 11px; font-family: 'JetBrains Mono', monospace; color: var(--text-dim); width: 24px; }}
  .track-checkbox {{ width: 16px; height: 16px; border-radius: 4px; border: 1.5px solid var(--border-hover); display: grid; place-items: center; }}
  .track-row.selected .track-checkbox {{ background: var(--accent); border-color: var(--accent); }}
  .track-row.selected .track-checkbox::after {{ content: "✓"; font-size: 10px; font-weight: 900; color: #000; }}
  .track-info {{ flex: 1; display: flex; align-items: baseline; gap: 8px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
  .track-title {{ font-size: 13px; font-weight: 600; color: var(--text-main); }}
  .track-artist {{ font-size: 12px; color: var(--text-muted); }}

  .progress-card {{ display: none; flex-direction: column; gap: 6px; padding: 10px 14px; background: rgba(0, 0, 0, 0.45); border: 1px solid var(--border); border-radius: 12px; flex-shrink: 0; }}
  .progress-header {{ display: flex; align-items: center; justify-content: space-between; font-size: 11px; font-weight: 600; }}
  .progress-track {{ height: 5px; background: rgba(255, 255, 255, 0.08); border-radius: 10px; overflow: hidden; }}
  .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent), #10B981); transition: width 0.2s ease; border-radius: 10px; box-shadow: 0 0 10px var(--accent-glow); }}

  .tools-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-shrink: 0; }}
  .tools-group {{ display: flex; align-items: center; gap: 8px; }}

  .console-card {{ padding: 9px 13px; background: #08090C; border: 1px solid var(--border); border-radius: 12px; flex-shrink: 0; }}
  .console-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 3px; }}
  .console-title {{ font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 1px; color: var(--text-dim); font-weight: 700; }}
  .console-logs {{ height: 80px; overflow-y: auto; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #9499AD; display: flex; flex-direction: column; gap: 2px; user-select: text; }}
  .log-line {{ line-height: 1.35; }}
  .log-success {{ color: var(--accent); }}
  .log-warn {{ color: #F59E0B; }}
  .log-error {{ color: var(--danger); }}
  .log-info {{ color: #A5B4FC; }}

  .modal-overlay {{ position: fixed; inset: 0; background: rgba(0, 0, 0, 0.78); backdrop-filter: blur(8px); display: grid; place-items: center; z-index: 100; opacity: 0; pointer-events: none; transition: all 0.2s ease; }}
  .modal-overlay.active {{ opacity: 1; pointer-events: auto; }}
  .modal {{ background: var(--card); border: 1px solid var(--border-hover); border-radius: 16px; padding: 20px; width: 92%; max-width: 580px; display: flex; flex-direction: column; gap: 13px; }}
  .modal textarea {{ width: 100%; height: 140px; background: #090A0D; border: 1px solid var(--border); border-radius: 10px; padding: 10px; color: #FFF; font-family: 'JetBrains Mono', monospace; font-size: 11px; outline: none; resize: none; }}

  /* Вкладки в настройках */
  .settings-tabs {{ display: flex; gap: 6px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
  .tab-btn {{ font-size: 12px; font-weight: 600; color: var(--text-muted); background: transparent; padding: 6px 12px; border-radius: 6px; }}
  .tab-btn.active {{ color: #FFF; background: rgba(255, 255, 255, 0.08); }}

  .tab-pane {{ display: none; flex-direction: column; gap: 9px; max-height: 380px; overflow-y: auto; padding-right: 4px; }}
  .tab-pane.active {{ display: flex; }}

  .setting-row {{ display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: rgba(0, 0, 0, 0.3); border: 1px solid var(--border); border-radius: 10px; }}
  .setting-info {{ display: flex; flex-direction: column; gap: 2px; }}
  .setting-title {{ font-size: 13px; font-weight: 600; color: #FFF; }}
  .setting-desc {{ font-size: 11px; color: var(--text-muted); }}

  .select-custom {{ background: #090A0D; border: 1px solid var(--border); border-radius: 6px; color: #FFF; font-family: inherit; font-size: 12px; padding: 4px 8px; outline: none; }}

  .theme-picker {{ display: flex; gap: 6px; }}
  .theme-btn {{ width: 22px; height: 22px; border-radius: 50%; border: 2px solid transparent; cursor: pointer; }}
  .theme-btn.active {{ border-color: #FFF; transform: scale(1.15); }}
  .theme-spotify {{ background: #1ED760; }}
  .theme-linear {{ background: #6366F1; }}
  .theme-cyberpunk {{ background: #F59E0B; }}
  .theme-cyan {{ background: #06B6D4; }}

  .switch {{ position: relative; display: inline-block; width: 38px; height: 22px; flex-shrink: 0; }}
  .switch input {{ opacity: 0; width: 0; height: 0; }}
  .slider {{ position: absolute; cursor: pointer; inset: 0; background-color: rgba(255, 255, 255, 0.15); transition: .25s; border-radius: 20px; }}
  .slider:before {{ position: absolute; content: ""; height: 16px; width: 16px; left: 3px; bottom: 3px; background-color: white; transition: .25s; border-radius: 50%; }}
  input:checked + .slider {{ background-color: var(--accent); }}
  input:checked + .slider:before {{ transform: translateX(16px); background-color: #000; }}
</style>
</head>
<body>

<div class="app-layout">
  
  <div class="header">
    <div class="brand">
      <div class="brand-icon">✦</div>
      <div class="brand-title">Syncify Studio <span class="brand-badge">v{CURRENT_VERSION}</span></div>
    </div>
    <div class="header-actions">
      <div id="updateChip" class="update-chip" onclick="openUpdateModal()">✨ Обновить</div>
      <div id="authStatusPill" class="status-pill">
        <div class="status-dot"></div>
        <span id="authStatusText">YouTube: Проверка...</span>
      </div>
      <button class="btn-ghost" style="padding: 6px 11px;" onclick="openSettingsModal()" title="Настройки">⚙️ Настройки</button>
    </div>
  </div>

  <div class="card">
    <div class="input-row">
      <span class="input-tag">SPOTIFY</span>
      <input type="text" id="spUrl" class="input-field" placeholder="Вставьте ссылку на плейлист Spotify..." onchange="saveSettings()">
      <button class="btn-open-link" onclick="openLink('spUrl')" title="Открыть в браузере">↗</button>
    </div>
    <div class="input-row">
      <span class="input-tag">YT MUSIC</span>
      <input type="text" id="ytmUrl" class="input-field" placeholder="Вставьте ссылку на плейлист YouTube Music..." onchange="saveSettings()">
      <button class="btn-open-link" onclick="openLink('ytmUrl')" title="Открыть в браузере">↗</button>
    </div>
  </div>

  <div class="card" style="display: flex; justify-content: space-between; align-items: center;">
    <button class="btn-ghost" onclick="openAuthModal()">🔑 Авторизация YouTube</button>
    <div style="display: flex; gap: 8px;">
      <button id="btnSnapshot" class="btn-ghost" onclick="saveSnapshotManual()">📸 База: 0 треков</button>
      <button class="btn-primary" onclick="loadSpotifyTracks()">📥 Загрузить треки</button>
    </div>
  </div>

  <!-- ТРЕКЛИСТ И АНАЛИТИКА -->
  <div class="tracklist-card">
    <div id="insightsBanner" class="insights-banner">
      <span>📊 Аналитика:</span>
      <span id="insightsContent"></span>
    </div>
    <div class="tracklist-toolbar">
      <div class="search-box">
        <input type="text" id="searchInput" placeholder="🔍 Поиск по песням (Shift + клик для диапазона)..." oninput="filterTracks()">
      </div>
      <button class="btn-ghost" onclick="selectAll(true)">Все</button>
      <button class="btn-ghost" onclick="selectAll(false)">Снять</button>
      <div id="counterChip" class="counter-chip">0 из 0</div>
    </div>
    <div id="tracksContainer" class="tracks-scroll">
      <div style="text-align: center; padding: 40px 0; color: var(--text-dim); font-size: 13px;">
        Плейлист пуст. Нажмите «Загрузить треки», чтобы увидеть песни.
      </div>
    </div>
  </div>

  <!-- ЖИВОЙ ПРОГРЕСС-БАР -->
  <div id="progressCard" class="progress-card">
    <div class="progress-header">
      <span id="progressLabel" style="color: var(--text-main);">Синхронизация...</span>
      <div style="display: flex; align-items: center; gap: 10px;">
        <span id="progressPercent" style="color: var(--accent);">0%</span>
        <button class="btn-ghost" style="padding: 2px 7px; color: var(--danger); font-size: 10px;" onclick="cancelProcess()">✕ Отмена</button>
      </div>
    </div>
    <div class="progress-track">
      <div id="progressBarFill" class="progress-fill"></div>
    </div>
  </div>

  <div class="card" style="display: flex; flex-direction: column; gap: 10px;">
    <div style="display: flex; gap: 10px;">
      <button class="btn-quick" onclick="quickSync()">⚡ Быстрый синхрон новинок</button>
      <button class="btn-sync" onclick="syncSelected()">✓ Синхронизировать выбранные</button>
    </div>
    <div class="tools-bar">
      <div class="tools-group">
        <button class="btn-ghost" onclick="runDedup()">🧹 Дубликаты</button>
        <button id="btnLost" class="btn-ghost" onclick="openLostModal()">📋 Потеряшки (0)</button>
        <button class="btn-ghost" onclick="downloadMp3()">📥 Скачать MP3</button>
      </div>
      <div class="tools-group" style="font-size: 11px; color: var(--text-muted);">
        <span id="autoSyncLabel">⏰ Авто: Выкл</span>
      </div>
    </div>
  </div>

  <div class="console-card">
    <div class="console-header">
      <span class="console-title">ACTIVITY LOG</span>
      <button class="btn-ghost" style="padding: 2px 7px; font-size: 10px;" onclick="clearLogs()">Очистить</button>
    </div>
    <div id="logsBox" class="console-logs">
      <div class="log-line log-info">[✦] Syncify Studio v{CURRENT_VERSION}. Движок готов.</div>
    </div>
  </div>

</div>

<!-- МОДАЛКА: ПРОФЕССИОНАЛЬНЫЕ НАСТРОЙКИ С ВКЛАДКАМИ -->
<div id="settingsModal" class="modal-overlay">
  <div class="modal">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="font-size: 16px;">⚙️ Панель управления Syncify</h3>
      <button class="btn-ghost" style="padding: 4px 8px;" onclick="closeModal('settingsModal')">✕</button>
    </div>
    
    <!-- Переключатель вкладок -->
    <div class="settings-tabs">
      <button class="tab-btn active" onclick="switchTab('tabSystem')">🎯 Система</button>
      <button class="tab-btn" onclick="switchTab('tabSync')">🔄 Синхронизация</button>
      <button class="tab-btn" onclick="switchTab('tabStorage')">💾 Хранилище</button>
      <button class="tab-btn" onclick="switchTab('tabDev')">🛠️ Разработчик</button>
    </div>

    <!-- Вкладка 1: Система -->
    <div id="tabSystem" class="tab-pane active">
      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Цветовая палитра</span>
          <span class="setting-desc">Тема оформления и акцентный свет кнопок</span>
        </div>
        <div class="theme-picker">
          <div class="theme-btn theme-spotify" title="Spotify Green" onclick="setTheme('spotify')"></div>
          <div class="theme-btn theme-linear" title="Linear Indigo" onclick="setTheme('linear')"></div>
          <div class="theme-btn theme-cyberpunk" title="Cyberpunk Amber" onclick="setTheme('cyberpunk')"></div>
          <div class="theme-btn theme-cyan" title="Electric Cyan" onclick="setTheme('cyan')"></div>
        </div>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Всплывающие уведомления Windows</span>
          <span class="setting-desc">Показывать системные уведомления по завершении</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="notificationsToggle" onchange="saveSettings()">
          <span class="slider"></span>
        </label>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Автозапуск вместе с Windows</span>
          <span class="setting-desc">Запускать при входе в систему</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="autostartToggle" onchange="toggleAutostart()">
          <span class="slider"></span>
        </label>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Сворачивать в трей при закрытии</span>
          <span class="setting-desc">Прятать к часам при нажатии на крестик</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="closeToTrayToggle" onchange="saveSettings()">
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <!-- Вкладка 2: Синхронизация -->
    <div id="tabSync" class="tab-pane">
      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Фоновый авто-мониторинг</span>
          <span class="setting-desc">Проверять новинки по расписанию</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="autoSyncToggle" onchange="toggleAutoSync()">
          <span class="slider"></span>
        </label>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Интервал авто-синхронизации</span>
          <span class="setting-desc">Как часто сканировать плейлист</span>
        </div>
        <select id="autoSyncInterval" class="select-custom" onchange="saveSettings()">
          <option value="6">Каждые 6 часов</option>
          <option value="12">Каждые 12 часов</option>
          <option value="24" selected>Каждые 24 часа</option>
          <option value="48">Каждые 48 часов</option>
        </select>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Зеркалировать удаления</span>
          <span class="setting-desc">Удалять из YouTube, если трек стерт в Spotify</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="syncDeleteToggle" onchange="saveSettings()">
          <span class="slider"></span>
        </label>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Безопасный режим (Safe Mode)</span>
          <span class="setting-desc">Блокировать массовые удаления при ручном переносе</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="safeModeToggle" onchange="saveSettings()">
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <!-- Вкладка 3: Хранилище -->
    <div id="tabStorage" class="tab-pane">
      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Системная директория</span>
          <span class="setting-desc">Открыть рабочую папку в Проводнике</span>
        </div>
        <button class="btn-ghost" onclick="openAppdataDir()">📂 Открыть %APPDATA%</button>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Кэш быстрого поиска</span>
          <span id="cacheCountLabel" class="setting-desc">Сохранено: 0 треков</span>
        </div>
        <button class="btn-ghost" style="color: var(--danger);" onclick="clearSearchCache()">Очистить кэш</button>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Сброс базы Spotify</span>
          <span class="setting-desc">Удалить снимок запомненных треков</span>
        </div>
        <button class="btn-ghost" style="color: var(--danger);" onclick="resetSnapshot()">Сбросить базу</button>
      </div>
    </div>

    <!-- Вкладка 4: Для разработчиков -->
    <div id="tabDev" class="tab-pane">
      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Потоки турбо-поиска</span>
          <span class="setting-desc">Число параллельных воркеров (ThreadPool)</span>
        </div>
        <select id="searchWorkers" class="select-custom" onchange="saveSettings()">
          <option value="2">2 потока (тихий)</option>
          <option value="4" selected>4 потока (баланс)</option>
          <option value="8">8 потоков (турбо)</option>
        </select>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Размер пакета заливки</span>
          <span class="setting-desc">Сколько треков слать за 1 запрос к API</span>
        </div>
        <select id="batchSize" class="select-custom" onchange="saveSettings()">
          <option value="10">10 треков</option>
          <option value="25" selected>25 треков</option>
          <option value="50">50 треков</option>
        </select>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Подробный Debug-лог</span>
          <span class="setting-desc">Выводить детальные сообщения отладки</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="verboseLogToggle" onchange="saveSettings()">
          <span class="slider"></span>
        </label>
      </div>

      <div class="setting-row">
        <div class="setting-info">
          <span class="setting-title">Диагностика системы</span>
          <span class="setting-desc">Скопировать технический отчет в буфер</span>
        </div>
        <button class="btn-ghost" onclick="copyDiagnostics()">📋 Отчет для баг-репорта</button>
      </div>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 4px;">
      <span style="font-size: 10px; color: var(--text-dim); font-family: monospace;">Chuvak12/SyncifyStudio</span>
      <button class="btn-primary" onclick="closeModal('settingsModal')">Готово</button>
    </div>
  </div>
</div>

<!-- МОДАЛКА: ОБНОВЛЕНИЕ -->
<div id="updateModal" class="modal-overlay">
  <div class="modal">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="font-size: 16px; color: #10B981;">✨ Доступно обновление!</h3>
      <button class="btn-ghost" style="padding: 4px 8px;" onclick="closeModal('updateModal')">✕</button>
    </div>
    <div id="updateNotes" style="font-size: 12px; color: var(--text-muted); line-height: 1.5; white-space: pre-wrap; max-height: 140px; overflow-y: auto;"></div>
    <div style="display: flex; justify-content: flex-end; gap: 8px;">
      <button class="btn-ghost" onclick="closeModal('updateModal')">Позже</button>
      <button id="btnDoUpdate" class="btn-primary" style="background: #10B981;" onclick="applyUpdate()">🚀 Обновить и перезапустить</button>
    </div>
  </div>
</div>

<!-- МОДАЛКА: АВТОРИЗАЦИЯ -->
<div id="authModal" class="modal-overlay">
  <div class="modal">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="font-size: 15px;">Авторизация в YouTube Music</h3>
      <button class="btn-ghost" style="padding: 4px 8px;" onclick="closeModal('authModal')">✕</button>
    </div>
    <div style="font-size: 12px; color: var(--text-muted); line-height: 1.5;">
      1. Откройте <a href="https://music.youtube.com" target="_blank" style="color: var(--accent);">music.youtube.com</a> в браузере.<br>
      2. Нажмите <b>F12</b> ➔ вкладка <b>Network (Сеть)</b> ➔ обновите страницу (F5).<br>
      3. Кликните любой запрос (browse), скопируйте всю строку <b>Cookie</b> и вставьте сюда:
    </div>
    <textarea id="authInput" placeholder="Вставьте строку Cookie..."></textarea>
    <div style="display: flex; justify-content: flex-end; gap: 8px;">
      <button class="btn-ghost" onclick="closeModal('authModal')">Отмена</button>
      <button class="btn-primary" onclick="submitAuth()">💾 Сохранить</button>
    </div>
  </div>
</div>

<!-- МОДАЛКА: ПОТЕРЯШКИ -->
<div id="lostModal" class="modal-overlay">
  <div class="modal">
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h3 style="font-size: 15px;">Потеряшки</h3>
      <button class="btn-ghost" style="padding: 4px 8px;" onclick="closeModal('lostModal')">✕</button>
    </div>
    <textarea id="lostInput" readonly></textarea>
    <div style="display: flex; justify-content: space-between;">
      <button class="btn-ghost" style="color: var(--danger);" onclick="clearLost()">🗑️ Очистить</button>
      <button class="btn-ghost" onclick="copyLost()">📋 Скопировать</button>
    </div>
  </div>
</div>

<script>
  let tracks = [];
  let lastClickedIndex = null;
  let isMouseDown = false;
  let dragValue = true;
  let updateData = null;
  let currentTheme = 'spotify';

  window.addEventListener('pywebviewready', async () => {{
    const config = await window.pywebview.api.get_config();
    if (config) {{
      document.getElementById('spUrl').value = config.sp_url || '';
      document.getElementById('ytmUrl').value = config.ytm_url || '';
      document.getElementById('syncDeleteToggle').checked = config.sync_delete !== 0;
      document.getElementById('safeModeToggle').checked = config.safe_mode !== 0;
      document.getElementById('autoSyncToggle').checked = config.auto_sync === 1;
      document.getElementById('closeToTrayToggle').checked = config.close_to_tray === 1;
      document.getElementById('autostartToggle').checked = config.autostart === 1;
      document.getElementById('notificationsToggle').checked = config.notifications !== 0;
      document.getElementById('verboseLogToggle').checked = config.verbose_logging === 1;
      
      if (config.auto_sync_interval) document.getElementById('autoSyncInterval').value = config.auto_sync_interval;
      if (config.search_workers) document.getElementById('searchWorkers').value = config.search_workers;
      if (config.batch_size) document.getElementById('batchSize').value = config.batch_size;

      setTheme(config.theme || 'spotify', false);
      updateAutoSyncLabel(config.auto_sync === 1, config.auto_sync_interval || 24);
    }}
    updateStatus();
    checkUpdate();
    checkClipboardLink();
  }});

  function switchTab(tabId) {{
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }}

  function setTheme(theme, save = true) {{
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    document.querySelectorAll('.theme-btn').forEach(btn => {{
      btn.classList.toggle('active', btn.classList.contains('theme-' + theme));
    }});
    if (save) saveSettings();
  }}

  async function checkClipboardLink() {{
    try {{
      const text = await navigator.clipboard.readText();
      const spInput = document.getElementById('spUrl');
      if (text && text.includes('open.spotify.com/playlist/') && !spInput.value.trim()) {{
        spInput.value = text.trim();
        saveSettings();
        appendLog('[📋] Ссылка на плейлист автоматически подставлена из буфера!', 'info');
      }}
    }} catch (e) {{}}
  }}

  function openLink(inputId) {{
    const val = document.getElementById(inputId).value.trim();
    if (val) window.pywebview.api.open_browser(val);
  }}

  function updateAutoSyncLabel(active, interval) {{
    const el = document.getElementById('autoSyncLabel');
    el.innerText = active ? `⏰ Авто: каждые ${{interval}}ч` : '⏰ Авто: Выкл';
    el.style.color = active ? 'var(--accent)' : 'var(--text-muted)';
  }}

  function updateProgress(percent, label = '') {{
    const card = document.getElementById('progressCard');
    if (percent < 0 || percent >= 100) {{
      card.style.display = 'none';
      return;
    }}
    card.style.display = 'flex';
    document.getElementById('progressBarFill').style.width = percent + '%';
    document.getElementById('progressPercent').innerText = percent + '%';
    if (label) document.getElementById('progressLabel').innerText = label;
  }}

  async function cancelProcess() {{
    await window.pywebview.api.cancel_process();
    updateProgress(-1);
  }}

  async function checkUpdate() {{
    const info = await window.pywebview.api.check_update();
    if (info && info.has_update) {{
      updateData = info;
      const chip = document.getElementById('updateChip');
      chip.style.display = 'inline-flex';
      chip.innerText = `✨ Обновить до v${{info.version}}`;
    }}
  }}

  function openUpdateModal() {{
    if (!updateData) return;
    document.getElementById('updateNotes').innerText = `Версия: v${{updateData.version}}\\n\\n${{updateData.notes}}`;
    document.getElementById('updateModal').classList.add('active');
  }}

  async function applyUpdate() {{
    if (!updateData) return;
    const btn = document.getElementById('btnDoUpdate');
    btn.innerText = '⏳ Скачивание...';
    btn.disabled = true;
    appendLog('[~] Загрузка новой версии...', 'info');
    await window.pywebview.api.apply_update(updateData.download_url);
  }}

  async function updateStatus() {{
    const status = await window.pywebview.api.get_status();
    const pill = document.getElementById('authStatusPill');
    const text = document.getElementById('authStatusText');
    const snapBtn = document.getElementById('btnSnapshot');
    const lostBtn = document.getElementById('btnLost');

    if (status.is_auth) {{
      pill.classList.add('online');
      text.innerText = 'YouTube: Подключен';
    }} else {{
      pill.classList.remove('online');
      text.innerText = 'YouTube: Не авторизован';
    }}

    snapBtn.innerText = `📸 База: ${{status.snapshot_count}} треков`;
    lostBtn.innerText = `📋 Потеряшки (${{status.lost_count}})`;
    document.getElementById('cacheCountLabel').innerText = `Сохранено: ${{status.cache_count}} соответствий`;
  }}

  function appendLog(text, type = 'normal') {{
    const box = document.getElementById('logsBox');
    const div = document.createElement('div');
    div.className = `log-line log-${{type}}`;
    div.innerText = text;
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
  }}

  function clearLogs() {{ document.getElementById('logsBox').innerHTML = ''; }}

  async function saveSettings() {{
    const sp_url = document.getElementById('spUrl').value.trim();
    const ytm_url = document.getElementById('ytmUrl').value.trim();
    const sync_delete = document.getElementById('syncDeleteToggle').checked ? 1 : 0;
    const safe_mode = document.getElementById('safeModeToggle').checked ? 1 : 0;
    const auto_sync = document.getElementById('autoSyncToggle').checked ? 1 : 0;
    const auto_sync_interval = parseInt(document.getElementById('autoSyncInterval').value);
    const close_to_tray = document.getElementById('closeToTrayToggle').checked ? 1 : 0;
    const autostart = document.getElementById('autostartToggle').checked ? 1 : 0;
    const notifications = document.getElementById('notificationsToggle').checked ? 1 : 0;
    const verbose_logging = document.getElementById('verboseLogToggle').checked ? 1 : 0;
    const search_workers = parseInt(document.getElementById('searchWorkers').value);
    const batch_size = parseInt(document.getElementById('batchSize').value);

    await window.pywebview.api.save_config({{
      sp_url, ytm_url, sync_delete, safe_mode, auto_sync, auto_sync_interval,
      close_to_tray, autostart, notifications, verbose_logging, search_workers,
      batch_size, theme: currentTheme
    }});
    updateAutoSyncLabel(auto_sync === 1, auto_sync_interval);
  }}

  async function toggleAutoSync() {{
    await saveSettings();
    const active = document.getElementById('autoSyncToggle').checked;
    await window.pywebview.api.toggle_auto_sync(active);
  }}

  async function toggleAutostart() {{
    const active = document.getElementById('autostartToggle').checked;
    await window.pywebview.api.set_autostart(active);
    await saveSettings();
  }}

  async function loadSpotifyTracks() {{
    await saveSettings();
    appendLog('[~] Загрузка плейлиста Spotify...', 'info');
    const res = await window.pywebview.api.fetch_tracks();
    if (res.success) {{
      tracks = res.tracks.map(t => ({{ ...t, selected: true }}));
      renderTracksFast();
      appendLog(`[✓] Загружено ${{tracks.length}} треков!`, 'success');
      updateStatus();

      if (res.insights) {{
        const b = document.getElementById('insightsBanner');
        b.style.display = 'flex';
        document.getElementById('insightsContent').innerHTML = `
          <span class="insights-accent">${{res.insights.total_tracks}}</span> треков • 
          <span class="insights-accent">${{res.insights.unique_artists}}</span> артистов • 
          Топ: <span class="insights-accent">${{res.insights.top_artists}}</span>
        `;
      }}
    }} else {{
      appendLog(`[-] Ошибка: ${{res.error}}`, 'error');
    }}
  }}

  function renderTracksFast() {{
    const container = document.getElementById('tracksContainer');
    container.innerHTML = '';
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    const fragment = document.createDocumentFragment();

    tracks.forEach((t, idx) => {{
      const match = !query || t.display.toLowerCase().includes(query);
      if (!match) return;

      const row = document.createElement('div');
      row.className = `track-row ${{t.selected ? 'selected' : ''}}`;
      row.innerHTML = `
        <span class="track-num">${{String(idx + 1).padStart(2, '0')}}</span>
        <div class="track-checkbox"></div>
        <div class="track-info">
          <span class="track-title">${{t.title}}</span>
          <span class="track-artist">— ${{t.artist}}</span>
        </div>
      `;

      row.addEventListener('mousedown', (e) => {{
        isMouseDown = true;
        if (e.shiftKey && lastClickedIndex !== null) {{
          const start = Math.min(lastClickedIndex, idx);
          const end = Math.max(lastClickedIndex, idx);
          const targetVal = tracks[lastClickedIndex].selected;
          for (let i = start; i <= end; i++) {{
            tracks[i].selected = targetVal;
          }}
          renderTracksFast();
          return;
        }}
        t.selected = !t.selected;
        dragValue = t.selected;
        lastClickedIndex = idx;
        renderTracksFast();
      }});

      row.addEventListener('mouseenter', () => {{
        if (isMouseDown) {{
          t.selected = dragValue;
          renderTracksFast();
        }}
      }});

      fragment.appendChild(row);
    }});

    container.appendChild(fragment);
    updateCounter();
  }}

  window.addEventListener('mouseup', () => {{ isMouseDown = false; }});

  function updateCounter() {{
    const selectedCount = tracks.filter(t => t.selected).length;
    document.getElementById('counterChip').innerText = `${{selectedCount}} из ${{tracks.length}}`;
  }}

  function selectAll(val) {{
    const query = document.getElementById('searchInput').value.toLowerCase().trim();
    tracks.forEach(t => {{
      if (!query || t.display.toLowerCase().includes(query)) {{
        t.selected = val;
      }}
    }});
    renderTracksFast();
  }}

  function filterTracks() {{ renderTracksFast(); }}

  async function quickSync() {{
    await saveSettings();
    appendLog('[~] Сверка новинок и удалений...', 'info');
    await window.pywebview.api.quick_sync();
    updateStatus();
  }}

  async function syncSelected() {{
    await saveSettings();
    const selected = tracks.filter(t => t.selected);
    if (!selected.length) {{
      appendLog('[-] Отметьте треки галочками!', 'warn');
      return;
    }}
    appendLog(`[~] Перенос ${{selected.length}} выбранных треков...`, 'info');
    await window.pywebview.api.sync_selected(selected);
    updateStatus();
  }}

  async function runDedup() {{
    await saveSettings();
    appendLog('[~] Очистка дубликатов в YouTube Music...', 'info');
    await window.pywebview.api.dedup();
  }}

  async function downloadMp3() {{
    const selected = tracks.filter(t => t.selected);
    if (!selected.length) {{
      appendLog('[-] Отметьте треки для скачивания!', 'warn');
      return;
    }}
    appendLog(`[↓] Выберите папку для сохранения...`, 'info');
    await window.pywebview.api.download_mp3(selected);
  }}

  async function saveSnapshotManual() {{
    await saveSettings();
    appendLog('[~] Фиксация базы плейлиста...', 'info');
    await window.pywebview.api.force_snapshot();
    updateStatus();
  }}

  async function openAppdataDir() {{
    await window.pywebview.api.open_appdata();
  }}

  async function clearSearchCache() {{
    await window.pywebview.api.clear_cache();
    updateStatus();
  }}

  async function resetSnapshot() {{
    await window.pywebview.api.reset_snapshot();
    updateStatus();
  }}

  async function copyDiagnostics() {{
    const text = await window.pywebview.api.get_diagnostics();
    navigator.clipboard.writeText(text);
    appendLog('[📋] Технический отчет скопирован в буфер!', 'success');
  }}

  function openAuthModal() {{ document.getElementById('authModal').classList.add('active'); }}
  function openSettingsModal() {{ document.getElementById('settingsModal').classList.add('active'); }}
  async function openLostModal() {{ 
    const list = await window.pywebview.api.get_lost();
    document.getElementById('lostInput').value = list.map(t => `• ${{t.display || t.query}}`).join('\\n');
    document.getElementById('lostModal').classList.add('active'); 
  }}
  function closeModal(id) {{ document.getElementById(id).classList.remove('active'); }}

  async function submitAuth() {{
    const raw = document.getElementById('authInput').value.trim();
    if (!raw) return;
    const ok = await window.pywebview.api.save_auth(raw);
    if (ok) {{
      closeModal('authModal');
      document.getElementById('authInput').value = '';
      updateStatus();
    }}
  }}

  function copyLost() {{
    const txt = document.getElementById('lostInput').value;
    navigator.clipboard.writeText(txt);
    appendLog('[+] Список потеряшек скопирован!', 'success');
  }}

  async function clearLost() {{
    await window.pywebview.api.clear_lost();
    document.getElementById('lostInput').value = '';
    updateStatus();
  }}
</script>

</body>
</html>
"""