function normalizeBasePath(pathname) {
  const raw = String(pathname || "")
    .split(/[?#]/, 1)[0]
    .trim();
  if (!raw || raw === "/") return "";
  const parts = raw.split("/").filter(Boolean);
  if (!parts.length) return "";
  const last = parts[parts.length - 1] || "";
  if (last.includes(".")) parts.pop();
  if (!parts.length) return "";
  return `/${parts.join("/")}`;
}

function getBasePath() {
  const currentSrc =
    document.currentScript && document.currentScript.src
      ? document.currentScript.src
      : "";
  if (currentSrc) {
    try {
      const url = new URL(currentSrc, window.location.href);
      return normalizeBasePath(url.pathname);
    } catch (e) {}
  }

  const script = document.querySelector(
    'script[src*="movies.min.js"], script[src*="movies.js"]',
  );
  const scriptSrc = script && script.src ? script.src : "";
  if (scriptSrc) {
    try {
      const url = new URL(scriptSrc, window.location.href);
      return normalizeBasePath(url.pathname);
    } catch (e) {}
  }

  return normalizeBasePath(window.location.pathname || "/");
}
const BASE_PATH = getBasePath();
let manualPlaybackMode = null;
let currentPlaybackMode = null;
let plexButton = null;
const PLAYBACK_OVERRIDE_PREFIX = "playback-override:";
let skipManualOverrideLoad = false;

function isPlexStreamUrl(url) {
  const raw = String(url || "").trim();
  if (!raw) return false;
  try {
    const parsed = new URL(raw, window.location.href);
    return /\/plex\//.test(parsed.pathname);
  } catch (e) {
    return /\/plex\//.test(raw) || raw.includes("plex_stream");
  }
}

function getKnownPlexStreamUrl(video) {
  const explicit = String(video?.plex_stream_url || "").trim();
  if (explicit) return explicit;
  const id = String(video?.id || "").trim();
  if (!id) return "";
  const thumb = String(video?.thumb_url || "").trim();
  const subtitle = String(video?.subtitle_url || "").trim();
  if (thumb.includes("/plex/") || subtitle.includes("/plex/")) {
    return `/plex/video/${id}.m3u8`;
  }
  return "";
}

function updatePlexIndicator(mode) {
  const resolvedMode = mode || currentPlaybackMode || "direct";
  currentPlaybackMode = resolvedMode;
  if (!plexButton) return;
  const forcedPlex = manualPlaybackMode === "plex";
  const forcedDirect = manualPlaybackMode === "direct";
  const isActive = resolvedMode === "plex";
  plexButton.classList.toggle("active", isActive);
  plexButton.dataset.mode = manualPlaybackMode || "auto";
  plexButton.setAttribute("aria-pressed", String(forcedPlex));
  if (forcedPlex) {
    plexButton.title = "Plex playback (forced)";
  } else if (forcedDirect) {
    plexButton.title = "Direct playback (forced)";
  } else {
    plexButton.title = mode === "plex"
      ? "Plex playback (auto)"
      : "Direct playback (auto)";
  }
}

function cycleManualPlaybackMode() {
  const video =
    currentVideoRecord ||
    (currentVideoId ? videos.find((v) => v.id === currentVideoId) : null);
  const hasPlex = Boolean(video && getKnownPlexStreamUrl(video));
  let nextMode;
  if (!manualPlaybackMode) {
    nextMode = currentPlaybackMode === "plex" ? "direct" : "plex";
  } else {
    nextMode = manualPlaybackMode === "plex" ? "direct" : "plex";
  }
  if (nextMode === "plex" && !hasPlex) {
    nextMode = "direct";
  }
  manualPlaybackMode = nextMode;
  skipManualOverrideLoad = true;
  persistManualPlaybackOverride(currentVideoId, manualPlaybackMode).catch(() => {});
  updateDebugPanel();
  if (video) {
    currentVideoRecord = video;
    const subtitle = video.subtitle_url ? withBase(video.subtitle_url) : null;
    openPlayer(pickStreamCandidates(video), video.name, subtitle);
    return;
  }
  updatePlexIndicator(currentPlaybackMode);
}
function withBase(path) {
  const raw = String(path || "").trim();
  if (!raw) return BASE_PATH || "/";
  if (
    /^[a-z][a-z0-9+.-]*:\/\//i.test(raw) ||
    raw.startsWith("blob:") ||
    raw.startsWith("data:")
  )
    return raw;
  const clean = raw.replace(/^\/+/, "");
  return BASE_PATH ? `${BASE_PATH}/${clean}` : `/${clean}`;
}
function apiUrl(path) {
  const clean = String(path || "").replace(/^\/+/, "");
  return BASE_PATH ? `${BASE_PATH}/api/${clean}` : `/api/${clean}`;
}
function isDesktopClient() {
  const ua = (navigator.userAgent || "").toLowerCase();
  const isiOS = /iphone|ipad|ipod/.test(ua);
  const isAndroid = /android/.test(ua);
  return !(isiOS || isAndroid);
}
function isIOSLike() {
  const ua = (navigator.userAgent || "").toLowerCase();
  return (
    /iphone|ipad|ipod/.test(ua) ||
    (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1)
  );
}
function isIPadClient() {
  const ua = (navigator.userAgent || "").toLowerCase();
  if (/ipad/.test(ua)) return true;
  const ipadOS13Plus =
    navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1;
  if (!ipadOS13Plus) return false;
  const shortSide = Math.min(
    window.screen.width || 0,
    window.screen.height || 0,
  );
  return shortSide >= 768;
}

const MOBILE_ZOOM_STORAGE_KEY = "movies_mobile_zoom_level";
function readPersistedMobileZoomLevel() {
  try {
    const stored = Number(localStorage.getItem(MOBILE_ZOOM_STORAGE_KEY));
    return stored === 2 ? 2 : 1;
  } catch (err) {
    return 1;
  }
}

const PINCH_TRIGGER_DISTANCE = 24;
let pinchTracking = {
  active: false,
  baseDist: 0,
  lastDist: 0,
  lastTs: 0,
  startTs: 0,
  pendingLevel: null,
  triggered: false,
};

function getTouchDistance(touches) {
  if (!touches || touches.length < 2) return 0;
  const [a, b] = touches;
  const dx = a.clientX - b.clientX;
  const dy = a.clientY - b.clientY;
  return Math.hypot(dx, dy);
}

function resetPinchTracking() {
  pinchTracking.lastDist = 0;
  pinchTracking.lastTs = 0;
  pinchTracking.startTs = 0;
  pinchTracking.pendingLevel = null;
  pinchTracking.triggered = false;
}

function updatePinchTracking(distance, timestamp) {
  pinchTracking.lastDist = distance;
  pinchTracking.lastTs = timestamp;
}

function getPinchAnimationDuration(endTs) {
  const elapsed = Math.max(16, endTs - (pinchTracking.startTs || endTs));
  const traveled = Math.abs(
    (pinchTracking.lastDist || pinchTracking.baseDist) - pinchTracking.baseDist,
  );
  const speed = traveled / elapsed;
  return Math.max(150, Math.min(460, 360 - speed * 260));
}

function handlePinchStart(event) {
  if (!isMobileLayout() || event.touches.length !== 2) {
    pinchTracking.active = false;
    return;
  }
  resetPinchTracking();
  pinchTracking.active = true;
  const startDistance = getTouchDistance(event.touches);
  const startTs = performance.now();
  pinchTracking.baseDist = startDistance;
  updatePinchTracking(startDistance, startTs);
  pinchTracking.startTs = startTs;
  pinchTracking.pendingLevel = mobileZoomLevel;
}

function handlePinchMove(event) {
  if (!pinchTracking.active || event.touches.length !== 2) return;
  const dist = getTouchDistance(event.touches);
  const delta = dist - pinchTracking.baseDist;
  if (Math.abs(delta) >= PINCH_TRIGGER_DISTANCE) {
    pinchTracking.pendingLevel = delta > 0 ? 2 : 1;
    if (
      !pinchTracking.triggered &&
      !zoomTransitionActive &&
      pinchTracking.pendingLevel !== mobileZoomLevel
    ) {
      pinchTracking.triggered = true;
      pinchTracking.active = false;
      setMobileZoomLevel(pinchTracking.pendingLevel, {
        durationMs: getPinchAnimationDuration(performance.now()),
      });
    }
  }
  updatePinchTracking(dist, performance.now());
  event.preventDefault();
}

function handlePinchEnd(event) {
  if (event.touches.length < 2) {
    const targetLevel = pinchTracking.pendingLevel;
    const endTs = performance.now();
    pinchTracking.active = false;
    if (
      !pinchTracking.triggered &&
      targetLevel &&
      targetLevel !== mobileZoomLevel
    ) {
      setMobileZoomLevel(targetLevel, {
        durationMs: getPinchAnimationDuration(endTs),
      });
    }
    resetPinchTracking();
  }
}

function getMobileZoomRowLimit() {
  const landscape = window.matchMedia("(orientation: landscape)").matches;
  if (isIPadClient()) {
    return landscape ? 7 : 5;
  }
  return landscape ? 7 : 3;
}

function persistMobileZoomLevel(level) {
  try {
    localStorage.setItem(MOBILE_ZOOM_STORAGE_KEY, String(level));
  } catch (err) {
    /* ignore */
  }
}

function setMobileZoomLevel(level, { durationMs = null } = {}) {
  const mobile = isMobileLayout();
  if (!mobile) return;
  const next = level === 2 ? 2 : 1;
  if (mobileZoomLevel === next) return;
  const zoomingIn = next > mobileZoomLevel;
  const applyZoom = () => {
    if (relayoutTimer) {
      clearTimeout(relayoutTimer);
      relayoutTimer = null;
    }
    mobileZoomLevel = next;
    persistMobileZoomLevel(next);
    grid.classList.toggle("zoomed", mobileZoomLevel > 1);
    applyMobileColumnSetting();
    buildRows(filteredVideos.slice(0, renderCount), {
      append: false,
      isFinal: renderCount >= filteredVideos.length && serverExhausted,
    });
  };
  animateMobileZoomTransition(applyZoom, { durationMs, zoomingIn });
}

function getVisibleGridCardRects() {
  const rects = new Map();
  if (!grid) return rects;
  grid.querySelectorAll(".card[data-id]").forEach((card) => {
    const id = card.dataset.id;
    if (!id) return;
    rects.set(id, card.getBoundingClientRect());
  });
  return rects;
}

function getMobileZoomAnchor() {
  if (!grid) return null;
  const cards = Array.from(grid.querySelectorAll(".card[data-id]"));
  if (!cards.length) return null;
  const viewportCenterY = window.innerHeight * 0.5;
  let best = null;
  let bestScore = Infinity;
  cards.forEach((card) => {
    const rect = card.getBoundingClientRect();
    if (!rect.height) return;
    const centerY = rect.top + rect.height / 2;
    const score = Math.abs(centerY - viewportCenterY);
    if (score < bestScore) {
      bestScore = score;
      best = {
        id: card.dataset.id,
        offsetTop: rect.top,
      };
    }
  });
  return best;
}

function getMobileZoomTransitionDuration(zoomingIn, durationMs) {
  if (durationMs != null) return Math.max(120, Math.min(480, durationMs));
  return zoomingIn ? 280 : 220;
}

function restoreAnchorAfterZoom(anchor) {
  if (!anchor?.id) return;
  const nextAnchor = grid.querySelector(`.card[data-id="${anchor.id}"]`);
  if (!nextAnchor) return;
  const rect = nextAnchor.getBoundingClientRect();
  const anchorScrollDelta = rect.top - anchor.offsetTop;
  if (Math.abs(anchorScrollDelta) > 0.5) {
    window.scrollBy(0, anchorScrollDelta);
  }
}

function applyInitialZoomCardTransforms(cards, beforeRects, zoomingIn) {
  cards.forEach((card) => {
    const prev = beforeRects.get(card.dataset.id);
    if (!prev) return;
    const next = card.getBoundingClientRect();
    if (!next.width || !next.height) return;
    const dx = prev.left - next.left;
    const dy = prev.top - next.top;
    const sx = prev.width / next.width;
    const sy = prev.height / next.height;
    if (
      Math.abs(dx) < 0.5 &&
      Math.abs(dy) < 0.5 &&
      Math.abs(sx - 1) < 0.01 &&
      Math.abs(sy - 1) < 0.01
    ) {
      return;
    }
    card.style.transition = "none";
    card.style.transformOrigin = "top left";
    card.style.transform = zoomingIn
      ? `translate(${dx}px,${dy}px) scale(${sx},${sy})`
      : `translate(${dx}px,${dy}px)`;
  });
}

function getMobileZoomTransitionCss(zoomingIn, transitionMs) {
  const opacityMs = zoomingIn
    ? Math.max(160, transitionMs - 80)
    : Math.max(140, transitionMs - 80);
  const easing = zoomingIn
    ? "cubic-bezier(.22,.7,.2,1)"
    : "cubic-bezier(.2,.65,.2,1)";
  return `transform ${transitionMs}ms ${easing}, opacity ${opacityMs}ms ease`;
}

function cleanupZoomCardTransforms(cards) {
  cards.forEach((card) => {
    card.style.transition = "";
    card.style.transform = "";
    card.style.transformOrigin = "";
  });
}

function animateMobileZoomTransition(
  work,
  { zoomingIn = true, durationMs = null } = {},
) {
  if (!grid) {
    work();
    return;
  }
  if (zoomTransitionActive) {
    work();
    return;
  }
  if (zoomFadeOutTimer) {
    clearTimeout(zoomFadeOutTimer);
    zoomFadeOutTimer = null;
  }
  if (zoomFadeInTimer) {
    clearTimeout(zoomFadeInTimer);
    zoomFadeInTimer = null;
  }
  zoomTransitionActive = true;
  const transitionMs = getMobileZoomTransitionDuration(zoomingIn, durationMs);
  const before = getVisibleGridCardRects();
  const anchor = getMobileZoomAnchor();
  work();
  restoreAnchorAfterZoom(anchor);
  const cards = Array.from(grid.querySelectorAll(".card[data-id]"));
  applyInitialZoomCardTransforms(cards, before, zoomingIn);
  void grid.getBoundingClientRect();
  zoomFadeOutTimer = window.requestAnimationFrame(() => {
    zoomFadeOutTimer = null;
    cards.forEach((card) => {
      card.style.transition = getMobileZoomTransitionCss(
        zoomingIn,
        transitionMs,
      );
      card.style.transform = "";
    });
    zoomFadeInTimer = window.setTimeout(() => {
      zoomFadeInTimer = null;
      cleanupZoomCardTransforms(cards);
      zoomTransitionActive = false;
    }, transitionMs);
  });
}
function getPreferredPlaybackMode(v, override = null) {
  if (override === "plex" || override === "direct") return override;
  const name = String(v?.name || "").toLowerCase();
  const rel = String(v?.relative_path || "").toLowerCase();
  const path = rel || name;
  if (path.endsWith(".mkv") || path.endsWith(".ts")) return "plex";
  const directUrl = String(
    v?.desktop_stream_url || v?.stream_url || v?.video_url || "",
  );
  const hasPlex = Boolean(getKnownPlexStreamUrl(v));
  if (!hasPlex) return "direct";
  if (directUrl.includes("?fmp4=1") || directUrl.includes("/hls/")) return "plex";
  const safeExt =
    path.endsWith(".mp4") || path.endsWith(".m4v") || path.endsWith(".webm");
  const directSafe = Boolean(v?.direct_play_safe);
  if (safeExt && directSafe) return "direct";
  return "plex";
}
function pickStreamUrl(v) {
  if (!v) return "";
  const mode = getPreferredPlaybackMode(v, manualPlaybackMode);
  const plexUrl = getKnownPlexStreamUrl(v);
  const directUrl =
    (isDesktopClient() || isIOSLike()) && v.desktop_stream_url
      ? v.desktop_stream_url
      : v.stream_url || v.video_url;
  if (mode === "plex" && plexUrl) return withBase(plexUrl);
  if (directUrl) return withBase(directUrl);
  return withBase(plexUrl || "");
}
function pickStreamCandidates(v) {
  if (!v) return [];
  const out = [];
  const seen = new Set();
  const push = (u) => {
    const s = String(u || "").trim();
    if (!s || seen.has(s)) return;
    seen.add(s);
    out.push(withBase(s));
  };

  const mode = getPreferredPlaybackMode(v, manualPlaybackMode);
  const plexUrl = getKnownPlexStreamUrl(v);
  const name = String(v.name || "").toLowerCase();
  const rel = String(v.relative_path || "").toLowerCase();
  const isHeavyContainer =
    name.endsWith(".mkv") ||
    name.endsWith(".ts") ||
    rel.endsWith(".mkv") ||
    rel.endsWith(".ts");
  const directUrl =
    (isDesktopClient() || isIOSLike()) && v.desktop_stream_url
      ? v.desktop_stream_url
      : v.stream_url || v.video_url;

  if (manualPlaybackMode === "plex") {
    push(plexUrl);
    return out;
  }

  if (manualPlaybackMode === "direct") {
    push(directUrl);
    return out;
  }

  if (mode === "plex") {
    push(plexUrl);
    push(directUrl);
  } else {
    push(directUrl);
    push(plexUrl);
  }

  // For MKV/TS, keep soft transcode as last fallback.
  if (isHeavyContainer) push(v.soft_stream_url);

  return out;
}
function getCandidateFallbackDelay(url) {
  const s = String(url || "");
  if (!s) return 3200;
  if (s.includes(".m3u8")) {
    // Plex HLS can take a second or two to finish manifest/segment delivery on macOS
    if (isIOSLike()) return 10000;
    return 9000;
  }
  if (isDesktopClient()) return 5000;
  if (isIOSLike()) return 5000;
  return 3200;
}
function autoHideNativeControls() {
  if (!isIOSLike()) return;
  const poke = () => {
    try {
      mvideo.dispatchEvent(
        new PointerEvent("pointerdown", {
          bubbles: true,
          pointerType: "touch",
        }),
      );
    } catch (e) {}
    try {
      mvideo.dispatchEvent(
        new PointerEvent("pointerup", { bubbles: true, pointerType: "touch" }),
      );
    } catch (e) {}
    try {
      mvideo.dispatchEvent(
        new TouchEvent("touchstart", { bubbles: true, cancelable: true }),
      );
    } catch (e) {}
    try {
      mvideo.dispatchEvent(
        new TouchEvent("touchend", { bubbles: true, cancelable: true }),
      );
    } catch (e) {}
    try {
      mvideo.dispatchEvent(
        new MouseEvent("click", { bubbles: true, cancelable: true }),
      );
    } catch (e) {}
  };
  setTimeout(poke, 220);
  setTimeout(poke, 520);
}
let videos = [];
let filteredVideos = [];
let folderListCache = [];
let catalogStatus = { available: true };
let privateMode = localStorage.getItem("movies_private_mode") === "1";
let serverConfig = { debug_enabled: false };
let serverConfigPromise = null;
let debugEnabled = false;
const debugState = {
  currentVideoId: null,
  lastCandidate: "",
  candidates: [],
  defaultMode: null,
};
let privatePasscode = "";
function setPrivateMode(v) {
  privateMode = !!v;
  localStorage.setItem("movies_private_mode", privateMode ? "1" : "0");
}
function getOrCreateDeviceId() {
  const k = "movies_device_id";
  let v = localStorage.getItem(k);
  if (v) return v;
  v =
    window.crypto && crypto.randomUUID
      ? crypto.randomUUID()
      : "dev-" + Math.random().toString(36).slice(2) + Date.now().toString(36);
  localStorage.setItem(k, v);
  return v;
}
const deviceId = getOrCreateDeviceId();
let currentSubtitleObjectUrl = null;
const CACHE_SCHEMA_VERSION = 4;
const CACHE_DB_NAME = "movies-cache";
const CACHE_STORE_NAME = "snapshots";
const CACHE_MAX_AGE_MS = 24 * 60 * 60 * 1000;
const CACHE_MAX_RECORDS = 8;
const CACHE_MAX_BYTES = 18 * 1024 * 1024;
function deviceHeaders(extra = {}) {
  return { ...extra, "X-Device-Id": deviceId };
}

async function loadServerConfig() {
  if (serverConfigPromise) return serverConfigPromise;
  serverConfigPromise = (async () => {
    try {
      const res = await fetch(apiUrl("config"), {
        headers: deviceHeaders(),
      });
      if (!res.ok) return;
      const data = await res.json();
      serverConfig = data || {};
      debugEnabled = !!serverConfig.debug_enabled;
      updateDebugPanel();
      return serverConfig;
    } catch (err) {
      return null;
    }
  })();
  return serverConfigPromise;
}

let debugDragActive = false;
const debugDragState = {
  startX: 0,
  startY: 0,
  startLeft: 0,
  startTop: 0,
};
let panelPosition = { left: null, top: null };
const PANEL_PEEK_RATIO = 0.1;
const PANEL_MIN_PEEK = 32;
let debugHiddenSide = null;
const supportsPointerEvents = typeof window.PointerEvent !== "undefined";
const isTouchDevice = !!("ontouchstart" in window || navigator.maxTouchPoints > 0);
const touchDragOptions = { passive: false };

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function setPanelPosition(left, top) {
  if (!debugPanel) return;
  const rect = debugPanel.getBoundingClientRect();
  const maxLeft = window.innerWidth - rect.width * 0.05;
  const minLeft = -rect.width * 0.95;
  const clampedLeft = clamp(left, minLeft, maxLeft);
  const clampedTop = clamp(top, 10, window.innerHeight - rect.height - 10);
  panelPosition.left = clampedLeft;
  panelPosition.top = clampedTop;
  debugPanel.style.left = `${clampedLeft}px`;
  debugPanel.style.top = `${clampedTop}px`;
  debugPanel.style.right = "auto";
  debugPanel.style.bottom = "auto";
}

function updateDebugCornerVisibility() {
  if (!debugCorner) return;
  const visible = !!debugHiddenSide;
  debugCorner.classList.toggle("visible", visible);
  debugCorner.setAttribute("aria-hidden", visible ? "false" : "true");
}

function ensureDebugPanelTouchMode() {
  if (!debugPanel) return;
  debugPanel.classList.toggle("touch-enabled", isTouchDevice);
}

function ensureDefaultPosition() {
  if (!debugPanel) return;
  if (panelPosition.left != null && panelPosition.top != null) return;
  const computedStyle = window.getComputedStyle(debugPanel);
  const wasHidden = computedStyle.display === "none";
  const prevDisplay = debugPanel.style.display;
  if (wasHidden) {
    debugPanel.style.display = "block";
  }
  const rect = debugPanel.getBoundingClientRect();
  const defaultLeft = window.innerWidth - rect.width - 16;
  const defaultTop = window.innerHeight - rect.height - 16;
  panelPosition.left = clamp(
    defaultLeft,
    10,
    window.innerWidth - rect.width - 10,
  );
  panelPosition.top = clamp(
    defaultTop,
    10,
    window.innerHeight - rect.height - 10,
  );
  if (wasHidden) {
    debugPanel.style.display = prevDisplay || "";
  }
}

function restorePanelPosition(forceDefault = false) {
  if (!debugPanel) return;
  const rect = debugPanel.getBoundingClientRect();
  if (forceDefault) {
    panelPosition.left = null;
    panelPosition.top = null;
  }
  if (forceDefault) {
    ensureDefaultPosition();
  } else if (debugHiddenSide) {
    const clampedTop = clamp(
      panelPosition.top ?? rect.top,
      10,
      window.innerHeight - rect.height - 10,
    );
    panelPosition.top = clampedTop;
    const defaultLeftRight = clamp(
      window.innerWidth - rect.width - 16,
      10,
      window.innerWidth - rect.width - 10,
    );
    const defaultLeftLeft = clamp(16, 10, window.innerWidth - rect.width - 10);
    panelPosition.left = debugHiddenSide === "left"
      ? defaultLeftLeft
      : defaultLeftRight;
  } else if (panelPosition.left == null || panelPosition.top == null) {
    ensureDefaultPosition();
  }
  debugHiddenSide = null;
  debugPanel.dataset.hiddenSide = "";
  setPanelPosition(panelPosition.left, panelPosition.top);
  debugPanel.style.transform = "translate(0, 0)";
  updateDebugCornerVisibility();
}

function peekHidePanel(side) {
  if (!debugPanel) return;
  const rect = debugPanel.getBoundingClientRect();
  const peek = Math.max(PANEL_MIN_PEEK, rect.width * PANEL_PEEK_RATIO);
  const top = clamp(rect.top, 10, window.innerHeight - rect.height - 10);
  const left = side === "left" ? -rect.width + peek : window.innerWidth - peek;
  setPanelPosition(left, top);
  debugPanel.style.transform = "translate(0, 0)";
  debugHiddenSide = side;
  debugPanel.dataset.hiddenSide = side;
  updateDebugCornerVisibility();
}

function snapPanelToEdge() {
  if (!debugPanel) return;
  const rect = debugPanel.getBoundingClientRect();
  const fullWidth = rect.width;
  const leftHidden = rect.left < -fullWidth * 0.3;
  const rightHidden = rect.right > window.innerWidth + fullWidth * 0.3;
  if (leftHidden) {
    peekHidePanel("left");
    return;
  }
  if (rightHidden) {
    peekHidePanel("right");
    return;
  }
  restorePanelPosition();
}

function showDebugPanel() {
  if (!debugPanel || !debugEnabled) return;
  ensureDebugPanelTouchMode();
  debugPanel.style.display = "block";
  restorePanelPosition(true);
  debugPanel.classList.add("visible");
  updateDebugCornerVisibility();
}

function hideDebugPanel() {
  if (!debugPanel) return;
  debugPanel.style.display = "none";
  debugPanel.classList.remove("visible");
  debugHiddenSide = null;
  if (debugPanel) debugPanel.dataset.hiddenSide = "";
  updateDebugCornerVisibility();
}

function getPointerPoint(e) {
  if (!e) return null;
  if (e.touches && e.touches[0]) return e.touches[0];
  if (e.changedTouches && e.changedTouches[0]) return e.changedTouches[0];
  return e;
}

function handleDebugDragStart(e) {
  if (!debugEnabled) return;
  const point = getPointerPoint(e);
  if (!point || !debugPanel) return;
  if (debugHiddenSide) {
    restorePanelPosition();
    debugHiddenSide = null;
    e.preventDefault();
    return;
  }
  debugDragActive = true;
  debugPanel.classList.add("dragging");
  const rect = debugPanel.getBoundingClientRect();
  debugDragState.startX = point.clientX;
  debugDragState.startY = point.clientY;
  debugDragState.startLeft = rect.left;
  debugDragState.startTop = rect.top;
  attachDragListeners();
  e.preventDefault();
}

function handleDebugDragMove(e) {
  if (!debugDragActive) return;
  const point = getPointerPoint(e);
  if (!point) return;
  const dx = point.clientX - debugDragState.startX;
  const dy = point.clientY - debugDragState.startY;
  setPanelPosition(
    debugDragState.startLeft + dx,
    debugDragState.startTop + dy,
  );
  e.preventDefault();
}

function handleDebugDragEnd() {
  if (!debugDragActive) return;
  debugDragActive = false;
  if (debugPanel) debugPanel.classList.remove("dragging");
  detachDragListeners();
  snapPanelToEdge();
}

let dragListenersAttached = false;
function attachDragListeners() {
  if (dragListenersAttached) return;
  dragListenersAttached = true;
  if (supportsPointerEvents) {
    window.addEventListener("pointermove", handleDebugDragMove);
    window.addEventListener("pointerup", handleDebugDragEnd);
    window.addEventListener("pointercancel", handleDebugDragEnd);
  } else {
    window.addEventListener("mousemove", handleDebugDragMove);
    window.addEventListener("mouseup", handleDebugDragEnd);
    window.addEventListener(
      "touchmove",
      handleDebugDragMove,
      touchDragOptions,
    );
    window.addEventListener("touchend", handleDebugDragEnd);
    window.addEventListener("touchcancel", handleDebugDragEnd);
  }
}

function detachDragListeners() {
  if (!dragListenersAttached) return;
  if (supportsPointerEvents) {
    window.removeEventListener("pointermove", handleDebugDragMove);
    window.removeEventListener("pointerup", handleDebugDragEnd);
    window.removeEventListener("pointercancel", handleDebugDragEnd);
  } else {
    window.removeEventListener("mousemove", handleDebugDragMove);
    window.removeEventListener("mouseup", handleDebugDragEnd);
    window.removeEventListener(
      "touchmove",
      handleDebugDragMove,
      touchDragOptions,
    );
    window.removeEventListener("touchend", handleDebugDragEnd);
    window.removeEventListener("touchcancel", handleDebugDragEnd);
  }
  dragListenersAttached = false;
}

function updateDebugPanel() {
  if (!debugPanel || !debugOutput) return;
  if (!debugEnabled) {
    hideDebugPanel();
    return;
  }
  const scan = catalogStatus?.scan_progress || {};
  const lines = [
    `default: ${debugState.defaultMode || "unknown"}`,
    `playback: ${currentPlaybackMode || "idle"}`,
    `whitelist: ${
      Array.isArray(serverConfig?.direct_audio_whitelist)
        ? serverConfig.direct_audio_whitelist.join(", ") || "none"
        : "none"
    }`,
    `video: ${debugState.currentVideoId || "idle"}`,
    `candidate: ${debugState.lastCandidate || "n/a"}`,
    `scan: ${scan.phase || "idle"} entries:${
      scan.processed_entries ?? 0
    } videos:${scan.videos_found ?? 0}`,
  ];
  debugOutput.innerHTML = lines.map((line) => escapeHtml(line)).join("<br />");
  showDebugPanel();
}
function openCacheDb() {
  return new Promise((resolve, reject) => {
    if (!window.indexedDB) return resolve(null);
    const req = indexedDB.open(CACHE_DB_NAME, 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(CACHE_STORE_NAME)) {
        db.createObjectStore(CACHE_STORE_NAME);
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
async function cacheGetRaw(key) {
  const db = await openCacheDb();
  if (!db) return null;
  return new Promise((resolve, reject) => {
    const tx = db.transaction(CACHE_STORE_NAME, "readonly");
    const req = tx.objectStore(CACHE_STORE_NAME).get(key);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => reject(req.error);
  }).finally(() => db.close());
}
async function cacheSetRaw(key, value) {
  const db = await openCacheDb();
  if (!db) return;
  return new Promise((resolve, reject) => {
    const tx = db.transaction(CACHE_STORE_NAME, "readwrite");
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.objectStore(CACHE_STORE_NAME).put(value, key);
  }).finally(() => db.close());
}
async function cacheDeleteRaw(key) {
  const db = await openCacheDb();
  if (!db) return;
  return new Promise((resolve, reject) => {
    const tx = db.transaction(CACHE_STORE_NAME, "readwrite");
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.objectStore(CACHE_STORE_NAME).delete(key);
  }).finally(() => db.close());
}
async function cacheListRecords() {
  const db = await openCacheDb();
  if (!db) return [];
  return new Promise((resolve, reject) => {
    const out = [];
    const tx = db.transaction(CACHE_STORE_NAME, "readonly");
    const store = tx.objectStore(CACHE_STORE_NAME);
    const req = store.openCursor();
    req.onsuccess = () => {
      const cursor = req.result;
      if (!cursor) {
        resolve(out);
        return;
      }
      out.push({ key: cursor.key, value: cursor.value });
      cursor.continue();
    };
    req.onerror = () => reject(req.error);
  }).finally(() => db.close());
}
async function cacheClearAll() {
  const db = await openCacheDb();
  if (!db) return;
  return new Promise((resolve, reject) => {
    const tx = db.transaction(CACHE_STORE_NAME, "readwrite");
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
    tx.objectStore(CACHE_STORE_NAME).clear();
  }).finally(() => db.close());
}
function playbackOverrideKey(videoId) {
  return `${PLAYBACK_OVERRIDE_PREFIX}${videoId}`;
}
async function loadManualPlaybackOverride(videoId) {
  if (!videoId) return null;
  const stored = await cacheGetRaw(playbackOverrideKey(videoId));
  return stored === "plex" || stored === "direct" ? stored : null;
}
async function persistManualPlaybackOverride(videoId, mode) {
  if (!videoId) return;
  const key = playbackOverrideKey(videoId);
  if (!mode) {
    await cacheDeleteRaw(key);
    return;
  }
  await cacheSetRaw(key, mode);
}
function estimateCacheBytes(payload) {
  try {
    return new Blob([JSON.stringify(payload)]).size;
  } catch (e) {
    return JSON.stringify(payload).length;
  }
}
function currentSnapshotCacheKey() {
  return JSON.stringify({
    v: CACHE_SCHEMA_VERSION,
    deviceId,
    folder: currentFolderFilter(),
    q: (q?.value || "").trim(),
    privateMode: privateMode ? 1 : 0,
  });
}
function stripDeviceIdFromUrl(url) {
  const raw = String(url || "").trim();
  if (!raw) return raw;
  if (/(^|\/)video\/[^/?#]+/i.test(raw)) return raw;
  try {
    const u = new URL(raw, window.location.origin);
    if (/(^|\/)video\/[^/?#]+/i.test(u.pathname)) return raw;
    u.searchParams.delete("device_id");
    return u.origin === window.location.origin
      ? `${u.pathname}${u.search}${u.hash}`
      : u.toString();
  } catch (e) {
    return raw.replace(/([?&])device_id=[^&]*&?/g, "$1").replace(/[?&]$/, "");
  }
}
function normalizeVideoRecord(v) {
  if (!v || typeof v !== "object") return v;
  const out = { ...v };
  for (const key of [
    "video_url",
    "stream_url",
    "desktop_stream_url",
    "soft_stream_url",
    "plex_stream_url",
    "subtitle_url",
    "thumb_url",
  ]) {
    if (out[key]) out[key] = stripDeviceIdFromUrl(out[key]);
  }
  if (!out.plex_stream_url) {
    const derivedPlexUrl = getKnownPlexStreamUrl(out);
    if (derivedPlexUrl) out.plex_stream_url = derivedPlexUrl;
  }
  if (Array.isArray(out.preview_urls))
    out.preview_urls = out.preview_urls.map(stripDeviceIdFromUrl);
  return out;
}
async function pruneSnapshotCache() {
  const now = Date.now();
  const records = await cacheListRecords();
  let totalBytes = 0;
  const keep = [];
  for (const rec of records) {
    const isOverride = String(rec.key || "").startsWith(PLAYBACK_OVERRIDE_PREFIX);
    if (isOverride) continue;

    const value = rec.value || {};
    const savedAt = Number(value.savedAt || 0);
    const expired = !savedAt || now - savedAt > CACHE_MAX_AGE_MS;
    if (expired) {
      await cacheDeleteRaw(rec.key);
      continue;
    }
    totalBytes += Number(value.bytes || 0);
    keep.push({
      key: rec.key,
      bytes: Number(value.bytes || 0),
      lastAccessedAt: Number(value.lastAccessedAt || value.savedAt || 0),
      savedAt,
    });
  }
  if (keep.length <= CACHE_MAX_RECORDS && totalBytes <= CACHE_MAX_BYTES) return;
  keep.sort((a, b) => {
    if (a.lastAccessedAt !== b.lastAccessedAt)
      return a.lastAccessedAt - b.lastAccessedAt;
    return a.savedAt - b.savedAt;
  });
  while (keep.length > CACHE_MAX_RECORDS || totalBytes > CACHE_MAX_BYTES) {
    const victim = keep.shift();
    if (!victim) break;
    totalBytes -= victim.bytes;
    await cacheDeleteRaw(victim.key);
  }
}
async function loadSnapshotFromCache() {
  try {
    const key = currentSnapshotCacheKey();
    const record = await cacheGetRaw(key);
    if (!record || !record.payload) return null;
    const savedAt = Number(record.savedAt || 0);
    if (!savedAt || Date.now() - savedAt > CACHE_MAX_AGE_MS) {
      await cacheDeleteRaw(key);
      return null;
    }
    record.lastAccessedAt = Date.now();
    await cacheSetRaw(key, record);
    return record.payload;
  } catch (e) {
    return null;
  }
}
async function saveSnapshotToCache() {
  if (!videos.length) return;
  try {
    const payload = {
      catalogStatus,
      folderListCache,
      videos,
      serverTotal,
      serverOffset,
      serverExhausted,
    };
    await cacheSetRaw(currentSnapshotCacheKey(), {
      savedAt: Date.now(),
      lastAccessedAt: Date.now(),
      bytes: estimateCacheBytes(payload),
      payload,
    });
    await pruneSnapshotCache();
  } catch (e) {}
}
function applyCachedSnapshot(snapshot) {
  if (!snapshot || !Array.isArray(snapshot.videos) || !snapshot.videos.length)
    return false;
  catalogStatus = snapshot.catalogStatus || { available: true };
  folderListCache = Array.isArray(snapshot.folderListCache)
    ? snapshot.folderListCache
    : [];
  videos = snapshot.videos.map(normalizeVideoRecord);
  filteredVideos = videos;
  refreshFilteredIndexMap();
  serverTotal = Number(snapshot.serverTotal || videos.length || 0);
  serverOffset = Number(snapshot.serverOffset || videos.length || 0);
  serverExhausted = Boolean(
    snapshot.serverExhausted || (serverTotal && videos.length >= serverTotal),
  );
  prefetchBuffer = [];
  preloadedThumbUrls.clear();
  queuedThumbUrls.clear();
  thumbPrefetchQueue = [];
  activeThumbPrefetches = 0;
  suppressFolderChange = true;
  refreshFolders();
  suppressFolderChange = false;
  updatePrivateToggle();
  render();
  uiReady = true;
  scheduleThumbPrefetch();
  return true;
}
function cleanupSubtitleObjectUrl() {
  if (!currentSubtitleObjectUrl) return;
  try {
    URL.revokeObjectURL(currentSubtitleObjectUrl);
  } catch (e) {}
  currentSubtitleObjectUrl = null;
}
async function resolveSubtitleTrackSrc(url) {
  const src = String(url || "").trim();
  if (!src) return "";
  const res = await fetch(src, { headers: deviceHeaders() });
  if (!res.ok) throw new Error(`subtitle_${res.status}`);
  const blob = await res.blob();
  cleanupSubtitleObjectUrl();
  currentSubtitleObjectUrl = URL.createObjectURL(blob);
  return currentSubtitleObjectUrl;
}
let renderCount = 0;
let loadingMore = false;
let lastScrollY = 0;
const INITIAL_RENDER_COUNT = 200;
const RENDER_BATCH_SIZE = 200;
const RENDER_NEXT_THRESHOLD = 100;
const API_PAGE_SIZE = 200;
const BASE_THUMB_PREFETCH_AHEAD = 48;
const FAST_THUMB_PREFETCH_AHEAD = 120;
const THUMB_PREFETCH_BEHIND = 16;
const MAX_THUMB_PREFETCH_CONCURRENCY = 8;
const PREFETCH_AHEAD_BATCH = 0;
let serverTotal = 0;
let serverOffset = 0;
let serverExhausted = false;
let fetchingPage = false;
let activeLoadId = 0;
let prefetchBuffer = [];
let suppressFolderChange = false;
let uiReady = false;
let loadInFlight = null;
let lastAppliedFolderValue = "";
let lastAppliedQueryValue = "";
const preloadedThumbUrls = new Set();
const queuedThumbUrls = new Set();
let thumbPrefetchQueue = [];
let activeThumbPrefetches = 0;
let filteredIndexMap = new Map();
let lastScrollSampleY = 0;
let lastScrollSampleAt = 0;
let scrollVelocity = 0;
let thumbPrefetchTimer = null;
function updateStat() {
  const loaded = Math.min(renderCount, filteredVideos.length);
  const total = serverTotal || filteredVideos.length || loaded;
  stat.textContent = `Loaded ${loaded} / Total ${total}`;
}

function drainPrefetchBuffer() {
  if (!prefetchBuffer.length) return;
  const seen = new Set(videos.map((v) => v.id));
  for (const it of prefetchBuffer) {
    if (!it || !it.id || seen.has(it.id)) continue;
    seen.add(it.id);
    videos.push(it);
  }
  prefetchBuffer = [];
  filteredVideos = videos;
}
const grid = document.getElementById("grid"),
  q = document.getElementById("q"),
  folder = document.getElementById("folderSelect"),
  folderBtn = document.getElementById("folderBtn"),
  folderPanel = document.getElementById("folderPanel"),
  folderSearch = document.getElementById("folderSearch"),
  folderOptions = document.getElementById("folderOptions"),
  stat = document.getElementById("stat"),
  notice = document.getElementById("notice"),
  tt = document.getElementById("tt"),
  scrollSentinel = document.getElementById("scrollSentinel"),
  debugPanel = document.getElementById("debugPanel"),
  debugOutput = document.getElementById("debugOutput");
const debugCorner = document.getElementById("debugCorner");
let currentMobileCols = 4;
let mobileZoomLevel = readPersistedMobileZoomLevel();
applyMobileColumnSetting();
const toTopBtn = document.getElementById("toTopBtn");
const preloadOverlay = document.getElementById("preloadOverlay");
const modal = document.getElementById("modal"),
  mbox = modal.querySelector(".box"),
  mclose = document.getElementById("mclose"),
  mtitle = document.getElementById("mtitle"),
  mvideo = document.getElementById("mvideo"),
  mss = document.getElementById("mss"),
  msub = document.getElementById("msub"),
  vloader = document.getElementById("vloader");
plexButton = document.getElementById("mplex");
if (plexButton) {
  plexButton.addEventListener("click", cycleManualPlaybackMode);
}
if (debugPanel) {
  if (supportsPointerEvents) {
    debugPanel.addEventListener("pointerdown", handleDebugDragStart);
  } else {
    debugPanel.addEventListener("mousedown", handleDebugDragStart);
    debugPanel.addEventListener("touchstart", handleDebugDragStart, {
      passive: false,
    });
  }
  debugPanel.addEventListener("click", (event) => {
    if (debugHiddenSide) {
      restorePanelPosition();
      event.stopPropagation();
    }
  });
  ensureDebugPanelTouchMode();
}

if (debugCorner) {
  debugCorner.addEventListener("click", (event) => {
    restorePanelPosition();
    event.preventDefault();
    event.stopPropagation();
  });
}
updateDebugCornerVisibility();
grid.classList.toggle("zoomed", isMobileLayout() && mobileZoomLevel > 1);
const pmodal = document.getElementById("pmodal"),
  ppass = document.getElementById("ppass"),
  pcancel = document.getElementById("pcancel"),
  pok = document.getElementById("pok");
const emodal = document.getElementById("emodal"),
  emsg = document.getElementById("emsg"),
  eok = document.getElementById("eok");
let currentSubtitleUrl = null;
let subtitleEnabled = false;
let currentSubtitleTrack = null;
let hlsPlayer = null;
let slideshowEnabled = false;
let currentVideoId = null;
let currentVideoRecord = null;
let hlsLoadingPromise = null;
let backgroundPageLoading = false;
let playerSessionId = 0;
const ENABLE_PREVIEW_FRAMES = true;

function getPreviewFrameUrls(video) {
  const raw = Array.isArray(video?.preview_urls) ? video.preview_urls : [];
  return [...new Set(raw.map((u) => withBase(u)).filter(Boolean))];
}

function preloadPreviewFrames(urls) {
  // Warm browser HTTP cache only (no JS data/image cache).
  for (const u of urls) {
    const im = new Image();
    im.decoding = "async";
    im.loading = "eager";
    im.src = u;
  }
}

function showPreloadOverlay() {
  if (preloadOverlay) preloadOverlay.classList.add("on");
}

function hidePreloadOverlay() {
  if (preloadOverlay) preloadOverlay.classList.remove("on");
}

function loadHlsLibrary() {
  if (window.Hls) return Promise.resolve(true);
  if (hlsLoadingPromise) return hlsLoadingPromise;
  const cdns = [
    "https://cdn.jsdelivr.net/npm/hls.js@1",
    "https://unpkg.com/hls.js@1/dist/hls.min.js",
  ];
  hlsLoadingPromise = new Promise((resolve) => {
    let idx = 0;
    const tryNext = () => {
      if (window.Hls) return resolve(true);
      if (idx >= cdns.length) return resolve(false);
      const s = document.createElement("script");
      s.src = cdns[idx++];
      s.async = true;
      s.onload = () => resolve(!!window.Hls);
      s.onerror = () => tryNext();
      document.head.appendChild(s);
    };
    tryNext();
  });
  return hlsLoadingPromise;
}
async function openPlayer(urlOrCandidates, name, subtitleUrl) {
  const sessionId = ++playerSessionId;
  const isActiveSession = () => sessionId === playerSessionId;
  if (folderPanel) folderPanel.style.display = "none";
  const candidates = Array.isArray(urlOrCandidates)
    ? urlOrCandidates.filter(Boolean)
    : [urlOrCandidates].filter(Boolean);
  let activeUrl = candidates[0] || "";
  const rawVideoId =
    (String(activeUrl || "").match(
      /\/(?:video|hls|plex\/video)\/([^/?#]+)/,
    ) || [])[1] || null;
  const videoId = rawVideoId
    ? String(rawVideoId).replace(/\.m3u8$/i, "")
    : null;
  if (!videoId) {
    manualPlaybackMode = null;
  }
  skipManualOverrideLoad = false;
  currentVideoId = videoId || null;
  currentVideoRecord =
    currentVideoId && videos.length
      ? videos.find((v) => v.id === currentVideoId) || currentVideoRecord
      : currentVideoRecord;
  debugState.currentVideoId = videoId;
  debugState.candidates = candidates;
  debugState.defaultMode = currentVideoRecord
    ? getPreferredPlaybackMode(currentVideoRecord)
    : null;
  updateDebugPanel();
  const fallback = currentVideoRecord || null;
  const fallbackVideoUrl =
    fallback && fallback.video_url
      ? withBase(stripDeviceIdFromUrl(fallback.video_url))
      : "";
  const resolvedSubtitle =
    subtitleUrl !== undefined && subtitleUrl !== null && subtitleUrl !== ""
      ? subtitleUrl
      : fallback && fallback.subtitle_url
        ? withBase(fallback.subtitle_url)
        : null;
  console.log("openPlayer called:", {
    candidates,
    activeUrl,
    name,
    subtitleUrl,
    resolvedSubtitle,
    fallbackVideoUrl,
  });
  mtitle.textContent = name || "播放";
  if (hlsPlayer) {
    try {
      hlsPlayer.destroy();
    } catch (e) {}
    hlsPlayer = null;
  }
  mvideo.removeAttribute("src");
  mvideo.load();
  const startPlayback = async (url) => {
    if (!isActiveSession()) return;
    if (!url) {
      mvideo.src = fallbackVideoUrl || "";
      return;
    }
    if (String(url || "").includes(".m3u8")) {
      const useNative = isIOSLike() && mvideo.canPlayType("application/vnd.apple.mpegurl");
      if (useNative) {
        mvideo.src = url || "";
      } else {
        const hasHls =
          window.Hls && window.Hls.isSupported
            ? window.Hls.isSupported()
            : false;
        const loaded = hasHls ? true : await loadHlsLibrary();
        if (!isActiveSession()) return;
        if (loaded && window.Hls && window.Hls.isSupported()) {
          let recoverCount = 0;
          hlsPlayer = new Hls({
            enableWorker: true,
            lowLatencyMode: false,
            backBufferLength: 30,
            maxBufferLength: 18,
            maxMaxBufferLength: 24,
            xhrSetup: (xhr) => {
              xhr.setRequestHeader("X-Device-Id", deviceId);
            },
          });
          hlsPlayer.on(Hls.Events.ERROR, (ev, data) => {
            if (!data || !data.fatal) return;
            if (
              data.type === Hls.ErrorTypes.NETWORK_ERROR &&
              recoverCount < 2
            ) {
              recoverCount++;
              try {
                hlsPlayer.startLoad();
                return;
              } catch (e) {}
            }
            if (data.type === Hls.ErrorTypes.MEDIA_ERROR && recoverCount < 2) {
              recoverCount++;
              try {
                hlsPlayer.recoverMediaError();
                return;
              } catch (e) {}
            }
            try {
              hlsPlayer.destroy();
            } catch (e) {}
            hlsPlayer = null;
            mvideo.src = fallbackVideoUrl || "";
            mvideo.play().catch(() => {});
          });
          hlsPlayer.loadSource(url || "");
          hlsPlayer.attachMedia(mvideo);
        } else {
          mvideo.src = fallbackVideoUrl || "";
        }
      }
    } else {
      mvideo.src = url || "";
    }
  };
  mvideo.querySelectorAll("track").forEach((t) => t.remove());
  cleanupSubtitleObjectUrl();
  currentSubtitleUrl = resolvedSubtitle;
  currentSubtitleTrack = null;
  subtitleEnabled = false;
  // Hide action buttons during loading
  msub.style.display = "none";
  mclose.style.display = "none";
  const attachSubtitleTrack = async () => {
    if (!isActiveSession()) return;
    if (!resolvedSubtitle) {
      msub.style.display = "none";
      return;
    }
    try {
      const trackSrc = await resolveSubtitleTrackSrc(resolvedSubtitle);
      if (!isActiveSession()) return;
      const track = document.createElement("track");
      track.kind = "subtitles";
      track.label = "Chinese (Traditional)";
      track.srclang = "zh-TW";
      track.src = trackSrc;
      track.default = true;
      mvideo.appendChild(track);
      currentSubtitleTrack = track;
      msub.textContent = "CC: On";
      subtitleEnabled = true;
      const applyMode = () => {
        setSubtitleMode(subtitleEnabled);
      };
      track.addEventListener("load", applyMode, { once: true });
      if (revealed) {
        msub.style.display = "inline-flex";
        applyMode();
      }
    } catch (e) {
      currentSubtitleUrl = null;
      currentSubtitleTrack = null;
      msub.style.display = "none";
    }
  };
  // Loading state: compact loader card
  const portrait = window.matchMedia("(orientation: portrait)").matches;
  mbox.style.width =
    window.innerWidth < 900 ? (portrait ? "250px" : "220px") : "420px";
  showPreloadOverlay();
  vloader.classList.remove("on");
  mvideo.style.display = "none";
  mvideo.style.visibility = "hidden";
  let revealed = false;
  let revealTimer = null;
  let candidateAttemptId = 0;
  let candidateFallbackTimer = null;
  let subtitleAttachStarted = false;
  const clearCandidateFallbackTimer = () => {
    if (!candidateFallbackTimer) return;
    clearTimeout(candidateFallbackTimer);
    candidateFallbackTimer = null;
  };
  const advanceCandidate = () => {
    if (!isActiveSession()) return;
    clearCandidateFallbackTimer();
    if (candidateIdx < candidates.length) {
      tryNextCandidate();
      return;
    }
    revealPlayer();
  };
  const revealPlayer = () => {
    if (!isActiveSession()) return;
    if (revealed) {
      relayoutModalBox();
      return;
    }
    revealed = true;
    try {
      if (revealTimer) clearTimeout(revealTimer);
    } catch (e) {}
    clearCandidateFallbackTimer();
    hidePreloadOverlay();
    if (!modal.classList.contains("on")) modal.classList.add("on");
    vloader.classList.remove("on");
    mvideo.style.display = "block";
    mvideo.style.visibility = "hidden";
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        relayoutModalBox();
        mvideo.style.visibility = "visible";
        mclose.style.display = "inline-flex";
        if (resolvedSubtitle) {
          msub.style.display = "inline-flex";
          setSubtitleMode(subtitleEnabled);
        }
      });
    });
  };
  mvideo.onloadedmetadata = revealPlayer;
  mvideo.onloadeddata = revealPlayer;
  mvideo.oncanplay = revealPlayer;
  mvideo.onplaying = () => {
    revealPlayer();
    relayoutModalBox();
    autoHideNativeControls();
    clearCandidateFallbackTimer();
  };
  mvideo.onresize = () => {
    relayoutModalBox();
  };
  let candidateIdx = 0;
  const tryNextCandidate = async () => {
    if (!isActiveSession()) return;
    const attemptId = ++candidateAttemptId;
    const next = candidates[candidateIdx++] || fallbackVideoUrl || "";
    activeUrl = next;
    const actualMode = next
      ? isPlexStreamUrl(next)
        ? "plex"
        : "direct"
      : null;
    updatePlexIndicator(actualMode);
    debugState.lastCandidate = activeUrl;
    updateDebugPanel();
    clearCandidateFallbackTimer();
    await startPlayback(next);
    if (!isActiveSession() || attemptId !== candidateAttemptId) return;
    if (!subtitleAttachStarted) {
      subtitleAttachStarted = true;
      attachSubtitleTrack();
    }
    if (!next.includes(".m3u8")) {
      candidateFallbackTimer = setTimeout(() => {
        if (attemptId !== candidateAttemptId || revealed) return;
        advanceCandidate();
      }, getCandidateFallbackDelay(next));
    } else {
      candidateFallbackTimer = null;
    }
    mvideo.play().catch((err) => {
      if (!isActiveSession() || attemptId !== candidateAttemptId) return;
      // iOS/iPadOS can reject autoplay-style play() after async work even though
      // the source is valid; do not treat that as a fatal playback candidate error.
      if (
        isIOSLike() &&
        err &&
        (err.name === "NotAllowedError" || err.name === "AbortError")
      ) {
        revealPlayer();
        return;
      }
      advanceCandidate();
    });
  };

  mvideo.onerror = () => {
    if (!isActiveSession()) return;
    advanceCandidate();
  };
  revealTimer = setTimeout(() => {
    if (!isActiveSession()) return;
    revealPlayer();
  }, 8000);

  await tryNextCandidate();
}

async function playVideoWithOverride(video, subtitleUrl) {
  if (!video) return;
  if (!skipManualOverrideLoad && video.id) {
    manualPlaybackMode = await loadManualPlaybackOverride(video.id);
  }
  const resolvedSubtitle =
    subtitleUrl !== undefined && subtitleUrl !== null && subtitleUrl !== ""
      ? subtitleUrl
      : video.subtitle_url
        ? withBase(video.subtitle_url)
        : null;
  openPlayer(pickStreamCandidates(video), video.name, resolvedSubtitle);
}
function relayoutModalBox() {
  if (!modal.classList.contains("on")) return;
  const vw = Math.max(
    320,
    window.innerWidth || document.documentElement.clientWidth || 320,
  );
  const vh = Math.max(
    320,
    window.innerHeight || document.documentElement.clientHeight || 320,
  );
  const chromeH = 56; // top bar height
  const maxW = Math.floor(vw * 0.96);
  const maxH = Math.floor(vh * 0.94) - chromeH;
  const vW = mvideo.videoWidth || 0;
  const vH = mvideo.videoHeight || 0;
  if (vW > 0 && vH > 0) {
    const scale = Math.min(maxW / vW, maxH / vH, 1);
    const boxW = Math.max(220, Math.floor(vW * scale));
    mbox.style.width = `${boxW}px`;
  } else {
    const portrait = window.matchMedia("(orientation: portrait)").matches;
    mbox.style.width =
      window.innerWidth < 900 ? (portrait ? "250px" : "220px") : "420px";
  }
}
function closePlayer() {
  playerSessionId += 1;
  try {
    mvideo.pause();
  } catch (e) {}
  if (hlsPlayer) {
    try {
      hlsPlayer.destroy();
    } catch (e) {}
    hlsPlayer = null;
  }
  cleanupSubtitleObjectUrl();
  currentSubtitleTrack = null;
  hidePreloadOverlay();
  mvideo.removeAttribute("src");
  mvideo.load();
  mvideo.style.display = "block";
  mvideo.style.visibility = "visible";
  vloader.classList.remove("on");
  mclose.style.display = "inline-flex";
  if (currentSubtitleUrl) {
    msub.style.display = "inline-flex";
  }
  mbox.style.width = "";
  modal.classList.remove("on");
  currentVideoId = null;
  currentVideoRecord = null;
  updatePlexIndicator(null);
  debugState.currentVideoId = null;
  debugState.lastCandidate = "";
  debugState.candidates = [];
  debugState.defaultMode = null;
  updateDebugPanel();
}
function playNextInSlideshow() {
  if (!slideshowEnabled || !currentVideoId) return;
  const idx = filteredVideos.findIndex((v) => v.id === currentVideoId);
  if (idx < 0) return;
  const next = filteredVideos[idx + 1];
  if (!next) {
    slideshowEnabled = false;
    mss.textContent = "Slideshow: Off";
    return;
  }
  currentVideoRecord = next;
  const sub = next && next.subtitle_url ? withBase(next.subtitle_url) : null;
  playVideoWithOverride(next, sub);
}
function setSubtitleMode(on) {
  const desiredMode = on ? "showing" : "disabled";
  if (currentSubtitleTrack && currentSubtitleTrack.track) {
    try {
      currentSubtitleTrack.track.mode = desiredMode;
    } catch (e) {}
  }
  const tracks = mvideo.textTracks || [];
  for (let i = 0; i < tracks.length; i++) {
    try {
      tracks[i].mode = desiredMode;
    } catch (e) {}
  }
}
function toggleSubtitle() {
  if (!currentSubtitleUrl) return;
  subtitleEnabled = !subtitleEnabled;
  setSubtitleMode(subtitleEnabled);
  msub.textContent = subtitleEnabled ? "CC: On" : "CC: Off";
}
function openPassModal() {
  ppass.value = "";
  pmodal.classList.add("on");
  setTimeout(() => ppass.focus(), 30);
}
function closePassModal() {
  pmodal.classList.remove("on");
}
function showErrorModal(msg) {
  emsg.textContent = msg || "發生錯誤";
  emodal.classList.add("on");
}
function closeErrorModal() {
  emodal.classList.remove("on");
}
mclose.addEventListener("click", closePlayer);
mss.addEventListener("click", () => {
  slideshowEnabled = !slideshowEnabled;
  mss.textContent = slideshowEnabled ? "Slideshow: On" : "Slideshow: Off";
});
msub.addEventListener("click", toggleSubtitle);
mvideo.addEventListener("ended", playNextInSlideshow);
modal.addEventListener("click", (e) => {
  if (e.target === modal) closePlayer();
});
if (preloadOverlay) {
  preloadOverlay.addEventListener("click", closePlayer);
}
pcancel.addEventListener("click", closePassModal);
eok.addEventListener("click", closeErrorModal);
emodal.addEventListener("click", (e) => {
  if (e.target === emodal) closeErrorModal();
});
pok.addEventListener("click", async () => {
  const code = (ppass.value || "").trim();
  if (!code) {
    ppass.focus();
    return;
  }
  let ok = false;
  try {
    const r = await fetch(apiUrl("private/unlock"), {
      method: "POST",
      headers: deviceHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ passcode: code }),
    });
    ok = !!r.ok;
  } catch (e) {}
  if (!ok) {
    showErrorModal("Wrong passcode");
    return;
  }
  setPrivateMode(true);
  privatePasscode = "";
  closePassModal();

  // wait a short moment for backend authorized-state visibility, then reload.
  try {
    for (let i = 0; i < 4; i++) {
      const sr = await fetch(apiUrl("status"), { headers: deviceHeaders() });
      const sj = await sr.json().catch(() => ({}));
      if (sj && sj.private_authorized) break;
      await new Promise((r) => setTimeout(r, 150));
    }
  } catch (e) {}

  await cacheClearAll().catch(() => {});
  await load(true);
});
ppass.addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    pok.click();
  }
  if (e.key === "Escape") {
    closePassModal();
  }
});
pmodal.addEventListener("click", (e) => {
  if (e.target === pmodal) closePassModal();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modal.classList.contains("on")) closePlayer();
});
const aspectMap = {};
let relayoutTimer = null;
const TARGET_ROW_H = 260;
const MIN_ROW_H = 190;
const MAX_ROW_H = 340;
const ZOOMED_TARGET_ROW_H = 200;
const ZOOMED_MIN_ROW_H = 60;
const ZOOMED_MAX_ROW_H = 320;
const ZOOMED_LANDSCAPE_MAX_ROW_H = 180;
const ZOOMED_LANDSCAPE_MIN_ROW_H = 60;
const ZOOM_FADER_DURATION = 220;
let zoomFadeOutTimer = null;
let zoomFadeInTimer = null;
let zoomTransitionActive = false;
let pendingRow = [];
let pendingSumAr = 0;

function getLayoutAr(v) {
  const ar = Number(v?.ar || 0);
  if (ar > 0) return ar;
  return aspectMap[v?.id] || 1.6;
}

function isMobileLayout() {
  const coarse = window.matchMedia("(pointer: coarse)").matches;
  const hasTouch = !!(
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0 ||
    navigator.msMaxTouchPoints > 0
  );
  return hasTouch || window.innerWidth < 1000 || coarse;
}

function applyMobileColumnSetting() {
  const zoomCols = mobileZoomLevel > 1 ? getMobileZoomRowLimit() : currentMobileCols;
  grid.style.setProperty("--mobile-cols", String(zoomCols));
}

function updateMobileCols() {
  const coarse = window.matchMedia("(pointer: coarse)").matches;
  const landscape = window.matchMedia("(orientation: landscape)").matches;
  let cols = 4;
  if (isIPadClient()) cols = landscape ? 8 : 6;
  else if (coarse && landscape) cols = 8;
  currentMobileCols = cols;
  applyMobileColumnSetting();
  return cols;
}

function scheduleRelayout() {
  if (relayoutTimer) clearTimeout(relayoutTimer);
  relayoutTimer = setTimeout(() => {
    relayoutTimer = null;
    buildRows(filteredVideos.slice(0, renderCount), {
      append: false,
      isFinal: renderCount >= filteredVideos.length && serverExhausted,
    });
  }, 80);
}

function bindCardEvents(scope) {
  scope.querySelectorAll(".card button").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const card = e.target.closest("article.card");
      if (card) {
        const v = videos.find((x) => x.id === card.dataset.id);
        const sub = v && v.subtitle_url ? withBase(v.subtitle_url) : null;
        currentVideoRecord = v || null;
        playVideoWithOverride(v, sub);
      }
    });
  });
  const pointerCoarse = window.matchMedia("(pointer: coarse)").matches;
  const pointerHover = window.matchMedia("(hover: hover)").matches;
  scope
    .querySelectorAll("article.card .name, article.card .sub")
    .forEach((el) => {
      const show = (e) => {
        const txt = el.getAttribute("data-fullname") || el.textContent || "";
        if (!txt) return;
        tt.textContent = txt;
        tt.style.display = "block";
        tt.style.left = `${Math.min(window.innerWidth - 20, e.clientX + 12)}px`;
        tt.style.top = `${Math.min(window.innerHeight - 20, e.clientY + 18)}px`;
      };
      const move = (e) => {
        if (tt.style.display === "block") {
          tt.style.left = `${Math.min(window.innerWidth - 20, e.clientX + 12)}px`;
          tt.style.top = `${Math.min(window.innerHeight - 20, e.clientY + 18)}px`;
        }
      };
      const hide = () => {
        tt.style.display = "none";
      };
      el.addEventListener("mouseenter", show);
      el.addEventListener("mousemove", move);
      el.addEventListener("mouseleave", hide);
    });
  scope.querySelectorAll("article.card img.thumb").forEach((img) => {
    let timer = null,
      idx = 0,
      original = img.getAttribute("src");
    const card = img.closest("article.card");
    const vid = card ? card.dataset.id : null;
    const syncAspect = () => {
      if (!img.naturalWidth || !img.naturalHeight || !vid) return;
      const ar = img.naturalWidth / img.naturalHeight;
      const prevAr = aspectMap[vid] || 0;
      aspectMap[vid] = ar;
      if (!isMobileLayout() && prevAr > 0 && Math.abs(prevAr - ar) > 0.08) {
        scheduleRelayout();
      }
    };
    if (img.complete) setTimeout(syncAspect, 0);
    else img.addEventListener("load", syncAspect, { once: true });
    const getVideo = () => {
      if (!card) return null;
      return videos.find((v) => v.id === card.dataset.id) || null;
    };
    const startPreview = () => {
      if (!ENABLE_PREVIEW_FRAMES) return;
      if (timer) return; // guard: avoid stacked intervals on repeated hover/click bindings
      const v = getVideo();
      if (!v || !v.preview_urls || v.preview_urls.length === 0) return;
      const frames = getPreviewFrameUrls(v);
      if (!frames.length) return;
      preloadPreviewFrames(frames);
      original = img.getAttribute("src");
      idx = 0;

      if (frames.length === 1) {
        const next = frames[0];
        if (img.dataset.previewSrc !== next) {
          img.src = next;
          img.dataset.previewSrc = next;
        }
        return;
      }

      timer = setInterval(() => {
        const next = frames[idx % frames.length];
        idx++;
        if (img.dataset.previewSrc !== next) {
          img.src = next;
          img.dataset.previewSrc = next;
        }
      }, 320);
    };
    const stopPreview = () => {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      if (img.getAttribute("src") !== original) img.src = original;
      delete img.dataset.previewSrc;
    };
    if (pointerCoarse) {
      img.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const c = img.closest("article.card");
        if (!c) return;
        const now = Date.now();
        const last = Number(c.dataset.lastTap || 0);
        const armed = c.dataset.tapArmed === "1";
        const previewActive = c.dataset.previewActive === "1";
        if (previewActive || (armed && now - last < 1800)) {
          const v = videos.find((x) => x.id === c.dataset.id);
          const sub = v && v.subtitle_url ? withBase(v.subtitle_url) : null;
          c.dataset.tapArmed = "0";
          c.dataset.lastTap = "0";
          c.dataset.previewActive = "0";
          stopPreview();
          currentVideoRecord = v || null;
          playVideoWithOverride(v, sub);
          return;
        }
        c.dataset.tapArmed = "1";
        c.dataset.lastTap = String(now);
        c.dataset.previewActive = "1";
        stopPreview();
        startPreview();
        // keep preview looping until user taps this card again to play
      });
    } else {
      if (pointerHover) {
        img.addEventListener("mouseenter", startPreview);
        img.addEventListener("mouseleave", stopPreview);
      }
      img.addEventListener("click", () => {
        const c = img.closest("article.card");
      if (c) {
        const v = videos.find((x) => x.id === c.dataset.id);
        const sub = v && v.subtitle_url ? withBase(v.subtitle_url) : null;
        currentVideoRecord = v || null;
        playVideoWithOverride(v, sub);
      }
    });
    }
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function cardHtml(v, w, h, opts = {}) {
  const { useFlex = false, flexFactor = 1 } = opts;
  const minCardWidth = mobileZoomLevel > 1 ? 90 : 120;
  const cw = Math.max(minCardWidth, Math.round(w));
  const safeName = escapeHtml(v.name);
  const safeFolder = escapeHtml(v.folder);
  const safeSize = escapeHtml(v.size);
  const style = useFlex
    ? `flex:${flexFactor} 0 0;height:${Math.round(h)}px;`
    : `width:${cw}px;`;
  return `<article class='card' style='${style}' data-rowh='${Math.round(h)}' data-id='${v.id}' data-url='${withBase(v.stream_url || v.video_url)}' data-name='${safeName}' data-subtitle='${v.subtitle_url || ""}'><img class='thumb' loading='lazy' src='${withBase(v.thumb_url)}' alt='${safeName}' style='height:${Math.round(h)}px'/><div class='meta'><div class='name' title='${safeName}' data-fullname='${safeName}'>${safeName}</div><div class='sub' title='${safeFolder} · ${safeSize}' data-fullname='${safeFolder} · ${safeSize}'>${safeFolder} · ${safeSize}</div><div class='actions'><button class='play-btn' type='button' aria-label='播放' title='播放'>▶</button></div></div></article>`;
}

function buildRows(items, { append = false, isFinal = false } = {}) {
  updateMobileCols();
  const mobile = isMobileLayout();
  const mobileZoomed = mobile && mobileZoomLevel > 1;
  grid.classList.toggle("mobile", mobile);
  grid.classList.toggle("zoomed", mobileZoomed);
  if (!append) {
    grid.innerHTML = "";
    pendingRow = [];
    pendingSumAr = 0;
  }
  if (!items.length) {
    if (!append) updateStat();
    return;
  }

  if (mobile && !mobileZoomed) {
    const wrap = document.createElement("div");
    wrap.className = "jrow";
    wrap.innerHTML = items
      .map((v) => {
        const safeName = escapeHtml(v.name);
        const safeFolder = escapeHtml(v.folder);
        const safeSize = escapeHtml(v.size);
        return `<article class='card' data-id='${v.id}' data-url='${withBase(v.stream_url || v.video_url)}' data-name='${safeName}' data-subtitle='${v.subtitle_url || ""}'><img class='thumb' loading='lazy' src='${withBase(v.thumb_url)}' alt='${safeName}'/><div class='meta'><div class='name' title='${safeName}' data-fullname='${safeName}'>${safeName}</div><div class='sub' title='${safeFolder} · ${safeSize}' data-fullname='${safeFolder} · ${safeSize}'>${safeFolder} · ${safeSize}</div><div class='actions'><button class='play-btn' type='button' aria-label='播放' title='播放'>▶</button></div></div></article>`;
      })
      .join("");
    bindCardEvents(wrap);
    while (wrap.firstChild) grid.appendChild(wrap.firstChild);
    updateStat();
    return;
  }

  const W = Math.max(
    320,
    Math.floor(
      (grid.getBoundingClientRect().width ||
        grid.clientWidth ||
        window.innerWidth) - 2,
    ),
  );
  const targetRowH = mobileZoomed ? ZOOMED_TARGET_ROW_H : TARGET_ROW_H;
  const minRowH = mobileZoomed ? ZOOMED_MIN_ROW_H : MIN_ROW_H;
  const maxRowH = mobileZoomed ? ZOOMED_MAX_ROW_H : MAX_ROW_H;
  const GAP = mobileZoomed ? 2 : 14;
  let row = append ? [...pendingRow] : [];
  let sumAr = append ? pendingSumAr : 0;
  const zoomRowLimit = mobileZoomed ? getMobileZoomRowLimit() : Infinity;
  let rowMaxCols = zoomRowLimit;

  const computeHeight = (count, arSum) =>
    (W - GAP * Math.max(0, count - 1)) / Math.max(0.0001, arSum);

  const flush = (isLast = false) => {
    if (!row.length) return;
    let h = targetRowH;
    const majorityLandscape =
      row.length && row.every((v) => getLayoutAr(v) > 1.2);
    const desktopLandscapeFill = !mobileZoomed && majorityLandscape && row.length >= 2;
    const localMinRowH = mobileZoomed && majorityLandscape
      ? ZOOMED_LANDSCAPE_MIN_ROW_H
      : minRowH;
    const localMaxRowH = mobileZoomed && majorityLandscape
      ? ZOOMED_LANDSCAPE_MAX_ROW_H
      : maxRowH;
    if (!isLast || mobileZoomed || desktopLandscapeFill) {
      h = computeHeight(row.length, sumAr);
      h = Math.max(localMinRowH, Math.min(localMaxRowH, h));
    }
    if (mobileZoomed && majorityLandscape) {
      const widthPerCard =
        (W - GAP * Math.max(0, row.length - 1)) / Math.max(1, row.length);
      const heightCap = Math.max(ZOOMED_LANDSCAPE_MIN_ROW_H, widthPerCard / 1.15);
      h = Math.min(h, heightCap, ZOOMED_LANDSCAPE_MAX_ROW_H);
    }
    const r = document.createElement("div");
    r.className = "jrow";
    const useFlex = mobileZoomed;
    r.innerHTML = row
      .map((v) => {
        const ar = getLayoutAr(v);
        return cardHtml(v, ar * h, h, {
          useFlex,
          flexFactor: ar,
        });
      })
      .join("");
    bindCardEvents(r);
    grid.appendChild(r);
    row = [];
    sumAr = 0;
    rowMaxCols = zoomRowLimit;
  };

  for (const v of items) {
    const ar = getLayoutAr(v);
    row.push(v);
    sumAr += ar;
    if (mobileZoomed) {
      if (row.length >= rowMaxCols) {
        flush(false);
      }
      continue;
    }
    const projected = sumAr * TARGET_ROW_H + GAP * (row.length - 1);
    if (projected >= W && row.length >= 2) flush(false);
  }

  if (isFinal) {
    flush(true);
    pendingRow = [];
    pendingSumAr = 0;
  } else {
    pendingRow = row;
    pendingSumAr = sumAr;
  }

  updateStat();
}

function refreshFilteredIndexMap() {
  filteredIndexMap = new Map(filteredVideos.map((v, i) => [v.id, i]));
}

function queueThumbPrefetch(url) {
  const u = String(url || "").trim();
  if (!u || preloadedThumbUrls.has(u) || queuedThumbUrls.has(u)) return;
  queuedThumbUrls.add(u);
  thumbPrefetchQueue.push(u);
}

function pumpThumbPrefetchQueue() {
  while (
    activeThumbPrefetches < MAX_THUMB_PREFETCH_CONCURRENCY &&
    thumbPrefetchQueue.length
  ) {
    const next = thumbPrefetchQueue.shift();
    if (!next) continue;
    queuedThumbUrls.delete(next);
    if (preloadedThumbUrls.has(next)) continue;
    preloadedThumbUrls.add(next);
    activeThumbPrefetches++;
    const im = new Image();
    im.decoding = "async";
    im.loading = "eager";
    const finish = () => {
      activeThumbPrefetches = Math.max(0, activeThumbPrefetches - 1);
      pumpThumbPrefetchQueue();
    };
    im.onload = finish;
    im.onerror = finish;
    im.src = next;
  }
}

function getRenderedRange() {
  const cards = grid.querySelectorAll("article.card[data-id]");
  if (!cards.length)
    return {
      start: 0,
      end: Math.max(0, Math.min(renderCount, filteredVideos.length) - 1),
    };
  const viewportTop = -window.innerHeight * 0.5;
  const viewportBottom = window.innerHeight * 1.5;
  let start = null;
  let end = null;
  for (const card of cards) {
    const rect = card.getBoundingClientRect();
    if (rect.bottom < viewportTop || rect.top > viewportBottom) continue;
    const idx = filteredIndexMap.get(card.dataset.id);
    if (idx === undefined) continue;
    if (start === null || idx < start) start = idx;
    if (end === null || idx > end) end = idx;
  }
  if (start === null || end === null) {
    const firstIdx = filteredIndexMap.get(cards[0]?.dataset.id) ?? 0;
    const lastIdx =
      filteredIndexMap.get(cards[cards.length - 1]?.dataset.id) ?? firstIdx;
    return { start: firstIdx, end: lastIdx };
  }
  return { start, end };
}

function scheduleThumbPrefetch() {
  if (thumbPrefetchTimer) clearTimeout(thumbPrefetchTimer);
  thumbPrefetchTimer = setTimeout(() => {
    thumbPrefetchTimer = null;
    if (!filteredVideos.length) return;
    const { start, end } = getRenderedRange();
    const movingFast = scrollVelocity > 1200;
    const ahead = movingFast
      ? FAST_THUMB_PREFETCH_AHEAD
      : BASE_THUMB_PREFETCH_AHEAD;
    const targetStart = Math.max(0, start - THUMB_PREFETCH_BEHIND);
    const targetEnd = Math.min(filteredVideos.length, end + ahead);
    for (let i = targetStart; i < targetEnd; i++) {
      const u = withBase(filteredVideos[i]?.thumb_url || "");
      queueThumbPrefetch(u);
    }
    pumpThumbPrefetchQueue();
  }, 60);
}

async function preloadAllPages(loadId = activeLoadId) {
  while (loadId === activeLoadId && !serverExhausted) {
    await fetchNextPage(loadId, { render: false });
  }
}

function renderChunk(reset = false, batchSize = RENDER_BATCH_SIZE) {
  if (loadingMore && !reset) return;
  loadingMore = true;
  let prevCount = renderCount;
  if (reset) {
    renderCount = 0;
    prevCount = 0;
  }
  const step = reset ? INITIAL_RENDER_COUNT : batchSize;
  renderCount = Math.min(filteredVideos.length, renderCount + step);
  const slice = filteredVideos.slice(prevCount, renderCount);
  const trulyFinal = renderCount >= filteredVideos.length && serverExhausted;
  buildRows(slice, { append: !reset, isFinal: trulyFinal });
  scheduleThumbPrefetch();
  loadingMore = false;
}

function nearBottom() {
  const y = window.scrollY || window.pageYOffset || 0;
  const docH = Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight,
  );
  return window.innerHeight + y >= docH - 260;
}

function nearMiddle() {
  const y = window.scrollY || window.pageYOffset || 0;
  const docH = Math.max(
    document.body.scrollHeight,
    document.documentElement.scrollHeight,
  );
  const maxScroll = Math.max(1, docH - window.innerHeight);
  return y >= maxScroll * 0.5;
}

async function ensurePrefetchAhead(loadId = activeLoadId) {
  if (PREFETCH_AHEAD_BATCH <= 0) return;
  if (loadId !== activeLoadId) return;
  if (serverExhausted) return;
  // Keep at least one API batch buffered ahead of rendered items.
  while (loadId === activeLoadId && !serverExhausted && !fetchingPage) {
    const ahead = Math.max(
      0,
      filteredVideos.length + prefetchBuffer.length - renderCount,
    );
    if (ahead >= PREFETCH_AHEAD_BATCH) break;
    await fetchNextPage(loadId, { render: false });
    if (fetchingPage) break;
  }
}

async function ensureAutoLoad() {
  if (loadingMore) return;
  const remainingLoaded = Math.max(0, filteredVideos.length - renderCount);
  const shouldAdvanceRender =
    remainingLoaded <= RENDER_NEXT_THRESHOLD || nearMiddle();
  if (shouldAdvanceRender && renderCount < filteredVideos.length) {
    renderChunk(false, RENDER_BATCH_SIZE);
  }
}

function render() {
  // Safety filter on client side too (prevents mixed batches during race/reload).
  const f = currentFolderFilter();
  const needle = (q?.value || "").trim().toLowerCase();
  filteredVideos = videos.filter((v) => {
    const okFolder = !f || String(v.folder || "") === f;
    const okName =
      !needle ||
      String(v.name || "")
        .toLowerCase()
        .includes(needle);
    return okFolder && okName;
  });
  refreshFilteredIndexMap();
  if (catalogStatus && catalogStatus.available === false) {
    notice.style.display = "block";
    notice.textContent = `Library not ready. Waiting for mounted disks: ${(catalogStatus.roots || []).join(", ")}`;
  } else {
    notice.style.display = "none";
    notice.textContent = "";
  }
  renderChunk(true);
}

function getSavedFolderSelection() {
  return localStorage.getItem("movies_folder") || "";
}

function saveFolderSelection(value) {
  localStorage.setItem("movies_folder", value || "");
}

function renderFolderOptions() {
  const source = folderListCache.length
    ? folderListCache
    : [...new Set(videos.map((v) => v.folder))].sort();
  const all = ["", ...source];
  const kw = (folderSearch?.value || "").trim().toLowerCase();
  const list = kw ? all.filter((f) => !f || f.toLowerCase().includes(kw)) : all;
  folderOptions.innerHTML = list
    .map((f) => {
      const label = f || "All folders";
      const active = folder.value === f ? " active" : "";
      return `<button type='button' class='folder-opt${active}' data-val='${escapeHtml(f)}'>${escapeHtml(label)}</button>`;
    })
    .join("");
  folderOptions.querySelectorAll(".folder-opt").forEach((b) => {
    b.addEventListener("click", () => {
      folder.value = b.dataset.val || "";
      saveFolderSelection(folder.value);
      folderBtn.textContent = folder.value || "All folders";
      folderPanel.style.display = "none";
      load();
    });
  });
}

function refreshFolders() {
  const selected = folder.value || getSavedFolderSelection();
  const set = folderListCache.length
    ? folderListCache
    : [...new Set(videos.map((v) => v.folder))].sort();
  folder.innerHTML =
    `<option value=''>All folders</option>` +
    set.map((f) => `<option value="${f}">${f}</option>`).join("");
  if (selected && set.includes(selected)) {
    folder.value = selected;
  } else {
    folder.value = "";
  }
  folderBtn.textContent = folder.value || "All folders";
  renderFolderOptions();
}
function videosApiPath() {
  return "videos";
}
function foldersApiPath() {
  return "folders";
}
function updatePrivateToggle() {
  const btn = document.getElementById("privateToggle");
  const enabled = !!(catalogStatus && catalogStatus.private_enabled);
  const authorized = !!(catalogStatus && catalogStatus.private_authorized);
  btn.disabled = !enabled;
  btn.style.opacity = enabled ? "1" : "0.5";
  // UI strictly follows server auth state to avoid stale local state.
  btn.classList.toggle("on", authorized);
  btn.title = authorized ? "Private Mode: On" : "Private Mode: Off";
}
function currentFolderFilter() {
  const live = (folder?.value || "").trim();
  if (live) return live;
  return (getSavedFolderSelection() || "").trim();
}

function buildVideosQuery(limit, offset) {
  const params = new URLSearchParams();
  params.set("limit", String(limit));
  params.set("offset", String(offset));
  const f = currentFolderFilter();
  const kw = (q?.value || "").trim();
  if (f) params.set("folder", f);
  if (kw) params.set("q", kw);
  return `${videosApiPath()}?${params.toString()}`;
}

async function fetchNextPage(loadId = activeLoadId, opts = {}) {
  const shouldRender = opts.render !== false;
  if (loadId !== activeLoadId) return;
  if (fetchingPage || serverExhausted) return;
  const reqOffset = serverOffset;
  fetchingPage = true;
  try {
    const headers = deviceHeaders();
    const rr = await fetch(
      apiUrl(buildVideosQuery(API_PAGE_SIZE, serverOffset)),
      { headers },
    );
    if (!rr.ok) return;
    const rj = await rr.json();
    if (loadId !== activeLoadId) return;
    const items = Array.isArray(rj?.items) ? rj.items : [];
    const total = Number(rj?.total || 0);
    serverTotal = total || serverTotal;
    if (!items.length) {
      serverExhausted = true;
      return;
    }
    const seen = new Set(videos.map((v) => v.id));
    const incoming = [];
    for (const it of items) {
      if (!it || !it.id || seen.has(it.id)) continue;
      seen.add(it.id);
      incoming.push(normalizeVideoRecord(it));
    }
    for (const it of incoming) videos.push(it);

    const respOffset = Number(rj?.offset ?? reqOffset);
    serverOffset = respOffset + items.length;
    if (serverOffset >= serverTotal || videos.length >= serverTotal)
      serverExhausted = true;
    filteredVideos = videos;
    if (shouldRender) {
      // Rebuild from all loaded items to avoid losing earlier pages in incremental append path.
      const keepScrollY = window.scrollY || window.pageYOffset || 0;
      renderCount = filteredVideos.length;
      refreshFilteredIndexMap();
      buildRows(filteredVideos, { append: false, isFinal: serverExhausted });
      requestAnimationFrame(() => {
        window.scrollTo(0, keepScrollY);
        scheduleThumbPrefetch();
      });
    } else {
      updateStat();
      scheduleThumbPrefetch();
    }
  } finally {
    fetchingPage = false;
  }
}

async function load(forceNetwork = false) {
  if (loadInFlight) return loadInFlight;
  loadInFlight = (async () => {
    activeLoadId += 1;
    const loadId = activeLoadId;
    const headers = deviceHeaders();
    await loadServerConfig();

    // Apply persisted folder filter immediately so first page query is consistent after refresh.
    const savedFolder = getSavedFolderSelection();
    if (savedFolder && folder) {
      try {
        folder.value = savedFolder;
        folderBtn.textContent = savedFolder;
      } catch (e) {}
    }
    if (!forceNetwork) {
      const cached = await loadSnapshotFromCache();
      if (cached && applyCachedSnapshot(cached)) {
        loadInFlight = null;
        return;
      }
    }

    const sr = await fetch(apiUrl("status"), { headers });
    catalogStatus = await sr.json();
    updateDebugPanel();
    if (catalogStatus && catalogStatus.private_authorized) setPrivateMode(true);
    updatePrivateToggle();

    try {
      const fr = await fetch(apiUrl(foldersApiPath()), { headers });
      if (fr.ok) {
        const fjson = await fr.json();
        folderListCache = Array.isArray(fjson?.folders) ? fjson.folders : [];
        suppressFolderChange = true;
        refreshFolders();
        suppressFolderChange = false;
      }
    } catch (e) {
      suppressFolderChange = false;
    }

    lastAppliedFolderValue = folder?.value || "";
    lastAppliedQueryValue = (q?.value || "").trim();

    videos = [];
    filteredVideos = videos;
    refreshFilteredIndexMap();
    prefetchBuffer = [];
    preloadedThumbUrls.clear();
    queuedThumbUrls.clear();
    thumbPrefetchQueue = [];
    activeThumbPrefetches = 0;
    renderCount = 0;
    serverTotal = 0;
    serverOffset = 0;
    serverExhausted = false;

    try {
      await fetchNextPage(loadId, { render: false });
      renderChunk(true);
      await ensurePrefetchAhead(loadId);
      // Eagerly load all remaining pages upfront; scrolling does render only.
      await preloadAllPages(loadId);
      await saveSnapshotToCache();
      uiReady = true;
    } finally {
      loadInFlight = null;
    }
  })();
  return loadInFlight;
}
const themeSel = document.getElementById("themeSel");
function applyTheme(v) {
  document.body.setAttribute("data-theme", v || "neo-dark");
}
themeSel.addEventListener("change", () => {
  localStorage.setItem("movies_theme", themeSel.value);
  applyTheme(themeSel.value);
});
const savedTheme = localStorage.getItem("movies_theme") || "neo-dark";
themeSel.value = savedTheme;
applyTheme(savedTheme);
let searchTimer = null;
q.addEventListener("input", () => {
  if (!uiReady) return;
  const next = (q?.value || "").trim();
  if (next === lastAppliedQueryValue) return;
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => load(), 220);
});
folder.addEventListener("change", () => {
  if (!uiReady) return;
  if (suppressFolderChange) return;
  const next = folder.value || "";
  if (next === lastAppliedFolderValue) return;
  saveFolderSelection(next);
  folderBtn.textContent = next || "All folders";
  renderFolderOptions();
  load();
});
folderBtn.addEventListener("click", (e) => {
  e.preventDefault();
  e.stopPropagation();
  const open = folderPanel.style.display !== "none";
  folderPanel.style.display = open ? "none" : "block";
  if (!open) {
    folderSearch.value = "";
    renderFolderOptions();
    // Avoid mobile keyboard popup: blur any focused input when opening panel.
    try {
      if (document.activeElement && document.activeElement.blur)
        document.activeElement.blur();
    } catch (err) {}
  }
});
folderSearch.addEventListener("input", renderFolderOptions);
const closeFolderPanelIfOutside = (e) => {
  const wrap = document.getElementById("folder");
  if (!wrap || !folderPanel || folderPanel.style.display === "none") return;
  if (!wrap.contains(e.target)) folderPanel.style.display = "none";
};
// Use pointer/touch capture so mobile taps outside close the panel immediately.
document.addEventListener("pointerdown", closeFolderPanelIfOutside, true);
document.addEventListener("touchstart", closeFolderPanelIfOutside, true);
document.addEventListener("click", closeFolderPanelIfOutside, true);
window.addEventListener("scroll", () => {
  const y = window.scrollY || window.pageYOffset || 0;
  const goingDown = y >= lastScrollY;
  const now = performance.now();
  if (lastScrollSampleAt) {
    const dt = Math.max(1, now - lastScrollSampleAt);
    scrollVelocity = Math.abs(((y - lastScrollSampleY) * 1000) / dt);
  }
  lastScrollSampleY = y;
  lastScrollSampleAt = now;
  lastScrollY = y;
  if (toTopBtn) toTopBtn.classList.toggle("show", y > 260);
  if (!goingDown) return;
  ensureAutoLoad();
  scheduleThumbPrefetch();
});
if (toTopBtn) {
  toTopBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}
let lastResizeW = window.innerWidth;
let resizeTimer = null;
const relayoutNow = () => {
  buildRows(filteredVideos.slice(0, renderCount), {
    append: false,
    isFinal: renderCount >= filteredVideos.length,
  });
  queueMicrotask(ensureAutoLoad);
};
window.addEventListener("resize", () => {
  const coarse = window.matchMedia("(pointer: coarse)").matches;
  if (isIPadClient() && mobileZoomLevel <= 1) {
    updateMobileCols();
    relayoutModalBox();
    return;
  }
  const landscape = window.matchMedia("(orientation: landscape)").matches;
  const w = window.innerWidth;
  const widthDelta = Math.abs(w - lastResizeW);
  lastResizeW = w;
  const threshold = coarse && landscape ? 120 : 48;
  if (coarse && widthDelta < threshold) {
    updateMobileCols();
    setTimeout(relayoutModalBox, 80);
    return;
  }
  if (resizeTimer) clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    relayoutNow();
    relayoutModalBox();
  }, 140);
});
window.addEventListener("orientationchange", () => {
  if (isIPadClient() && mobileZoomLevel <= 1) {
    updateMobileCols();
    relayoutModalBox();
    return;
  }
  const prevCols = currentMobileCols;
  const nextCols = updateMobileCols();
  if (prevCols !== nextCols) {
    setTimeout(relayoutNow, 90);
    setTimeout(relayoutNow, 320);
  } else {
    setTimeout(updateMobileCols, 120);
  }
  setTimeout(relayoutModalBox, 120);
  setTimeout(relayoutModalBox, 360);
});
if (window.visualViewport && window.visualViewport.addEventListener) {
  window.visualViewport.addEventListener("resize", () => {
    const coarse = window.matchMedia("(pointer: coarse)").matches;
    if (!coarse) return;
    if (isIPadClient() && mobileZoomLevel <= 1) {
      updateMobileCols();
      return;
    }
    const prevCols = currentMobileCols;
    const nextCols = updateMobileCols();
    if (prevCols !== nextCols) {
      if (resizeTimer) clearTimeout(resizeTimer);
      resizeTimer = setTimeout(relayoutNow, 140);
    }
  });
}
if ("IntersectionObserver" in window && scrollSentinel) {
  const io = new IntersectionObserver(
    (entries) => {
      for (const ent of entries) {
        if (ent.isIntersecting) {
          ensureAutoLoad();
        }
      }
    },
    { root: null, rootMargin: "360px 0px", threshold: 0.01 },
  );
  io.observe(scrollSentinel);
}
document.getElementById("rescan").addEventListener("click", async () => {
  await fetch(withBase("rescan"), { headers: deviceHeaders() });
  await cacheClearAll().catch(() => {});
  setTimeout(() => load(true), 800);
});
document.getElementById("privateToggle").addEventListener("click", async () => {
  const authorized = !!(catalogStatus && catalogStatus.private_authorized);
  if (authorized) {
    // Optimistic lock UX: reflect locked state immediately.
    setPrivateMode(false);
    privatePasscode = "";
    // Reset folder selection to avoid stuck private folder after lock.
    saveFolderSelection("");
    if (folder) folder.value = "";
    if (folderBtn) folderBtn.textContent = "All folders";
    if (catalogStatus) catalogStatus.private_authorized = false;
    updatePrivateToggle();
    try {
      await fetch(apiUrl("private/lock"), {
        method: "POST",
        headers: deviceHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify({}),
      });
    } catch (e) {}
    await cacheClearAll().catch(() => {});
    await load(true);
    return;
  }
  openPassModal();
});

// Force-disable zoom on all devices/browsers when configured
let lastTouchEnd = 0;
const PREVENT_NATIVE_PINCH = true;

if (PREVENT_NATIVE_PINCH) {
  document.addEventListener("gesturestart", (e) => e.preventDefault(), {
    passive: false,
  });
  document.addEventListener("gesturechange", (e) => e.preventDefault(), {
    passive: false,
  });
  document.addEventListener("gestureend", (e) => e.preventDefault(), {
    passive: false,
  });
  document.addEventListener(
    "touchstart",
    (e) => {
      if (e.touches && e.touches.length > 1) e.preventDefault();
    },
    { passive: false },
  );
  document.addEventListener(
    "touchend",
    (e) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 320) e.preventDefault();
      lastTouchEnd = now;
    },
    { passive: false },
  );
}

window.addEventListener(
  "wheel",
  (e) => {
    if (e.ctrlKey) e.preventDefault();
  },
  { passive: false },
);
window.addEventListener(
  "keydown",
  (e) => {
    if ((e.ctrlKey || e.metaKey) && ["+", "=", "-", "0"].includes(e.key))
      e.preventDefault();
  },
  { passive: false },
);

document.addEventListener("touchstart", handlePinchStart, { passive: false });
document.addEventListener("touchmove", handlePinchMove, { passive: false });
document.addEventListener("touchend", handlePinchEnd);
document.addEventListener("touchcancel", handlePinchEnd);

if (!window.__mirandaMoviesBooted) {
  window.__mirandaMoviesBooted = true;
  updatePrivateToggle();
  load();
}
