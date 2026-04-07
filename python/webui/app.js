const fileCleaningState = {
  candidates: [],
  installers: [],
  downloads: [],
  largeFiles: [],
  candidateSelectedPaths: new Set(),
  installerSelectedPaths: new Set(),
  downloadSelectedPaths: new Set(),
  largeSelectedPaths: new Set(),
  currentView: null,
  currentPath: null,
  selectionAnchors: {
    candidate: null,
    installer: null,
    download: null,
    large: null,
  },
};

const appCacheState = {
  categories: [],
  files: [],
  selectedPaths: new Set(),
  currentPath: null,
  expandedGroups: new Set(),
  groupScrollTop: new Map(),
  selectionAnchor: null,
};

const startupState = {
  items: [],
  selectedIds: new Set(),
  currentId: null,
  expandedGroups: new Set(),
  groupScrollTop: new Map(),
  selectionAnchor: null,
};

const memoryState = {
  items: [],
  selectedIds: new Set(),
  currentId: null,
  selectionAnchor: null,
};

const imageState = {
  screenshots: [],
  downloads: [],
  similar: [],
  duplicates: [],
  largeOld: [],
  screenshotSelectedPaths: new Set(),
  downloadSelectedPaths: new Set(),
  similarSelectedPaths: new Set(),
  duplicateSelectedPaths: new Set(),
  largeOldSelectedPaths: new Set(),
  currentView: null,
  currentPath: null,
  selectionAnchors: {
    screenshots: null,
    downloads: null,
    similar: null,
    duplicates: null,
    largeOld: null,
  },
};

const diskState = {
  roots: [],
  largeFiles: [],
  selectedPaths: new Set(),
  currentPath: null,
  expandedGroups: new Set(),
  groupScrollTop: new Map(),
  selectionAnchor: null,
};

const applicationState = {
  items: [],
  selectedPaths: new Set(),
  currentPath: null,
  expandedGroups: new Set(),
  groupScrollTop: new Map(),
  selectionAnchor: null,
};

const overviewState = {
  cards: [],
  selectedIds: new Set(),
  selectionAnchors: {},
};

const dragSelectionState = {
  active: false,
  scope: null,
  targetChecked: false,
};

const versionLine = document.getElementById("versionLine");
const routeLine = document.getElementById("routeLine");
const heroTitle = document.getElementById("heroTitle");
const overviewTab = document.getElementById("overviewTab");
const fileCleaningTab = document.getElementById("fileCleaningTab");
const appCachesTab = document.getElementById("appCachesTab");
const startupTab = document.getElementById("startupTab");
const memoryTab = document.getElementById("memoryTab");
const imagesTab = document.getElementById("imagesTab");
const spaceTab = document.getElementById("spaceTab");
const applicationsTab = document.getElementById("applicationsTab");
const fileCleaningView = document.getElementById("fileCleaningView");
const appCacheView = document.getElementById("appCacheView");
const startupView = document.getElementById("startupView");
const memoryView = document.getElementById("memoryView");
const imagesView = document.getElementById("imagesView");
const spaceView = document.getElementById("spaceView");
const applicationsView = document.getElementById("applicationsView");
const overviewView = document.getElementById("overviewView");

const scanOverviewBtn = document.getElementById("scanOverviewBtn");
const clearOverviewSelectionBtn = document.getElementById("clearOverviewSelectionBtn");
const executeOverviewBtn = document.getElementById("executeOverviewBtn");
const overviewSummary = document.getElementById("overviewSummary");
const overviewSelectionSummary = document.getElementById("overviewSelectionSummary");
const overviewStatus = document.getElementById("overviewStatus");
const overviewGrid = document.getElementById("overviewGrid");
const overviewResultBox = document.getElementById("overviewResultBox");

const summary = document.getElementById("summary");
const statusLine = document.getElementById("status");
const candidateSummary = document.getElementById("candidateSummary");
const installerSummary = document.getElementById("installerSummary");
const downloadSummary = document.getElementById("downloadSummary");
const largeFilesSummary = document.getElementById("largeFilesSummary");
const candidateTableBody = document.getElementById("candidateTableBody");
const installerTableBody = document.getElementById("installerTableBody");
const downloadTableBody = document.getElementById("downloadTableBody");
const largeFilesTableBody = document.getElementById("largeFilesTableBody");
const detailBox = document.getElementById("detailBox");
const resultBox = document.getElementById("resultBox");
const revealFileBtn = document.getElementById("revealFileBtn");
const openFileBtn = document.getElementById("openFileBtn");

const scanBtn = document.getElementById("scanBtn");
const executeCategoryBtn = document.getElementById("executeCategoryBtn");
const selectAllCandidatesBtn = document.getElementById("selectAllCandidatesBtn");
const clearCandidateSelectionBtn = document.getElementById("clearCandidateSelectionBtn");
const deleteCandidateBtn = document.getElementById("deleteCandidateBtn");
const selectAllInstallersBtn = document.getElementById("selectAllInstallersBtn");
const clearInstallerSelectionBtn = document.getElementById("clearInstallerSelectionBtn");
const deleteInstallerBtn = document.getElementById("deleteInstallerBtn");
const selectAllDownloadsBtn = document.getElementById("selectAllDownloadsBtn");
const clearDownloadSelectionBtn = document.getElementById("clearDownloadSelectionBtn");
const deleteDownloadBtn = document.getElementById("deleteDownloadBtn");
const selectAllLargeBtn = document.getElementById("selectAllLargeBtn");
const clearLargeSelectionBtn = document.getElementById("clearLargeSelectionBtn");
const deleteLargeBtn = document.getElementById("deleteLargeBtn");

const appCacheSummary = document.getElementById("appCacheSummary");
const appCacheStatus = document.getElementById("appCacheStatus");
const appCacheFilesSummary = document.getElementById("appCacheFilesSummary");
const appCacheGroups = document.getElementById("appCacheGroups");
const appCacheDetailBox = document.getElementById("appCacheDetailBox");
const appCacheResultBox = document.getElementById("appCacheResultBox");
const revealAppCacheBtn = document.getElementById("revealAppCacheBtn");
const openAppCacheBtn = document.getElementById("openAppCacheBtn");

const scanAppCachesBtn = document.getElementById("scanAppCachesBtn");
const executeAppCategoriesBtn = document.getElementById("executeAppCategoriesBtn");
const selectAllAppCacheBtn = document.getElementById("selectAllAppCacheBtn");
const clearAppCacheSelectionBtn = document.getElementById("clearAppCacheSelectionBtn");
const deleteAppCacheBtn = document.getElementById("deleteAppCacheBtn");

const startupSummary = document.getElementById("startupSummary");
const startupStatus = document.getElementById("startupStatus");
const startupItemsSummary = document.getElementById("startupItemsSummary");
const startupGroups = document.getElementById("startupGroups");
const startupDetailBox = document.getElementById("startupDetailBox");
const startupResultBox = document.getElementById("startupResultBox");
const openStartupBtn = document.getElementById("openStartupBtn");
const revealStartupBtn = document.getElementById("revealStartupBtn");
const scanStartupBtn = document.getElementById("scanStartupBtn");
const disableStartupBtn = document.getElementById("disableStartupBtn");
const selectAllStartupBtn = document.getElementById("selectAllStartupBtn");
const clearStartupSelectionBtn = document.getElementById("clearStartupSelectionBtn");

const memorySummary = document.getElementById("memorySummary");
const memoryStatus = document.getElementById("memoryStatus");
const memoryItemsSummary = document.getElementById("memoryItemsSummary");
const memoryTableBody = document.getElementById("memoryTableBody");
const memoryDetailBox = document.getElementById("memoryDetailBox");
const memoryResultBox = document.getElementById("memoryResultBox");
const openMemoryBtn = document.getElementById("openMemoryBtn");
const revealMemoryBtn = document.getElementById("revealMemoryBtn");
const scanMemoryBtn = document.getElementById("scanMemoryBtn");
const terminateMemoryBtn = document.getElementById("terminateMemoryBtn");
const selectAllMemoryBtn = document.getElementById("selectAllMemoryBtn");
const clearMemorySelectionBtn = document.getElementById("clearMemorySelectionBtn");

const imageSummary = document.getElementById("imageSummary");
const imageStatus = document.getElementById("imageStatus");
const screenshotSummary = document.getElementById("screenshotSummary");
const downloadedImageSummary = document.getElementById("downloadedImageSummary");
const similarImageSummary = document.getElementById("similarImageSummary");
const duplicateImageSummary = document.getElementById("duplicateImageSummary");
const largeOldImageSummary = document.getElementById("largeOldImageSummary");
const screenshotTableBody = document.getElementById("screenshotTableBody");
const downloadedImagesTableBody = document.getElementById("downloadedImagesTableBody");
const similarImagesTableBody = document.getElementById("similarImagesTableBody");
const duplicateImagesTableBody = document.getElementById("duplicateImagesTableBody");
const largeOldImagesTableBody = document.getElementById("largeOldImagesTableBody");
const imagePreview = document.getElementById("imagePreview");
const imagePreviewEmpty = document.getElementById("imagePreviewEmpty");
const imageDetailBox = document.getElementById("imageDetailBox");
const imageResultBox = document.getElementById("imageResultBox");
const openImageBtn = document.getElementById("openImageBtn");
const revealImageBtn = document.getElementById("revealImageBtn");
const scanImagesBtn = document.getElementById("scanImagesBtn");
const selectAllScreenshotsBtn = document.getElementById("selectAllScreenshotsBtn");
const clearScreenshotSelectionBtn = document.getElementById("clearScreenshotSelectionBtn");
const deleteScreenshotsBtn = document.getElementById("deleteScreenshotsBtn");
const selectAllDownloadedImagesBtn = document.getElementById("selectAllDownloadedImagesBtn");
const clearDownloadedImageSelectionBtn = document.getElementById("clearDownloadedImageSelectionBtn");
const deleteDownloadedImagesBtn = document.getElementById("deleteDownloadedImagesBtn");
const selectAllSimilarImagesBtn = document.getElementById("selectAllSimilarImagesBtn");
const clearSimilarImageSelectionBtn = document.getElementById("clearSimilarImageSelectionBtn");
const deleteSimilarImagesBtn = document.getElementById("deleteSimilarImagesBtn");
const selectAllDuplicateImagesBtn = document.getElementById("selectAllDuplicateImagesBtn");
const clearDuplicateImageSelectionBtn = document.getElementById("clearDuplicateImageSelectionBtn");
const deleteDuplicateImagesBtn = document.getElementById("deleteDuplicateImagesBtn");
const selectAllLargeOldImagesBtn = document.getElementById("selectAllLargeOldImagesBtn");
const clearLargeOldImageSelectionBtn = document.getElementById("clearLargeOldImageSelectionBtn");
const deleteLargeOldImagesBtn = document.getElementById("deleteLargeOldImagesBtn");

const diskSummary = document.getElementById("diskSummary");
const diskStatus = document.getElementById("diskStatus");
const diskRootsSummary = document.getElementById("diskRootsSummary");
const diskLargeFilesSummary = document.getElementById("diskLargeFilesSummary");
const diskRootsGroups = document.getElementById("diskRootsGroups");
const diskLargeFilesTableBody = document.getElementById("diskLargeFilesTableBody");
const diskDetailBox = document.getElementById("diskDetailBox");
const diskResultBox = document.getElementById("diskResultBox");
const openDiskBtn = document.getElementById("openDiskBtn");
const revealDiskBtn = document.getElementById("revealDiskBtn");
const scanDiskBtn = document.getElementById("scanDiskBtn");
const selectAllDiskLargeFilesBtn = document.getElementById("selectAllDiskLargeFilesBtn");
const clearDiskLargeFilesSelectionBtn = document.getElementById("clearDiskLargeFilesSelectionBtn");
const deleteDiskLargeFilesBtn = document.getElementById("deleteDiskLargeFilesBtn");

const applicationSummary = document.getElementById("applicationSummary");
const applicationStatus = document.getElementById("applicationStatus");
const applicationItemsSummary = document.getElementById("applicationItemsSummary");
const applicationGroups = document.getElementById("applicationGroups");
const applicationDetailBox = document.getElementById("applicationDetailBox");
const applicationResultBox = document.getElementById("applicationResultBox");
const openApplicationBtn = document.getElementById("openApplicationBtn");
const revealApplicationBtn = document.getElementById("revealApplicationBtn");
const scanApplicationsBtn = document.getElementById("scanApplicationsBtn");
const deleteApplicationsBtn = document.getElementById("deleteApplicationsBtn");
const selectAllApplicationsBtn = document.getElementById("selectAllApplicationsBtn");
const clearApplicationSelectionBtn = document.getElementById("clearApplicationSelectionBtn");

const routes = {
  overview: {
    hash: "#/overview",
    title: "全面检查",
    pageTitle: "macOS Cleaner | 全面检查",
    routeLine: "当前页面：全面检查",
  },
  file: {
    hash: "#/files",
    title: "文件清理",
    pageTitle: "macOS Cleaner | 文件清理",
    routeLine: "当前页面：文件清理",
  },
  app: {
    hash: "#/caches",
    title: "软件缓存",
    pageTitle: "macOS Cleaner | 软件缓存",
    routeLine: "当前页面：软件缓存",
  },
  startup: {
    hash: "#/startup",
    title: "开机启动",
    pageTitle: "macOS Cleaner | 开机启动",
    routeLine: "当前页面：开机启动",
  },
  memory: {
    hash: "#/memory",
    title: "内存管理",
    pageTitle: "macOS Cleaner | 内存管理",
    routeLine: "当前页面：内存管理",
  },
  images: {
    hash: "#/images",
    title: "图片管理",
    pageTitle: "macOS Cleaner | 图片管理",
    routeLine: "当前页面：图片管理",
  },
  space: {
    hash: "#/space",
    title: "磁盘空间",
    pageTitle: "macOS Cleaner | 磁盘空间",
    routeLine: "当前页面：磁盘空间",
  },
  applications: {
    hash: "#/applications",
    title: "应用程序",
    pageTitle: "macOS Cleaner | 应用程序",
    routeLine: "当前页面：应用程序",
  },
};

function formatBytes(value) {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = Number(value || 0);
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx += 1;
  }
  return `${size.toFixed(2)} ${units[idx]}`;
}

function formatAge(ageDays) {
  if (ageDays == null || ageDays < 0) return "最近使用时间未知";
  return `${ageDays} 天未修改`;
}

function localizedFindingName(key, fallback) {
  if (key === "duplicate_files") return "重复文件";
  if (key === "stale_large_files") return "长期未使用的大文件";
  if (key === "installer_files") return "安装文件";
  if (key === "download_files") return "下载文件";
  if (key === "largest_files_top10") return "大型文件";
  return fallback || key;
}

function selectedCategories(selector) {
  return [...document.querySelectorAll(selector)].map((el) => el.value);
}

function selectedFileCleaningCategories() {
  return selectedCategories("#fileCleaningView .checkboxes input:checked");
}

function selectedAppCacheCategories() {
  return selectedCategories("#appCacheView .checkboxes input:checked");
}

function selectedStartupGroups() {
  return selectedCategories("#startupView .checkboxes input:checked");
}

function selectedImageRoots() {
  return selectedCategories("#imagesView .checkboxes input:checked");
}

function selectedDiskRoots() {
  return selectedCategories("#spaceView .checkboxes input:checked");
}

function applyRangeSelection(items, selectedSet, anchorKey, targetKey, shouldSelect, keyFn) {
  const getKey = keyFn || ((item) => item.path);
  const startIndex = items.findIndex((item) => getKey(item) === anchorKey);
  const endIndex = items.findIndex((item) => getKey(item) === targetKey);
  if (startIndex < 0 || endIndex < 0) return;
  const [from, to] = startIndex <= endIndex ? [startIndex, endIndex] : [endIndex, startIndex];
  for (let index = from; index <= to; index += 1) {
    const key = getKey(items[index]);
    if (shouldSelect) selectedSet.add(key);
    else selectedSet.delete(key);
  }
}

function stopDragSelection() {
  if (!dragSelectionState.active) return;
  dragSelectionState.active = false;
  dragSelectionState.scope = null;
  dragSelectionState.targetChecked = false;
  document.body.classList.remove("drag-selecting");
}

function beginDragSelection(event, scope, selectedSet, key, anchorKey, setAnchor, items, applyChecked, keyFn) {
  if (event.button !== 0) return false;
  event.preventDefault();
  event.stopPropagation();
  const targetChecked = !selectedSet.has(key);
  if (event.shiftKey && anchorKey) {
    applyRangeSelection(items, selectedSet, anchorKey, key, targetChecked, keyFn);
    setAnchor(key);
    stopDragSelection();
    return false;
  }
  dragSelectionState.active = true;
  dragSelectionState.scope = scope;
  dragSelectionState.targetChecked = targetChecked;
  document.body.classList.add("drag-selecting");
  applyChecked(targetChecked);
  setAnchor(key);
  return true;
}

function continueDragSelection(scope, applyChecked) {
  if (!dragSelectionState.active || dragSelectionState.scope !== scope) return;
  applyChecked(dragSelectionState.targetChecked);
}

function setActiveTab(view) {
  const overviewActive = view === "overview";
  const route = routes[view] || routes.file;
  const fileActive = view === "file";
  const appActive = view === "app";
  const startupActive = view === "startup";
  const memoryActive = view === "memory";
  const imagesActive = view === "images";
  const spaceActive = view === "space";
  const applicationsActive = view === "applications";
  overviewView.classList.toggle("hidden", !overviewActive);
  fileCleaningView.classList.toggle("hidden", !fileActive);
  appCacheView.classList.toggle("hidden", !appActive);
  startupView.classList.toggle("hidden", !startupActive);
  memoryView.classList.toggle("hidden", !memoryActive);
  imagesView.classList.toggle("hidden", !imagesActive);
  spaceView.classList.toggle("hidden", !spaceActive);
  applicationsView.classList.toggle("hidden", !applicationsActive);
  overviewTab.classList.toggle("tab-active", overviewActive);
  overviewTab.classList.toggle("primary", overviewActive);
  fileCleaningTab.classList.toggle("tab-active", fileActive);
  fileCleaningTab.classList.toggle("primary", fileActive);
  appCachesTab.classList.toggle("tab-active", appActive);
  appCachesTab.classList.toggle("primary", appActive);
  startupTab.classList.toggle("tab-active", startupActive);
  startupTab.classList.toggle("primary", startupActive);
  memoryTab.classList.toggle("tab-active", memoryActive);
  memoryTab.classList.toggle("primary", memoryActive);
  imagesTab.classList.toggle("tab-active", imagesActive);
  imagesTab.classList.toggle("primary", imagesActive);
  spaceTab.classList.toggle("tab-active", spaceActive);
  spaceTab.classList.toggle("primary", spaceActive);
  applicationsTab.classList.toggle("tab-active", applicationsActive);
  applicationsTab.classList.toggle("primary", applicationsActive);
  heroTitle.textContent = route.title;
  routeLine.textContent = route.routeLine;
  document.title = route.pageTitle;
  window.scrollTo({ top: 0, behavior: "auto" });
}

function setFileBusy(busy, text) {
  statusLine.textContent = `状态：${text}`;
  [
    scanBtn,
    executeCategoryBtn,
    selectAllCandidatesBtn,
    clearCandidateSelectionBtn,
    deleteCandidateBtn,
    selectAllInstallersBtn,
    clearInstallerSelectionBtn,
    deleteInstallerBtn,
    selectAllDownloadsBtn,
    clearDownloadSelectionBtn,
    deleteDownloadBtn,
    selectAllLargeBtn,
    clearLargeSelectionBtn,
    deleteLargeBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealFileBtn.disabled = true;
    openFileBtn.disabled = true;
    return;
  }
  revealFileBtn.disabled = !getCurrentFileCleaningItem();
  openFileBtn.disabled = !getCurrentFileCleaningItem() || !canTryOpen(getCurrentFileCleaningItem());
}

function setAppCacheBusy(busy, text) {
  appCacheStatus.textContent = `状态：${text}`;
  [
    scanAppCachesBtn,
    executeAppCategoriesBtn,
    selectAllAppCacheBtn,
    clearAppCacheSelectionBtn,
    deleteAppCacheBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealAppCacheBtn.disabled = true;
    openAppCacheBtn.disabled = true;
    return;
  }
  revealAppCacheBtn.disabled = !getCurrentAppCacheItem();
  openAppCacheBtn.disabled = !getCurrentAppCacheItem() || !canTryOpen(getCurrentAppCacheItem());
}

function setStartupBusy(busy, text) {
  startupStatus.textContent = `状态：${text}`;
  [
    scanStartupBtn,
    disableStartupBtn,
    selectAllStartupBtn,
    clearStartupSelectionBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealStartupBtn.disabled = true;
    openStartupBtn.disabled = true;
    return;
  }
  revealStartupBtn.disabled = !getCurrentStartupItem() || !getCurrentStartupItem().action_path;
  openStartupBtn.disabled = !getCurrentStartupItem() || !getCurrentStartupItem().action_path;
}

function setApplicationBusy(busy, text) {
  applicationStatus.textContent = `状态：${text}`;
  [
    scanApplicationsBtn,
    deleteApplicationsBtn,
    selectAllApplicationsBtn,
    clearApplicationSelectionBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealApplicationBtn.disabled = true;
    openApplicationBtn.disabled = true;
    return;
  }
  revealApplicationBtn.disabled = !getCurrentApplicationItem();
  openApplicationBtn.disabled = !getCurrentApplicationItem();
}

function setMemoryBusy(busy, text) {
  memoryStatus.textContent = `状态：${text}`;
  [
    scanMemoryBtn,
    terminateMemoryBtn,
    selectAllMemoryBtn,
    clearMemorySelectionBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealMemoryBtn.disabled = true;
    openMemoryBtn.disabled = true;
    return;
  }
  const current = getCurrentMemoryItem();
  revealMemoryBtn.disabled = !current || !current.app_path;
  openMemoryBtn.disabled = !current || !current.app_path;
}

function setOverviewBusy(busy, text) {
  overviewStatus.textContent = `状态：${text}`;
  scanOverviewBtn.disabled = busy;
  clearOverviewSelectionBtn.disabled = busy;
  executeOverviewBtn.disabled = busy;
}

function setImageBusy(busy, text) {
  imageStatus.textContent = `状态：${text}`;
  [
    scanImagesBtn,
    selectAllScreenshotsBtn,
    clearScreenshotSelectionBtn,
    deleteScreenshotsBtn,
    selectAllDownloadedImagesBtn,
    clearDownloadedImageSelectionBtn,
    deleteDownloadedImagesBtn,
    selectAllSimilarImagesBtn,
    clearSimilarImageSelectionBtn,
    deleteSimilarImagesBtn,
    selectAllDuplicateImagesBtn,
    clearDuplicateImageSelectionBtn,
    deleteDuplicateImagesBtn,
    selectAllLargeOldImagesBtn,
    clearLargeOldImageSelectionBtn,
    deleteLargeOldImagesBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealImageBtn.disabled = true;
    openImageBtn.disabled = true;
    return;
  }
  const current = getCurrentImageItem();
  revealImageBtn.disabled = !current;
  openImageBtn.disabled = !current;
}

function setDiskBusy(busy, text) {
  diskStatus.textContent = `状态：${text}`;
  [
    scanDiskBtn,
    selectAllDiskLargeFilesBtn,
    clearDiskLargeFilesSelectionBtn,
    deleteDiskLargeFilesBtn,
  ].forEach((btn) => {
    btn.disabled = busy;
  });
  if (busy) {
    revealDiskBtn.disabled = true;
    openDiskBtn.disabled = true;
    return;
  }
  const current = getCurrentDiskItem();
  revealDiskBtn.disabled = !current;
  openDiskBtn.disabled = !current;
}

function viewForHash(hash) {
  const normalized = hash || routes.overview.hash;
  if (normalized === routes.overview.hash) return "overview";
  if (normalized === routes.app.hash) return "app";
  if (normalized === routes.startup.hash) return "startup";
  if (normalized === routes.memory.hash) return "memory";
  if (normalized === routes.images.hash) return "images";
  if (normalized === routes.space.hash) return "space";
  if (normalized === routes.applications.hash) return "applications";
  return "file";
}

function goToRoute(view) {
  const route = routes[view] || routes.file;
  if (window.location.hash !== route.hash) {
    window.location.hash = route.hash;
    return;
  }
  setActiveTab(view);
}

function syncRoute() {
  const hash = window.location.hash || routes.overview.hash;
  const view = viewForHash(hash);
  const route = routes[view];
  if (window.location.hash !== route.hash) {
    window.location.replace(route.hash);
    return;
  }
  setActiveTab(view);
}

async function api(path, payload = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

function pathExtension(path) {
  const name = path.split("/").pop() || "";
  const idx = name.lastIndexOf(".");
  return idx >= 0 ? name.slice(idx + 1).toLowerCase() : "";
}

function classifyReadableType(item) {
  const ext = pathExtension(item.path || "");
  if (["jpg", "jpeg", "png", "gif", "webp", "heic"].includes(ext)) return "图片文件";
  if (["mp4", "mov", "webm", "mkv"].includes(ext)) return "视频文件";
  if (["mp3", "aac", "m4a", "flac", "ogg", "wav"].includes(ext)) return "音频文件";
  if (["zip", "rar", "7z", "tar", "gz"].includes(ext)) return "压缩包";
  if (["dmg", "pkg"].includes(ext)) return "安装包";
  if (["pdf"].includes(ext)) return "文档文件";
  if (["js", "css", "html", "wasm"].includes(ext)) return "网页资源文件";
  const raw = (item.path || "").toLowerCase();
  if (raw.includes("/cache/") || raw.includes("/cache_data/")) return "缓存文件";
  return item.note || "普通文件";
}

function buildLocationTag(item) {
  const raw = (item.path || "").toLowerCase();
  if (raw.includes("/downloads/")) return "下载目录";
  if (raw.includes("/desktop/")) return "桌面目录";
  if (raw.includes("/documents/")) return "文稿目录";
  if (raw.includes("/online_play_cache/")) return "在线音乐缓存目录";
  if (raw.includes("/cache_data/")) return "网页资源缓存目录";
  if (raw.includes("/code cache/")) return "脚本代码缓存目录";
  if (raw.includes("/business/emoticon/thumb")) return "表情缩略图目录";
  if (raw.includes("/business/emoticon/temp")) return "表情临时目录";
  if (raw.includes("/business/favorite/thumb")) return "收藏缩略图目录";
  if (raw.includes("/business/favorite/mid")) return "收藏中间图目录";
  if (raw.includes("/msg/attach/")) return "聊天附件目录";
  if (raw.includes("/msg/video/")) return "聊天视频目录";
  if (raw.includes("/msg/file/")) return "聊天文件目录";
  if (raw.includes("/xwechat_files/") && raw.includes("/cache/")) return "微信媒体缓存目录";
  if (raw.includes("/xwechat_files/") && raw.includes("/temp/")) return "微信临时目录";
  if (raw.includes("/app_data/radium/web/profiles/")) return "微信网页内核目录";
  if (raw.includes("/applet/icon/")) return "小程序图标目录";
  if (raw.includes("/wmpfcache/")) return "小程序缓存目录";
  if (raw.includes("/cdncomm/cdn/download/")) return "CDN 下载缓存目录";
  if (raw.includes("/video/") && raw.includes("/thumbtemp/")) return "视频临时缩略图目录";
  if (raw.includes("/video/") && raw.includes("/thumb/")) return "视频缩略图目录";
  if (raw.includes("/file/") && raw.includes("/thumb")) return "文件缩略图目录";
  if (raw.includes("/dynamic_package/")) return "QQ 动态资源目录";
  if (raw.includes("/emoji/emoji-recv/") && raw.includes("/thumb")) return "表情缩略图目录";
  if (raw.includes("/emoji/emoji-recv/") && raw.includes("/oritemp")) return "表情原图临时目录";
  if (raw.includes("/emoji/emoji-resource/") || raw.includes("/baseemojisyastems/")) return "表情资源目录";
  if (raw.includes("/wpkcaches/")) return "钉钉程序缓存目录";
  if (raw.includes("/resource_cache/")) return "直播资源缓存目录";
  if (raw.includes("/downloaddefaultemotion/")) return "表情资源目录";
  if (raw.includes("/portrait/")) return "头像缓存目录";
  return "标准缓存目录";
}

function canTryOpen(item) {
  const ext = pathExtension(item.path || "");
  return [
    "jpg", "jpeg", "png", "gif", "webp", "heic",
    "mp4", "mov", "webm", "mkv",
    "mp3", "aac", "m4a", "flac", "ogg", "wav",
    "pdf", "txt", "json", "log", "html",
  ].includes(ext);
}

function buildNameCell(item) {
  const cell = document.createElement("td");
  const strong = document.createElement("strong");
  strong.textContent = item.name;
  const lineBreak = document.createElement("br");
  const sub = document.createElement("span");
  sub.textContent = item.path;
  cell.appendChild(strong);
  cell.appendChild(lineBreak);
  cell.appendChild(sub);
  return cell;
}

function buildCleanSummary(result, title) {
  const lines = [title, ""];
  (result.results || []).forEach((item) => {
    lines.push(`处理文件数: ${item.deleted_files || 0}`);
    lines.push(`释放空间: ${formatBytes(item.reclaimed_bytes || 0)}`);
    const skippedCount = (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0);
    lines.push(`跳过文件数: ${skippedCount}`);
    if ((item.deleted_paths || []).length) {
      lines.push("", "示例路径：");
      item.deleted_paths.slice(0, 12).forEach((path) => lines.push(`- ${path}`));
    }
    if ((item.skipped_paths || []).length) {
      lines.push("", "部分跳过路径：");
      item.skipped_paths.slice(0, 8).forEach((path) => lines.push(`- ${path}`));
    }
  });
  return lines.join("\n");
}

function getOverviewSelectedItems() {
  return overviewState.cards.flatMap((card) =>
    (card.items || []).filter((item) => overviewState.selectedIds.has(item.id))
  );
}

function updateOverviewSelectionSummary() {
  const selectedItems = getOverviewSelectedItems();
  const totalBytes = selectedItems.reduce((sum, item) => sum + Number(item.estimated_bytes || 0), 0);
  overviewSelectionSummary.textContent =
    `已勾选 ${selectedItems.length} 项，预计可处理 ${formatBytes(totalBytes)} 的文件或内存占用。`;
}

async function revealOverviewItem(item) {
  if (!item.reveal_path) {
    alert("这个项目暂时没有可在访达中定位的路径。");
    return;
  }
  await api("/api/reveal-file", { path: item.reveal_path });
}

async function openOverviewItem(item) {
  if (!item.open_path) {
    alert("这个项目暂时没有可直接打开的路径。");
    return;
  }
  await api("/api/open-file", { path: item.open_path });
}

function buildOverviewItem(card, item) {
  const wrapper = document.createElement("div");
  wrapper.className = "overview-item";

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = overviewState.selectedIds.has(item.id);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });

  const applyChecked = (checked) => {
    if (checked) overviewState.selectedIds.add(item.id);
    else overviewState.selectedIds.delete(item.id);
    checkbox.checked = checked;
    updateOverviewSelectionSummary();
  };

  const scope = `overview:${card.key}`;
  const startDrag = (event) => {
    const startedDrag = beginDragSelection(
      event,
      scope,
      overviewState.selectedIds,
      item.id,
      overviewState.selectionAnchors[card.key],
      (value) => { overviewState.selectionAnchors[card.key] = value; },
      card.items || [],
      applyChecked,
      (entry) => entry.id
    );
    if (!startedDrag && event.shiftKey) {
      renderOverviewCards(overviewState.cards);
      updateOverviewSelectionSummary();
    }
  };

  checkbox.addEventListener("mousedown", startDrag);
  checkbox.addEventListener("mouseenter", () => continueDragSelection(scope, applyChecked));

  const main = document.createElement("div");
  main.className = "overview-item-main";
  const title = document.createElement("p");
  title.className = "overview-item-title";
  title.textContent = item.name;
  const meta = document.createElement("p");
  meta.className = "overview-item-meta";
  meta.textContent = item.meta || "待确认项目";
  const note = document.createElement("p");
  note.className = "overview-item-note";
  note.textContent = item.note || "建议手动确认后再处理。";
  main.appendChild(title);
  main.appendChild(meta);
  main.appendChild(note);

  const actions = document.createElement("div");
  actions.className = "overview-item-actions";
  const revealButton = document.createElement("button");
  revealButton.textContent = "定位";
  revealButton.disabled = !item.reveal_path;
  revealButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    try {
      await revealOverviewItem(item);
      overviewSummary.textContent = `已在访达中定位：${item.name}`;
    } catch (error) {
      alert(error.message);
    }
  });
  const openButton = document.createElement("button");
  openButton.textContent = "打开";
  openButton.disabled = !item.open_path;
  openButton.addEventListener("click", async (event) => {
    event.stopPropagation();
    try {
      await openOverviewItem(item);
      overviewSummary.textContent = `已尝试打开：${item.name}`;
    } catch (error) {
      alert(error.message);
    }
  });
  actions.appendChild(revealButton);
  actions.appendChild(openButton);

  wrapper.appendChild(checkbox);
  wrapper.appendChild(main);
  wrapper.appendChild(actions);
  wrapper.addEventListener("mouseenter", () => continueDragSelection(scope, applyChecked));
  return wrapper;
}

function renderOverviewCards(cards) {
  overviewGrid.innerHTML = "";
  if (!cards.length) {
    overviewGrid.innerHTML = '<div class="overview-card empty-block">点击“开始全面检查”后，这里会按功能显示最值得你优先处理的建议。</div>';
    updateOverviewSelectionSummary();
    return;
  }
  cards.forEach((card) => {
    const wrapper = document.createElement("article");
    wrapper.className = `overview-card ${card.ok ? "is-good" : "is-alert"}`;

    const header = document.createElement("div");
    header.className = "overview-card-head";
    const title = document.createElement("h3");
    title.textContent = card.title;
    const badge = document.createElement("span");
    badge.className = `overview-badge ${card.ok ? "good" : "alert"}`;
    badge.textContent = card.status;
    header.appendChild(title);
    header.appendChild(badge);

    const body = document.createElement("pre");
    body.textContent = card.body;

    const list = document.createElement("div");
    list.className = "overview-items";
    if ((card.items || []).length) {
      card.items.forEach((item) => {
        list.appendChild(buildOverviewItem(card, item));
      });
    } else {
      const empty = document.createElement("div");
      empty.className = "empty-block";
      empty.textContent = card.ok ? "当前没有需要你手动处理的代表性项目。" : "当前没有可直接操作的样本，请点“打开详情页”查看完整列表。";
      list.appendChild(empty);
    }

    const footer = document.createElement("div");
    footer.className = "overview-card-actions";
    const button = document.createElement("button");
    button.textContent = "打开详情页";
    button.addEventListener("click", () => goToRoute(card.route));
    footer.appendChild(button);

    wrapper.appendChild(header);
    wrapper.appendChild(body);
    wrapper.appendChild(list);
    wrapper.appendChild(footer);
    overviewGrid.appendChild(wrapper);
  });
  updateOverviewSelectionSummary();
}

async function scanOverview(options = {}) {
  const { preserveResult = false } = options;
  try {
    setOverviewBusy(true, "扫描中，请稍候...");
    overviewSummary.textContent = "全面检查中，请稍候...";
    const result = await api("/api/scan-overview");
    overviewState.cards = result.cards || [];
    overviewState.selectedIds = new Set([...overviewState.selectedIds].filter((id) =>
      overviewState.cards.some((card) => (card.items || []).some((item) => item.id === id))
    ));
    overviewState.selectionAnchors = {};
    overviewSummary.textContent = result.all_good
      ? "全面检查完成。当前整体状态良好。"
      : `全面检查完成。发现 ${result.issue_count || 0} 个更值得优先处理的功能模块。`;
    if (!preserveResult && !result.all_good) {
      overviewResultBox.textContent = "全面检查已完成。\n\n你可以直接在卡片里勾选项目，然后点“一键处理已勾选项”。";
    }
    renderOverviewCards(overviewState.cards);
  } catch (error) {
    alert(error.message);
    overviewSummary.textContent = "全面检查失败，请看错误提示。";
  } finally {
    setOverviewBusy(false, "空闲");
  }
}

async function executeOverviewSelection() {
  const items = getOverviewSelectedItems();
  if (!items.length) {
    alert("请先在全面检查页勾选至少一个项目。");
    return;
  }
  if (!confirm(`即将处理 ${items.length} 个你勾选的项目，是否继续？`)) return;
  try {
    setOverviewBusy(true, "正在分模块处理，请稍候...");
    const result = await api("/api/execute-overview-actions", { items });
    overviewState.selectedIds.clear();
    overviewState.selectionAnchors = {};
    const lines = [
      "全面检查处理完成",
      "",
      `成功处理: ${result.success_count || 0} 项`,
      `处理失败: ${result.failed_count || 0} 项`,
      `释放空间 / 估计回收: ${formatBytes(result.reclaimed_bytes || 0)}`,
    ];
    if ((result.modules || []).length) {
      lines.push("", "分模块结果：");
      result.modules.forEach((module) => {
        lines.push(
          `- ${module.title}: 成功 ${module.success_count || 0} 项，失败 ${module.failed_count || 0} 项，释放 ${formatBytes(module.reclaimed_bytes || 0)}`
        );
      });
    }
    overviewResultBox.textContent = lines.join("\n");
    overviewSummary.textContent = `已处理 ${result.handled_count || 0} 个总览项目。`;
    await scanOverview({ preserveResult: true });
  } catch (error) {
    alert(error.message);
  } finally {
    setOverviewBusy(false, "空闲");
  }
}

function removeDeletedPaths(paths, items, selectedSet, stateObject, currentKey) {
  const deleted = new Set(paths || []);
  const filtered = items.filter((item) => !deleted.has(item.path));
  const nextSelected = new Set([...selectedSet].filter((path) => !deleted.has(path)));
  stateObject[currentKey] = null;
  return { filtered, nextSelected };
}

function fileCleaningItems(view) {
  if (view === "candidate") return fileCleaningState.candidates;
  if (view === "installer") return fileCleaningState.installers;
  if (view === "download") return fileCleaningState.downloads;
  if (view === "large") return fileCleaningState.largeFiles;
  return [];
}

function fileCleaningSelectedSet(view) {
  if (view === "candidate") return fileCleaningState.candidateSelectedPaths;
  if (view === "installer") return fileCleaningState.installerSelectedPaths;
  if (view === "download") return fileCleaningState.downloadSelectedPaths;
  if (view === "large") return fileCleaningState.largeSelectedPaths;
  return new Set();
}

function getCurrentFileCleaningItem() {
  if (!fileCleaningState.currentView || !fileCleaningState.currentPath) return null;
  return fileCleaningItems(fileCleaningState.currentView).find((item) => item.path === fileCleaningState.currentPath) || null;
}

function ensureCurrentFileCleaningItem() {
  const current = getCurrentFileCleaningItem();
  if (current) return current;
  if (fileCleaningState.candidates.length) {
    fileCleaningState.currentView = "candidate";
    fileCleaningState.currentPath = fileCleaningState.candidates[0].path;
    return fileCleaningState.candidates[0];
  }
  if (fileCleaningState.installers.length) {
    fileCleaningState.currentView = "installer";
    fileCleaningState.currentPath = fileCleaningState.installers[0].path;
    return fileCleaningState.installers[0];
  }
  if (fileCleaningState.downloads.length) {
    fileCleaningState.currentView = "download";
    fileCleaningState.currentPath = fileCleaningState.downloads[0].path;
    return fileCleaningState.downloads[0];
  }
  if (fileCleaningState.largeFiles.length) {
    fileCleaningState.currentView = "large";
    fileCleaningState.currentPath = fileCleaningState.largeFiles[0].path;
    return fileCleaningState.largeFiles[0];
  }
  fileCleaningState.currentView = null;
  fileCleaningState.currentPath = null;
  return null;
}

function renderFileDetail(item, view) {
  if (!item) {
    revealFileBtn.disabled = true;
    openFileBtn.disabled = true;
    detailBox.textContent = "扫描后，点击候选文件、安装文件、下载文件或大型文件，就会在这里显示完整路径、大小和说明。";
    return;
  }
  revealFileBtn.disabled = false;
  openFileBtn.disabled = !canTryOpen(item);
  const checked = fileCleaningSelectedSet(view).has(item.path) ? "已勾选" : "未勾选";
  const sourceMap = {
    candidate: "候选文件",
    installer: "安装文件",
    download: "下载文件",
    large: "大型文件 Top 10",
  };
  const source = sourceMap[view] || "文件清理";
  detailBox.textContent = [
    `区域: ${source}`,
    `文件名: ${item.name}`,
    `分类: ${item.group}`,
    `内容判断: ${classifyReadableType(item)}`,
    `位置标签: ${buildLocationTag(item)}`,
    `文件后缀: ${pathExtension(item.path) || "无"}`,
    `状态: ${checked}`,
    `大小: ${formatBytes(item.size)}`,
    `使用情况: ${formatAge(item.age_days)}`,
    `说明: ${item.note || "可手动确认是否需要"}`,
    "",
    "完整路径:",
    item.path,
  ].join("\n");
}

function updateFileSectionSummary(items, selectedPaths, target, label) {
  const totalBytes = items.reduce((sum, item) => sum + Number(item.size || 0), 0);
  const selectedItems = items.filter((item) => selectedPaths.has(item.path));
  const selectedBytes = selectedItems.reduce((sum, item) => sum + Number(item.size || 0), 0);
  target.textContent =
    `${label}：${items.length} 个，总大小 ${formatBytes(totalBytes)}；` +
    `已勾选 ${selectedItems.length} 个，共 ${formatBytes(selectedBytes)}`;
}

function refreshFileSelectionSummary(view) {
  if (view === "candidate") {
    updateFileSectionSummary(fileCleaningState.candidates, fileCleaningState.candidateSelectedPaths, candidateSummary, "候选文件");
    return;
  }
  if (view === "installer") {
    updateFileSectionSummary(fileCleaningState.installers, fileCleaningState.installerSelectedPaths, installerSummary, "安装文件");
    return;
  }
  if (view === "download") {
    updateFileSectionSummary(fileCleaningState.downloads, fileCleaningState.downloadSelectedPaths, downloadSummary, "下载文件");
    return;
  }
  if (view === "large") {
    updateFileSectionSummary(fileCleaningState.largeFiles, fileCleaningState.largeSelectedPaths, largeFilesSummary, "大型文件");
  }
}

function buildFileCleaningRow(item, view, lastColumnText) {
  const tr = document.createElement("tr");
  if (fileCleaningState.currentView === view && fileCleaningState.currentPath === item.path) {
    tr.classList.add("selected");
  }

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = fileCleaningSelectedSet(view).has(item.path);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    const selectedSet = fileCleaningSelectedSet(view);
    if (checked) selectedSet.add(item.path);
    else selectedSet.delete(item.path);
    checkbox.checked = checked;
    refreshFileSelectionSummary(view);
    if (fileCleaningState.currentView === view && fileCleaningState.currentPath === item.path) {
      renderFileDetail(item, view);
    }
  };
  const startDrag = (event) => {
    const selectedSet = fileCleaningSelectedSet(view);
    const startedDrag = beginDragSelection(
      event,
      `files:${view}`,
      selectedSet,
      item.path,
      fileCleaningState.selectionAnchors[view],
      (value) => { fileCleaningState.selectionAnchors[view] = value; },
      fileCleaningItems(view),
      applyChecked
    );
    if (!startedDrag && event.shiftKey) {
      renderFileCleaningTables();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection(`files:${view}`, applyChecked));
  checkboxCell.appendChild(checkbox);

  const sizeCell = document.createElement("td");
  sizeCell.textContent = formatBytes(item.size);

  const lastCell = document.createElement("td");
  lastCell.textContent = lastColumnText;

  tr.appendChild(checkboxCell);
  tr.appendChild(buildNameCell(item));
  tr.appendChild(sizeCell);
  tr.appendChild(lastCell);

  tr.addEventListener("click", () => {
    fileCleaningState.currentView = view;
    fileCleaningState.currentPath = item.path;
    renderFileCleaningTables();
  });

  tr.addEventListener("dblclick", async () => {
    fileCleaningState.currentView = view;
    fileCleaningState.currentPath = item.path;
    renderFileCleaningTables();
    await revealFileCleaningItem();
  });

  return tr;
}

function renderFileCleaningTable(body, items, view, emptyText) {
  body.innerHTML = "";
  if (!items.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = emptyText;
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }
  items.forEach((item) => {
    let label = item.group || item.note || "";
    if (view === "large") {
      label = formatAge(item.age_days);
    }
    if (view === "download") {
      label = item.note || formatAge(item.age_days);
    }
    if (view === "installer") {
      label = item.note || "安装文件";
    }
    body.appendChild(buildFileCleaningRow(item, view, label));
  });
}

function renderFileCleaningTables() {
  renderFileCleaningTable(
    candidateTableBody,
    fileCleaningState.candidates,
    "candidate",
    "扫描后，这里会显示重复文件和长期未使用的大文件。"
  );
  renderFileCleaningTable(
    installerTableBody,
    fileCleaningState.installers,
    "installer",
    "扫描后，这里会显示 Desktop、Documents、Downloads 里的 DMG、PKG 等安装文件。"
  );
  renderFileCleaningTable(
    downloadTableBody,
    fileCleaningState.downloads,
    "download",
    "扫描后，这里会显示 Downloads 中体积较大或长期未使用的下载文件。"
  );
  renderFileCleaningTable(
    largeFilesTableBody,
    fileCleaningState.largeFiles,
    "large",
    "扫描后，这里会按大小显示前 10 个大型文件。"
  );
  updateFileSectionSummary(
    fileCleaningState.candidates,
    fileCleaningState.candidateSelectedPaths,
    candidateSummary,
    "候选文件"
  );
  updateFileSectionSummary(
    fileCleaningState.installers,
    fileCleaningState.installerSelectedPaths,
    installerSummary,
    "安装文件"
  );
  updateFileSectionSummary(
    fileCleaningState.downloads,
    fileCleaningState.downloadSelectedPaths,
    downloadSummary,
    "下载文件"
  );
  updateFileSectionSummary(
    fileCleaningState.largeFiles,
    fileCleaningState.largeSelectedPaths,
    largeFilesSummary,
    "大型文件"
  );
  renderFileDetail(ensureCurrentFileCleaningItem(), fileCleaningState.currentView);
}

function buildFileScanSummary(result) {
  const lines = [
    "扫描摘要",
    "",
    `基础清理范围总空间: ${formatBytes(result.grand_total_bytes || 0)}`,
    `手动确认文件总空间: ${formatBytes(result.grand_total_candidate_bytes || 0)}`,
    `大型文件 Top 10 总空间: ${formatBytes(result.large_files?.total_bytes || 0)}`,
    "",
    "基础分类统计：",
  ];
  (result.categories || []).forEach((category) => {
    lines.push(`- ${category.name}: ${formatBytes(category.total_bytes || 0)}，${category.file_count || 0} 个文件`);
  });
  if (result.large_files?.file_count) {
    lines.push("", "大型文件 Top 10：");
    (result.large_files.files || []).slice(0, 10).forEach((file) => {
      lines.push(`- ${file.path} | ${formatBytes(file.size || 0)}`);
    });
  }
  if ((result.findings || []).length) {
    lines.push("", "手动确认分组：");
    result.findings.forEach((finding) => {
      lines.push(
        `- ${localizedFindingName(finding.key, finding.name)}: ${finding.file_count || 0} 个文件，${formatBytes(finding.total_bytes || 0)}`
      );
    });
  }
  return lines.join("\n");
}

async function scanFileCleaning() {
  try {
    setFileBusy(true, "扫描中，请稍候...");
    summary.textContent = "扫描中，请稍候...";
    resultBox.textContent = "扫描中，请稍候...\n\n如果文件很多，首次扫描可能需要十几秒。";
    const result = await api("/api/scan", { categories: selectedFileCleaningCategories() });

    fileCleaningState.candidates = [];
    fileCleaningState.installers = [];
    fileCleaningState.downloads = [];
    fileCleaningState.largeFiles = [];
    fileCleaningState.candidateSelectedPaths.clear();
    fileCleaningState.installerSelectedPaths.clear();
    fileCleaningState.downloadSelectedPaths.clear();
    fileCleaningState.largeSelectedPaths.clear();
    fileCleaningState.currentView = null;
    fileCleaningState.currentPath = null;
    fileCleaningState.selectionAnchors = { candidate: null, installer: null, download: null, large: null };

    (result.findings || []).forEach((finding) => {
      const mappedFiles = (finding.files || []).map((file) => ({
        group: localizedFindingName(finding.key, finding.name),
        path: file.path,
        name: file.path.split("/").pop() || file.path,
        size: file.size,
        age_days: file.age_days,
        note: file.note,
      }));

      if (finding.key === "installer_files") {
        fileCleaningState.installers.push(...mappedFiles);
      } else if (finding.key === "download_files") {
        fileCleaningState.downloads.push(...mappedFiles);
      } else {
        fileCleaningState.candidates.push(...mappedFiles);
      }
    });

    (result.large_files?.files || []).forEach((file) => {
      fileCleaningState.largeFiles.push({
        group: "大型文件",
        path: file.path,
        name: file.path.split("/").pop() || file.path,
        size: file.size,
        age_days: file.age_days,
        note: file.note || "按大小排名进入前 10",
      });
    });

    summary.textContent =
      `扫描完成。候选文件 ${fileCleaningState.candidates.length} 个；安装文件 ${fileCleaningState.installers.length} 个；` +
      `下载文件 ${fileCleaningState.downloads.length} 个；大型文件 ${fileCleaningState.largeFiles.length} 个。`;
    resultBox.textContent = buildFileScanSummary(result);
    renderFileCleaningTables();
  } catch (error) {
    alert(error.message);
    summary.textContent = "扫描失败，请看错误提示。";
  } finally {
    setFileBusy(false, "空闲");
  }
}

async function executeFileCleaningCategories() {
  const selectedCount =
    fileCleaningState.candidateSelectedPaths.size +
    fileCleaningState.installerSelectedPaths.size +
    fileCleaningState.downloadSelectedPaths.size +
    fileCleaningState.largeSelectedPaths.size;
  if (selectedCount > 0) {
    const proceed = confirm(
      `你当前勾选了 ${selectedCount} 个手动文件。\n\n` +
      "“执行基础清理”不会删除这些勾选文件，它只会处理缓存、日志和废纸篓。\n\n仍然继续执行基础清理吗？"
    );
    if (!proceed) return;
  }

  if (!confirm("这会真实删除缓存、日志和废纸篓里的文件，是否继续？")) return;

  try {
    setFileBusy(true, "执行基础清理中，请稍候...");
    const result = await api("/api/clean-categories", {
      categories: selectedFileCleaningCategories(),
      dry_run: false,
    });
    resultBox.textContent = buildCleanSummary(result, "执行基础清理");
    const rows = result.results || [];
    const actual = rows.every((item) => item.dry_run === false);
    const deletedCount = rows.reduce((sum, item) => sum + Number(item.deleted_files || 0), 0);
    const skippedCount = rows.reduce(
      (sum, item) => sum + (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0),
      0
    );
    if (!actual) {
      summary.textContent = "后端返回的是预演结果，没有真实删除。";
    } else if (deletedCount === 0) {
      summary.textContent = `执行基础清理完成，但没有删掉任何文件。通常是文件被占用或权限不足。跳过 ${skippedCount} 个。`;
    } else {
      summary.textContent = `执行基础清理完成，实际删除 ${deletedCount} 个文件，跳过 ${skippedCount} 个。`;
    }
  } catch (error) {
    alert(error.message);
  } finally {
    setFileBusy(false, "空闲");
  }
}

async function previewFileCleaningSelection(view, title) {
  const paths = [...fileCleaningSelectedSet(view)];
  if (!paths.length) {
    alert("请先勾选至少一个文件。");
    return;
  }
  try {
    setFileBusy(true, `${title}中，请稍候...`);
    const result = await api("/api/clean-files", { paths, dry_run: true });
    resultBox.textContent = buildCleanSummary(result, title);
    const item = (result.results || [])[0] || {};
    summary.textContent = `${title}完成。涉及 ${item.deleted_files || 0} 个文件，预计释放 ${formatBytes(item.reclaimed_bytes || 0)}。`;
  } catch (error) {
    alert(error.message);
  } finally {
    setFileBusy(false, "空闲");
  }
}

async function deleteFileCleaningSelection(view, title) {
  const paths = [...fileCleaningSelectedSet(view)];
  if (!paths.length) {
    alert("请先勾选至少一个文件。");
    return;
  }
  if (!confirm(`即将删除 ${paths.length} 个你勾选的文件，是否继续？`)) return;
  try {
    setFileBusy(true, `${title}中，请稍候...`);
    const result = await api("/api/clean-files", { paths, dry_run: false });
    resultBox.textContent = buildCleanSummary(result, title);
    const item = (result.results || [])[0] || {};
    if (item.dry_run === false) {
      const deleted = new Set(item.deleted_paths || []);
      fileCleaningState.candidates = fileCleaningState.candidates.filter((candidate) => !deleted.has(candidate.path));
      fileCleaningState.installers = fileCleaningState.installers.filter((candidate) => !deleted.has(candidate.path));
      fileCleaningState.downloads = fileCleaningState.downloads.filter((candidate) => !deleted.has(candidate.path));
      fileCleaningState.largeFiles = fileCleaningState.largeFiles.filter((candidate) => !deleted.has(candidate.path));
      fileCleaningState.candidateSelectedPaths = new Set(
        [...fileCleaningState.candidateSelectedPaths].filter((path) => !deleted.has(path))
      );
      fileCleaningState.installerSelectedPaths = new Set(
        [...fileCleaningState.installerSelectedPaths].filter((path) => !deleted.has(path))
      );
      fileCleaningState.downloadSelectedPaths = new Set(
        [...fileCleaningState.downloadSelectedPaths].filter((path) => !deleted.has(path))
      );
      fileCleaningState.largeSelectedPaths = new Set(
        [...fileCleaningState.largeSelectedPaths].filter((path) => !deleted.has(path))
      );
      if (fileCleaningState.currentPath && deleted.has(fileCleaningState.currentPath)) {
        fileCleaningState.currentPath = null;
        fileCleaningState.currentView = null;
      }
      const skippedCount = (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0);
      summary.textContent = `${title}完成，实际删除 ${item.deleted_files || 0} 个，跳过 ${skippedCount} 个。`;
      renderFileCleaningTables();
    } else {
      summary.textContent = "后端返回的是预演结果，没有真实删除。";
    }
  } catch (error) {
    alert(error.message);
  } finally {
    setFileBusy(false, "空闲");
  }
}

async function revealFileCleaningItem() {
  const current = getCurrentFileCleaningItem();
  if (!current) {
    alert("请先选择一个文件。");
    return;
  }
  try {
    setFileBusy(true, "正在访达中定位文件...");
    await api("/api/reveal-file", { path: current.path });
    summary.textContent = `已在访达中显示：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setFileBusy(false, "空闲");
  }
}

async function openFileCleaningItem() {
  const current = getCurrentFileCleaningItem();
  if (!current) {
    alert("请先选择一个文件。");
    return;
  }
  if (!canTryOpen(current)) {
    alert("这个文件类型不适合直接打开。建议先在访达中显示，再手动判断。");
    return;
  }
  try {
    setFileBusy(true, "正在尝试打开文件...");
    await api("/api/open-file", { path: current.path });
    summary.textContent = `已尝试打开：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setFileBusy(false, "空闲");
  }
}

function getCurrentAppCacheItem() {
  if (!appCacheState.currentPath) return null;
  return appCacheState.files.find((item) => item.path === appCacheState.currentPath) || null;
}

function ensureCurrentAppCacheItem() {
  const current = getCurrentAppCacheItem();
  if (current) return current;
  if (appCacheState.files.length) {
    appCacheState.currentPath = appCacheState.files[0].path;
    return appCacheState.files[0];
  }
  appCacheState.currentPath = null;
  return null;
}

function markCurrentAppCacheRow() {
  appCacheGroups.querySelectorAll("tbody tr[data-path]").forEach((row) => {
    row.classList.toggle("selected", row.dataset.path === appCacheState.currentPath);
  });
}

function renderAppCacheDetail(item) {
  if (!item) {
    revealAppCacheBtn.disabled = true;
    openAppCacheBtn.disabled = true;
    appCacheDetailBox.textContent = "扫描软件缓存后，点击某个缓存文件，就会在这里显示它的完整路径、所属应用和说明。";
    return;
  }
  revealAppCacheBtn.disabled = false;
  openAppCacheBtn.disabled = !canTryOpen(item);
  const checked = appCacheState.selectedPaths.has(item.path) ? "已勾选" : "未勾选";
  appCacheDetailBox.textContent = [
    `所属应用: ${item.group}`,
    `文件名: ${item.name}`,
    `内容判断: ${classifyReadableType(item)}`,
    `位置标签: ${buildLocationTag(item)}`,
    `文件后缀: ${pathExtension(item.path) || "无"}`,
    `状态: ${checked}`,
    `大小: ${formatBytes(item.size)}`,
    `使用情况: ${formatAge(item.age_days)}`,
    `说明: ${item.note || "软件缓存文件"}`,
    "",
    "完整路径:",
    item.path,
  ].join("\n");
}

function updateAppCacheSummary() {
  const totalBytes = appCacheState.files.reduce((sum, item) => sum + Number(item.size || 0), 0);
  const selectedItems = appCacheState.files.filter((item) => appCacheState.selectedPaths.has(item.path));
  const selectedBytes = selectedItems.reduce((sum, item) => sum + Number(item.size || 0), 0);
  appCacheFilesSummary.textContent =
    `缓存文件：${appCacheState.files.length} 个，总大小 ${formatBytes(totalBytes)}；` +
    `已勾选 ${selectedItems.length} 个，共 ${formatBytes(selectedBytes)}`;
}

function groupAppCacheFiles() {
  const grouped = new Map();
  appCacheState.files.forEach((item) => {
    if (!grouped.has(item.group)) grouped.set(item.group, []);
    grouped.get(item.group).push(item);
  });
  return [...grouped.entries()].map(([group, files]) => {
    files.sort((left, right) => Number(right.size || 0) - Number(left.size || 0) || left.path.localeCompare(right.path));
    const totalBytes = files.reduce((sum, item) => sum + Number(item.size || 0), 0);
    const category = appCacheState.categories.find((entry) => entry.name === group);
    return { group, files, totalBytes, fileCount: files.length, category };
  }).sort((left, right) => right.totalBytes - left.totalBytes || left.group.localeCompare(right.group));
}

function buildAppCacheGroupRow(item) {
  const tr = document.createElement("tr");
  tr.dataset.path = item.path;
  if (appCacheState.currentPath === item.path) tr.classList.add("selected");

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = appCacheState.selectedPaths.has(item.path);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    if (checked) appCacheState.selectedPaths.add(item.path);
    else appCacheState.selectedPaths.delete(item.path);
    checkbox.checked = checked;
    updateAppCacheSummary();
    if (appCacheState.currentPath === item.path) {
      renderAppCacheDetail(item);
    }
  };
  const startDrag = (event) => {
    const startedDrag = beginDragSelection(
      event,
      `app-cache:${item.group}`,
      appCacheState.selectedPaths,
      item.path,
      appCacheState.selectionAnchor,
      (value) => { appCacheState.selectionAnchor = value; },
      appCacheState.files,
      applyChecked
    );
    if (!startedDrag && event.shiftKey) {
      renderAppCacheGroups();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection(`app-cache:${item.group}`, applyChecked));
  checkboxCell.appendChild(checkbox);

  const sizeCell = document.createElement("td");
  sizeCell.textContent = formatBytes(item.size);

  const typeCell = document.createElement("td");
  typeCell.textContent = classifyReadableType(item);

  const noteCell = document.createElement("td");
  noteCell.textContent = item.note || "软件缓存文件";

  const locationCell = document.createElement("td");
  locationCell.textContent = buildLocationTag(item);

  tr.appendChild(checkboxCell);
  tr.appendChild(buildNameCell(item));
  tr.appendChild(sizeCell);
  tr.appendChild(typeCell);
  tr.appendChild(noteCell);
  tr.appendChild(locationCell);

  tr.addEventListener("click", () => {
    appCacheState.currentPath = item.path;
    markCurrentAppCacheRow();
    renderAppCacheDetail(item);
  });

  tr.addEventListener("dblclick", async () => {
    appCacheState.currentPath = item.path;
    markCurrentAppCacheRow();
    renderAppCacheDetail(item);
    await revealAppCacheItem();
  });

  return tr;
}

function renderAppCacheGroups() {
  appCacheGroups.innerHTML = "";
  if (!appCacheState.files.length) {
    appCacheState.expandedGroups.clear();
    appCacheState.groupScrollTop.clear();
    appCacheGroups.innerHTML = '<div class="empty-block">扫描后，这里会按应用分组显示缓存文件。每组都可以折叠，方便你逐个判断。</div>';
    updateAppCacheSummary();
    renderAppCacheDetail(null);
    return;
  }

  const grouped = groupAppCacheFiles();
  const hasSavedExpandedGroups = appCacheState.expandedGroups.size > 0;
  grouped.forEach((entry, index) => {
    const details = document.createElement("details");
    details.className = "group-card";
    details.dataset.group = entry.group;

    const containsCurrent = entry.files.some((item) => item.path === appCacheState.currentPath);
    details.open = appCacheState.expandedGroups.has(entry.group) ||
      (!hasSavedExpandedGroups && (containsCurrent || index === 0));
    details.addEventListener("toggle", () => {
      if (details.open) appCacheState.expandedGroups.add(entry.group);
      else appCacheState.expandedGroups.delete(entry.group);
    });

    const summaryEl = document.createElement("summary");
    const title = document.createElement("span");
    title.textContent = entry.group;
    const meta = document.createElement("span");
    meta.className = "group-meta";
    meta.textContent = `${entry.fileCount} 个文件 · ${formatBytes(entry.totalBytes)}`;
    summaryEl.appendChild(title);
    summaryEl.appendChild(meta);
    details.appendChild(summaryEl);

    const body = document.createElement("div");
    body.className = "group-body";
    body.dataset.group = entry.group;
    body.addEventListener("scroll", () => {
      appCacheState.groupScrollTop.set(entry.group, body.scrollTop);
    }, { passive: true });

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>选择</th>
        <th>文件名</th>
        <th>大小</th>
        <th>文件内容</th>
        <th>缓存说明</th>
        <th>位置标签</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    entry.files.forEach((item) => tbody.appendChild(buildAppCacheGroupRow(item)));
    table.appendChild(tbody);
    body.appendChild(table);

    if (entry.category?.description) {
      const tip = document.createElement("p");
      tip.className = "group-meta";
      tip.textContent = entry.category.description;
      body.appendChild(tip);
    }

    details.appendChild(body);
    appCacheGroups.appendChild(details);

    const savedScrollTop = appCacheState.groupScrollTop.get(entry.group);
    if (savedScrollTop) {
      body.scrollTop = savedScrollTop;
    }
  });

  updateAppCacheSummary();
  renderAppCacheDetail(ensureCurrentAppCacheItem());
  markCurrentAppCacheRow();
}

function buildAppCacheScanSummary(result) {
  const lines = [
    "软件缓存扫描摘要",
    "",
    `扫描到的缓存总空间: ${formatBytes(result.total_bytes || 0)}`,
    `扫描到的缓存文件数: ${result.total_file_count || 0}`,
    `当前展示的大型缓存文件数: ${(result.files || []).length}`,
    "",
    "应用统计：",
  ];
  (result.categories || []).forEach((category) => {
    lines.push(`- ${category.name}: ${formatBytes(category.total_bytes || 0)}，${category.file_count || 0} 个文件`);
  });
  if ((result.files || []).length) {
    lines.push("", "大型缓存文件示例：");
    result.files.slice(0, 20).forEach((file) => {
      lines.push(`- [${file.group}] ${file.path} | ${formatBytes(file.size || 0)}`);
    });
  }
  return lines.join("\n");
}

async function scanAppCaches() {
  try {
    setAppCacheBusy(true, "扫描中，请稍候...");
    appCacheSummary.textContent = "扫描软件缓存中，请稍候...";
    appCacheResultBox.textContent = "扫描软件缓存中，请稍候...\n\n我会优先列出体积较大的缓存文件，方便你手动判断。";
    const result = await api("/api/scan-app-caches", { categories: selectedAppCacheCategories() });

    appCacheState.categories = result.categories || [];
    appCacheState.files = (result.files || []).map((file) => ({
      group: file.group || "未知应用",
      path: file.path,
      name: file.path.split("/").pop() || file.path,
      size: file.size,
      age_days: file.age_days,
      note: file.note,
    }));
    appCacheState.selectedPaths.clear();
    appCacheState.currentPath = null;
    appCacheState.expandedGroups.clear();
    appCacheState.groupScrollTop.clear();
    appCacheState.selectionAnchor = null;

    appCacheSummary.textContent =
      `扫描完成。共发现 ${result.total_file_count || 0} 个缓存文件，总空间 ${formatBytes(result.total_bytes || 0)}。`;
    appCacheResultBox.textContent = buildAppCacheScanSummary(result);
    renderAppCacheGroups();
  } catch (error) {
    alert(error.message);
    appCacheSummary.textContent = "扫描软件缓存失败，请看错误提示。";
  } finally {
    setAppCacheBusy(false, "空闲");
  }
}

async function executeAppCacheCategories() {
  if (appCacheState.selectedPaths.size > 0) {
    const proceed = confirm(
      `你当前勾选了 ${appCacheState.selectedPaths.size} 个缓存文件。\n\n` +
      "“执行软件缓存清理”不会只删这些勾选文件，而是会按上面勾选的软件，直接清理这些软件的缓存目录。\n\n仍然继续吗？"
    );
    if (!proceed) return;
  }

  if (!confirm("这会真实删除已勾选软件的缓存目录内容，是否继续？")) return;

  try {
    setAppCacheBusy(true, "执行软件缓存清理中，请稍候...");
    const result = await api("/api/clean-app-caches", {
      categories: selectedAppCacheCategories(),
      dry_run: false,
    });
    appCacheResultBox.textContent = buildCleanSummary(result, "执行软件缓存清理");
    const rows = result.results || [];
    const deletedCount = rows.reduce((sum, item) => sum + Number(item.deleted_files || 0), 0);
    const skippedCount = rows.reduce(
      (sum, item) => sum + (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0),
      0
    );
    if (deletedCount === 0) {
      appCacheSummary.textContent = `执行软件缓存清理完成，但没有删掉任何文件。跳过 ${skippedCount} 个。`;
    } else {
      appCacheSummary.textContent = `执行软件缓存清理完成，实际删除 ${deletedCount} 个文件，跳过 ${skippedCount} 个。`;
    }
  } catch (error) {
    alert(error.message);
  } finally {
    setAppCacheBusy(false, "空闲");
  }
}

async function previewAppCacheSelection() {
  const paths = [...appCacheState.selectedPaths];
  if (!paths.length) {
    alert("请先勾选至少一个缓存文件。");
    return;
  }
  try {
    setAppCacheBusy(true, "预演缓存文件中，请稍候...");
    const result = await api("/api/clean-files", { paths, dry_run: true });
    appCacheResultBox.textContent = buildCleanSummary(result, "预演缓存文件");
    const item = (result.results || [])[0] || {};
    appCacheSummary.textContent =
      `预演缓存文件完成。涉及 ${item.deleted_files || 0} 个文件，预计释放 ${formatBytes(item.reclaimed_bytes || 0)}。`;
  } catch (error) {
    alert(error.message);
  } finally {
    setAppCacheBusy(false, "空闲");
  }
}

async function deleteAppCacheSelection() {
  const paths = [...appCacheState.selectedPaths];
  if (!paths.length) {
    alert("请先勾选至少一个缓存文件。");
    return;
  }
  if (!confirm(`即将删除 ${paths.length} 个你勾选的缓存文件，是否继续？`)) return;
  try {
    setAppCacheBusy(true, "删除缓存文件中，请稍候...");
    const result = await api("/api/clean-files", { paths, dry_run: false });
    appCacheResultBox.textContent = buildCleanSummary(result, "删除缓存文件");
    const item = (result.results || [])[0] || {};
    if (item.dry_run === false) {
      const deleted = new Set(item.deleted_paths || []);
      appCacheState.files = appCacheState.files.filter((file) => !deleted.has(file.path));
      appCacheState.selectedPaths = new Set([...appCacheState.selectedPaths].filter((path) => !deleted.has(path)));
      if (appCacheState.currentPath && deleted.has(appCacheState.currentPath)) {
        appCacheState.currentPath = null;
      }
      const skippedCount = (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0);
      appCacheSummary.textContent = `删除缓存文件完成，实际删除 ${item.deleted_files || 0} 个，跳过 ${skippedCount} 个。`;
      renderAppCacheGroups();
    } else {
      appCacheSummary.textContent = "后端返回的是预演结果，没有真实删除。";
    }
  } catch (error) {
    alert(error.message);
  } finally {
    setAppCacheBusy(false, "空闲");
  }
}

async function openAppCacheItem() {
  const current = getCurrentAppCacheItem();
  if (!current) {
    alert("请先选择一个缓存文件。");
    return;
  }
  if (!canTryOpen(current)) {
    alert("这个缓存文件类型不适合直接打开。建议先在访达中显示，再看它所在目录。");
    return;
  }
  try {
    setAppCacheBusy(true, "正在尝试打开缓存文件...");
    await api("/api/open-file", { path: current.path });
    appCacheSummary.textContent = `已尝试打开：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setAppCacheBusy(false, "空闲");
  }
}

async function revealAppCacheItem() {
  const current = getCurrentAppCacheItem();
  if (!current) {
    alert("请先选择一个缓存文件。");
    return;
  }
  try {
    setAppCacheBusy(true, "正在访达中定位缓存文件...");
    await api("/api/reveal-file", { path: current.path });
    appCacheSummary.textContent = `已在访达中显示：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setAppCacheBusy(false, "空闲");
  }
}

function getCurrentStartupItem() {
  if (!startupState.currentId) return null;
  return startupState.items.find((item) => item.id === startupState.currentId) || null;
}

function ensureCurrentStartupItem() {
  const current = getCurrentStartupItem();
  if (current) return current;
  if (startupState.items.length) {
    startupState.currentId = startupState.items[0].id;
    return startupState.items[0];
  }
  startupState.currentId = null;
  return null;
}

function markCurrentStartupRow() {
  startupGroups.querySelectorAll("tbody tr[data-id]").forEach((row) => {
    row.classList.toggle("selected", row.dataset.id === startupState.currentId);
  });
}

function renderStartupDetail(item) {
  if (!item) {
    revealStartupBtn.disabled = true;
    openStartupBtn.disabled = true;
    startupDetailBox.textContent = "扫描后，点击某个启动项，就会在这里显示它的路径、类型和估计影响。";
    return;
  }
  revealStartupBtn.disabled = !item.action_path;
  openStartupBtn.disabled = !item.action_path;
  const checked = startupState.selectedIds.has(item.id) ? "已勾选" : "未勾选";
  startupDetailBox.textContent = [
    `来源: ${item.group}`,
    `名称: ${item.name}`,
    `类型: ${item.kind === "login_item" ? "登录项" : "后台项目"}`,
    `估计影响: ${item.impact_level}`,
    `判断依据: ${item.impact_reason || "未提供"}`,
    `状态: ${checked}`,
    `隐藏启动: ${item.hidden ? "是" : "否"}`,
    `RunAtLoad: ${item.run_at_load ? "是" : "否"}`,
    `StartInterval: ${item.start_interval ? `${item.start_interval} 秒` : "无"}`,
    `WatchPaths: ${(item.watch_paths || []).length ? item.watch_paths.join(" | ") : "无"}`,
    item.label ? `Label: ${item.label}` : "",
    item.plist_path ? `后台项目配置文件: ${item.plist_path}` : "",
    item.path ? `程序/目标路径: ${item.path}` : "程序/目标路径: 未解析到",
  ].filter(Boolean).join("\n");
}

function updateStartupSummary() {
  const selectedItems = startupState.items.filter((item) => startupState.selectedIds.has(item.id));
  const highImpactCount = startupState.items.filter((item) => item.impact_level === "高").length;
  startupItemsSummary.textContent =
    `启动项：${startupState.items.length} 个；高影响 ${highImpactCount} 个；已勾选 ${selectedItems.length} 个`;
}

function groupStartupItems() {
  const grouped = new Map();
  startupState.items.forEach((item) => {
    if (!grouped.has(item.group)) grouped.set(item.group, []);
    grouped.get(item.group).push(item);
  });
  return [...grouped.entries()].map(([group, items]) => {
    items.sort((left, right) => {
      const leftScore = { "高": 0, "中": 1, "低": 2 }[left.impact_level] ?? 3;
      const rightScore = { "高": 0, "中": 1, "低": 2 }[right.impact_level] ?? 3;
      return leftScore - rightScore || left.name.localeCompare(right.name);
    });
    return {
      group,
      items,
      highImpactCount: items.filter((item) => item.impact_level === "高").length,
    };
  });
}

function buildStartupNameCell(item) {
  const cell = document.createElement("td");
  const strong = document.createElement("strong");
  strong.textContent = item.name;
  const lineBreak = document.createElement("br");
  const sub = document.createElement("span");
  sub.textContent = item.path || item.plist_path || "未解析到路径";
  cell.appendChild(strong);
  cell.appendChild(lineBreak);
  cell.appendChild(sub);
  return cell;
}

function buildStartupGroupRow(item) {
  const tr = document.createElement("tr");
  tr.dataset.id = item.id;
  if (startupState.currentId === item.id) tr.classList.add("selected");

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = startupState.selectedIds.has(item.id);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    if (checked) startupState.selectedIds.add(item.id);
    else startupState.selectedIds.delete(item.id);
    checkbox.checked = checked;
    updateStartupSummary();
    if (startupState.currentId === item.id) {
      renderStartupDetail(item);
    }
  };
  const startDrag = (event) => {
    const startedDrag = beginDragSelection(
      event,
      `startup:${item.group}`,
      startupState.selectedIds,
      item.id,
      startupState.selectionAnchor,
      (value) => { startupState.selectionAnchor = value; },
      startupState.items,
      applyChecked,
      (entry) => entry.id
    );
    if (!startedDrag && event.shiftKey) {
      renderStartupGroups();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection(`startup:${item.group}`, applyChecked));
  checkboxCell.appendChild(checkbox);

  const typeCell = document.createElement("td");
  typeCell.textContent = item.kind === "login_item" ? "登录项" : "后台项目";

  const impactCell = document.createElement("td");
  impactCell.textContent = item.impact_level;

  const noteCell = document.createElement("td");
  noteCell.textContent = item.impact_reason || "估计影响较小";

  tr.appendChild(checkboxCell);
  tr.appendChild(buildStartupNameCell(item));
  tr.appendChild(typeCell);
  tr.appendChild(impactCell);
  tr.appendChild(noteCell);

  tr.addEventListener("click", () => {
    startupState.currentId = item.id;
    markCurrentStartupRow();
    renderStartupDetail(item);
  });

  return tr;
}

function renderStartupGroups() {
  startupGroups.innerHTML = "";
  if (!startupState.items.length) {
    startupState.expandedGroups.clear();
    startupState.groupScrollTop.clear();
    startupGroups.innerHTML = '<div class="empty-block">扫描后，这里会按“登录项 / 后台项目”分组显示开机启动项。</div>';
    updateStartupSummary();
    renderStartupDetail(null);
    return;
  }

  const grouped = groupStartupItems();
  const hasSavedExpandedGroups = startupState.expandedGroups.size > 0;
  grouped.forEach((entry, index) => {
    const details = document.createElement("details");
    details.className = "group-card";
    details.dataset.group = entry.group;
    const containsCurrent = entry.items.some((item) => item.id === startupState.currentId);
    details.open = startupState.expandedGroups.has(entry.group) ||
      (!hasSavedExpandedGroups && (containsCurrent || index === 0));
    details.addEventListener("toggle", () => {
      if (details.open) startupState.expandedGroups.add(entry.group);
      else startupState.expandedGroups.delete(entry.group);
    });

    const summaryEl = document.createElement("summary");
    const title = document.createElement("span");
    title.textContent = entry.group;
    const meta = document.createElement("span");
    meta.className = "group-meta";
    meta.textContent = `${entry.items.length} 个项目 · 高影响 ${entry.highImpactCount} 个`;
    summaryEl.appendChild(title);
    summaryEl.appendChild(meta);
    details.appendChild(summaryEl);

    const body = document.createElement("div");
    body.className = "group-body";
    body.dataset.group = entry.group;
    body.addEventListener("scroll", () => {
      startupState.groupScrollTop.set(entry.group, body.scrollTop);
    }, { passive: true });

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>选择</th>
        <th>名称</th>
        <th>类型</th>
        <th>估计影响</th>
        <th>判断依据</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    entry.items.forEach((item) => tbody.appendChild(buildStartupGroupRow(item)));
    table.appendChild(tbody);
    body.appendChild(table);
    details.appendChild(body);
    startupGroups.appendChild(details);

    const savedScrollTop = startupState.groupScrollTop.get(entry.group);
    if (savedScrollTop) {
      body.scrollTop = savedScrollTop;
    }
  });

  updateStartupSummary();
  renderStartupDetail(ensureCurrentStartupItem());
  markCurrentStartupRow();
}

function buildStartupScanSummary(result) {
  const lines = [
    "开机启动项扫描摘要",
    "",
    `扫描到的启动项总数: ${result.total_count || 0}`,
    `其中高影响项目: ${result.high_impact_count || 0}`,
    "",
    "分组统计：",
  ];
  (result.groups || []).forEach((group) => {
    lines.push(`- ${group.name}: ${group.count || 0} 个，其中高影响 ${group.high_impact_count || 0} 个`);
  });
  if ((result.items || []).length) {
    lines.push("", "示例项目：");
    result.items.slice(0, 12).forEach((item) => {
      lines.push(`- [${item.group}] ${item.name} | 估计影响 ${item.impact_level}`);
    });
  }
  return lines.join("\n");
}

async function scanStartupItems() {
  try {
    setStartupBusy(true, "扫描中，请稍候...");
    startupSummary.textContent = "扫描开机启动项中，请稍候...";
    startupResultBox.textContent = "扫描开机启动项中，请稍候...\n\n我会区分登录项和后台项目，并给出估计影响。";
    const result = await api("/api/scan-startup-items", { groups: selectedStartupGroups() });
    startupState.items = result.items || [];
    startupState.selectedIds.clear();
    startupState.currentId = null;
    startupState.expandedGroups.clear();
    startupState.groupScrollTop.clear();
    startupState.selectionAnchor = null;
    startupSummary.textContent =
      `扫描完成。共发现 ${result.total_count || 0} 个启动项，其中高影响 ${result.high_impact_count || 0} 个。`;
    startupResultBox.textContent = buildStartupScanSummary(result);
    renderStartupGroups();
  } catch (error) {
    alert(error.message);
    startupSummary.textContent = "扫描开机启动项失败，请看错误提示。";
  } finally {
    setStartupBusy(false, "空闲");
  }
}

async function disableStartupSelection() {
  const items = startupState.items.filter((item) => startupState.selectedIds.has(item.id));
  if (!items.length) {
    alert("请先勾选至少一个启动项。");
    return;
  }
  if (!confirm(`即将关闭 ${items.length} 个开机启动项，是否继续？`)) return;
  try {
    setStartupBusy(true, "关闭启动项中，请稍候...");
    const result = await api("/api/disable-startup-items", { items });
    const successIds = new Set((result.results || []).filter((item) => item.success).map((item) => item.id));
    startupState.items = startupState.items.filter((item) => !successIds.has(item.id));
    startupState.selectedIds = new Set([...startupState.selectedIds].filter((id) => !successIds.has(id)));
    if (startupState.currentId && successIds.has(startupState.currentId)) {
      startupState.currentId = null;
    }
    const lines = [
      "关闭开机启动项结果",
      "",
      `成功: ${result.disabled_count || 0}`,
      `失败: ${result.failed_count || 0}`,
      "",
    ];
    (result.results || []).forEach((item) => {
      lines.push(`- ${item.name}: ${item.success ? "成功" : "失败"} | ${item.message}`);
    });
    startupResultBox.textContent = lines.join("\n");
    startupSummary.textContent =
      `关闭完成。成功 ${result.disabled_count || 0} 个，失败 ${result.failed_count || 0} 个。`;
    renderStartupGroups();
  } catch (error) {
    alert(error.message);
  } finally {
    setStartupBusy(false, "空闲");
  }
}

async function revealStartupItem() {
  const current = getCurrentStartupItem();
  if (!current || !current.action_path) {
    alert("当前启动项没有可定位的路径。");
    return;
  }
  try {
    setStartupBusy(true, "正在访达中定位启动项...");
    await api("/api/reveal-file", { path: current.action_path });
    startupSummary.textContent = `已在访达中显示：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setStartupBusy(false, "空闲");
  }
}

async function openStartupItem() {
  const current = getCurrentStartupItem();
  if (!current || !current.action_path) {
    alert("当前启动项没有可打开的路径。");
    return;
  }
  try {
    setStartupBusy(true, "正在尝试打开程序...");
    await api("/api/open-file", { path: current.action_path });
    startupSummary.textContent = `已尝试打开：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setStartupBusy(false, "空闲");
  }
}

function getCurrentMemoryItem() {
  if (!memoryState.currentId) return null;
  return memoryState.items.find((item) => item.id === memoryState.currentId) || null;
}

function ensureCurrentMemoryItem() {
  const current = getCurrentMemoryItem();
  if (current) return current;
  if (memoryState.items.length) {
    memoryState.currentId = memoryState.items[0].id;
    return memoryState.items[0];
  }
  memoryState.currentId = null;
  return null;
}

function renderMemoryDetail(item) {
  if (!item) {
    revealMemoryBtn.disabled = true;
    openMemoryBtn.disabled = true;
    memoryDetailBox.textContent = "扫描后，点击某个进程，就会在这里显示 PID、内存、CPU、风险说明和命令行。";
    return;
  }
  revealMemoryBtn.disabled = !item.app_path;
  openMemoryBtn.disabled = !item.app_path;
  const checked = memoryState.selectedIds.has(item.id) ? "已勾选" : "未勾选";
  memoryDetailBox.textContent = [
    `进程名: ${item.name}`,
    `应用家族: ${item.family}`,
    `PID: ${item.pid}`,
    `父进程 PID: ${item.ppid}`,
    `状态: ${checked}`,
    `内存占用: ${formatBytes(item.memory_bytes || 0)}`,
    `CPU 占用: ${Number(item.cpu_percent || 0).toFixed(1)}%`,
    `后台进程: ${item.is_background ? "是" : "否"}`,
    `风险等级: ${item.risk_level}`,
    `可结束: ${item.can_terminate ? "是" : "否"}`,
    `说明: ${item.recommendation}`,
    item.app_path ? `应用位置: ${item.app_path}` : "应用位置: 未解析到 .app",
    "",
    "命令行:",
    item.command,
  ].filter(Boolean).join("\n");
}

function updateMemorySummary() {
  const selectedItems = memoryState.items.filter((item) => memoryState.selectedIds.has(item.id));
  const selectedBytes = selectedItems.reduce((sum, item) => sum + Number(item.memory_bytes || 0), 0);
  const lowRiskCount = memoryState.items.filter((item) => item.risk_level === "低").length;
  memoryItemsSummary.textContent =
    `进程：${memoryState.items.length} 个；低风险 ${lowRiskCount} 个；` +
    `已勾选 ${selectedItems.length} 个，共 ${formatBytes(selectedBytes)}`;
}

function buildMemoryNameCell(item) {
  const cell = document.createElement("td");
  const strong = document.createElement("strong");
  strong.textContent = item.name;
  const lineBreak = document.createElement("br");
  const sub = document.createElement("span");
  sub.textContent = `PID ${item.pid} · ${item.family}`;
  cell.appendChild(strong);
  cell.appendChild(lineBreak);
  cell.appendChild(sub);
  return cell;
}

function buildMemoryRow(item) {
  const tr = document.createElement("tr");
  tr.dataset.id = item.id;
  if (memoryState.currentId === item.id) tr.classList.add("selected");

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = memoryState.selectedIds.has(item.id);
  checkbox.disabled = !item.can_terminate;
  checkbox.title = item.can_terminate ? "" : item.recommendation;
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    if (!item.can_terminate) return;
    if (checked) memoryState.selectedIds.add(item.id);
    else memoryState.selectedIds.delete(item.id);
    checkbox.checked = checked;
    updateMemorySummary();
    if (memoryState.currentId === item.id) renderMemoryDetail(item);
  };
  const startDrag = (event) => {
    if (checkbox.disabled) return;
    const startedDrag = beginDragSelection(
      event,
      "memory:all",
      memoryState.selectedIds,
      item.id,
      memoryState.selectionAnchor,
      (value) => { memoryState.selectionAnchor = value; },
      memoryState.items.filter((entry) => entry.can_terminate),
      applyChecked,
      (entry) => entry.id
    );
    if (!startedDrag && event.shiftKey) {
      renderMemoryTable();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection("memory:all", applyChecked));
  checkboxCell.appendChild(checkbox);

  const memoryCell = document.createElement("td");
  memoryCell.textContent = formatBytes(item.memory_bytes || 0);

  const cpuCell = document.createElement("td");
  cpuCell.textContent = `${Number(item.cpu_percent || 0).toFixed(1)}%`;

  const backgroundCell = document.createElement("td");
  backgroundCell.textContent = item.is_background ? "是" : "否";

  const riskCell = document.createElement("td");
  riskCell.textContent = item.risk_level;

  tr.appendChild(checkboxCell);
  tr.appendChild(buildMemoryNameCell(item));
  tr.appendChild(memoryCell);
  tr.appendChild(cpuCell);
  tr.appendChild(backgroundCell);
  tr.appendChild(riskCell);

  tr.addEventListener("click", () => {
    memoryState.currentId = item.id;
    renderMemoryTable();
  });

  return tr;
}

function renderMemoryTable() {
  memoryTableBody.innerHTML = "";
  if (!memoryState.items.length) {
    memoryTableBody.innerHTML = '<tr><td colspan="6" class="empty">扫描后，这里会显示当前用户中更值得你处理的高占用进程。</td></tr>';
    updateMemorySummary();
    renderMemoryDetail(null);
    return;
  }

  memoryState.items.forEach((item) => memoryTableBody.appendChild(buildMemoryRow(item)));
  updateMemorySummary();
  renderMemoryDetail(ensureCurrentMemoryItem());
}

function buildMemoryScanSummary(result) {
  const lines = [
    "内存管理扫描摘要",
    "",
    `当前用户进程总数: ${result.current_user_process_count || 0}`,
    `可管理候选进程: ${result.total_candidate_count || 0}`,
    `当前展示: ${result.visible_count || 0} 个`,
    `展示中的总内存占用: ${formatBytes(result.visible_memory_bytes || 0)}`,
    `低风险进程: ${result.low_risk_count || 0}`,
    `后台进程: ${result.background_count || 0}`,
    `高内存进程: ${result.high_memory_count || 0}`,
    "",
    "进程示例：",
  ];
  (result.items || []).slice(0, 12).forEach((item) => {
    lines.push(
      `- ${item.name} | ${formatBytes(item.memory_bytes || 0)} | CPU ${Number(item.cpu_percent || 0).toFixed(1)}% | ` +
      `${item.is_background ? "后台" : "前台"} | 风险 ${item.risk_level}`
    );
  });
  return lines.join("\n");
}

function buildMemoryTerminateSummary(result) {
  const lines = [
    "结束进程结果",
    "",
    `成功: ${result.terminated_count || 0}`,
    `失败: ${result.failed_count || 0}`,
    `估计释放内存: ${formatBytes(result.reclaimed_bytes_estimate || 0)}`,
    "",
  ];
  (result.results || []).forEach((item) => {
    lines.push(`- ${item.name} (PID ${item.pid}): ${item.success ? "成功" : "失败"} | ${item.message}`);
  });
  return lines.join("\n");
}

async function scanMemoryProcesses() {
  try {
    setMemoryBusy(true, "扫描中，请稍候...");
    memorySummary.textContent = "扫描内存进程中，请稍候...";
    memoryResultBox.textContent = "扫描内存进程中，请稍候...\n\n我会优先列出当前用户中更值得你人工判断的高占用进程。";
    const result = await api("/api/scan-memory-processes", { limit: 20 });
    memoryState.items = result.items || [];
    memoryState.selectedIds.clear();
    memoryState.currentId = null;
    memoryState.selectionAnchor = null;
    memorySummary.textContent =
      `扫描完成。当前展示 ${result.visible_count || 0} 个高占用进程，合计 ${formatBytes(result.visible_memory_bytes || 0)}。`;
    memoryResultBox.textContent = buildMemoryScanSummary(result);
    renderMemoryTable();
  } catch (error) {
    alert(error.message);
    memorySummary.textContent = "扫描内存进程失败，请看错误提示。";
  } finally {
    setMemoryBusy(false, "空闲");
  }
}

async function terminateMemorySelection() {
  const items = memoryState.items.filter((item) => memoryState.selectedIds.has(item.id));
  if (!items.length) {
    alert("请先勾选至少一个进程。");
    return;
  }
  if (!confirm(`即将结束 ${items.length} 个你勾选的进程，是否继续？`)) return;
  try {
    setMemoryBusy(true, "结束进程中，请稍候...");
    const result = await api("/api/terminate-processes", { items });
    const successIds = new Set((result.results || []).filter((item) => item.success).map((item) => `process::${item.pid}`));
    memoryState.items = memoryState.items.filter((item) => !successIds.has(item.id));
    memoryState.selectedIds = new Set([...memoryState.selectedIds].filter((id) => !successIds.has(id)));
    if (memoryState.currentId && successIds.has(memoryState.currentId)) {
      memoryState.currentId = null;
    }
    memorySummary.textContent =
      `结束完成。成功 ${result.terminated_count || 0} 个，失败 ${result.failed_count || 0} 个，估计释放 ${formatBytes(result.reclaimed_bytes_estimate || 0)}。`;
    memoryResultBox.textContent = buildMemoryTerminateSummary(result);
    renderMemoryTable();
  } catch (error) {
    alert(error.message);
  } finally {
    setMemoryBusy(false, "空闲");
  }
}

async function revealMemoryItem() {
  const current = getCurrentMemoryItem();
  if (!current || !current.app_path) {
    alert("当前进程没有可定位的应用路径。");
    return;
  }
  try {
    setMemoryBusy(true, "正在访达中定位应用...");
    await api("/api/reveal-file", { path: current.app_path });
    memorySummary.textContent = `已在访达中显示：${current.family}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setMemoryBusy(false, "空闲");
  }
}

async function openMemoryItem() {
  const current = getCurrentMemoryItem();
  if (!current || !current.app_path) {
    alert("当前进程没有可打开的应用路径。");
    return;
  }
  try {
    setMemoryBusy(true, "正在尝试打开应用...");
    await api("/api/open-file", { path: current.app_path });
    memorySummary.textContent = `已尝试打开：${current.family}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setMemoryBusy(false, "空闲");
  }
}

function imageItems(view) {
  if (view === "screenshots") return imageState.screenshots;
  if (view === "downloads") return imageState.downloads;
  if (view === "similar") return imageState.similar;
  if (view === "duplicates") return imageState.duplicates;
  if (view === "largeOld") return imageState.largeOld;
  return [];
}

function imageSelectedSet(view) {
  if (view === "screenshots") return imageState.screenshotSelectedPaths;
  if (view === "downloads") return imageState.downloadSelectedPaths;
  if (view === "similar") return imageState.similarSelectedPaths;
  if (view === "duplicates") return imageState.duplicateSelectedPaths;
  if (view === "largeOld") return imageState.largeOldSelectedPaths;
  return new Set();
}

function getCurrentImageItem() {
  if (!imageState.currentView || !imageState.currentPath) return null;
  return imageItems(imageState.currentView).find((item) => item.path === imageState.currentPath) || null;
}

function ensureCurrentImageItem() {
  const current = getCurrentImageItem();
  if (current) return current;
  const order = ["screenshots", "downloads", "similar", "duplicates", "largeOld"];
  for (const view of order) {
    const items = imageItems(view);
    if (items.length) {
      imageState.currentView = view;
      imageState.currentPath = items[0].path;
      return items[0];
    }
  }
  imageState.currentView = null;
  imageState.currentPath = null;
  return null;
}

function renderImagePreview(item) {
  if (!item) {
    imagePreview.classList.add("hidden");
    imagePreview.removeAttribute("src");
    imagePreviewEmpty.classList.remove("hidden");
    return;
  }
  imagePreview.classList.remove("hidden");
  imagePreviewEmpty.classList.add("hidden");
  imagePreview.src = `/api/image-preview?path=${encodeURIComponent(item.path)}`;
}

function renderImageDetail(item, view) {
  if (!item) {
    revealImageBtn.disabled = true;
    openImageBtn.disabled = true;
    renderImagePreview(null);
    imageDetailBox.textContent = "扫描后，点击某张图片，就会在这里显示路径、大小、分辨率和分类说明。";
    return;
  }
  revealImageBtn.disabled = false;
  openImageBtn.disabled = false;
  renderImagePreview(item);
  const checked = imageSelectedSet(view).has(item.path) ? "已勾选" : "未勾选";
  imageDetailBox.textContent = [
    `分类: ${item.category}`,
    `文件名: ${item.name}`,
    `来源目录: ${item.root_name || "未知"}`,
    `状态: ${checked}`,
    `大小: ${formatBytes(item.size_bytes || 0)}`,
    `分辨率: ${item.dimensions || "未知"}`,
    `格式: ${item.suffix ? item.suffix.toUpperCase() : "未知"}`,
    `使用情况: ${formatAge(item.age_days)}`,
    item.group_label ? `组别: ${item.group_label}` : "",
    `说明: ${item.reason || "可手动确认是否需要"}`,
    "",
    "完整路径:",
    item.path,
  ].filter(Boolean).join("\n");
}

function updateImageSectionSummary(items, selectedPaths, target, label) {
  const totalBytes = items.reduce((sum, item) => sum + Number(item.size_bytes || 0), 0);
  const selectedItems = items.filter((item) => selectedPaths.has(item.path));
  const selectedBytes = selectedItems.reduce((sum, item) => sum + Number(item.size_bytes || 0), 0);
  target.textContent =
    `${label}：${items.length} 张，总大小 ${formatBytes(totalBytes)}；` +
    `已勾选 ${selectedItems.length} 张，共 ${formatBytes(selectedBytes)}`;
}

function buildImageRow(item, view, lastColumnText) {
  const tr = document.createElement("tr");
  if (imageState.currentView === view && imageState.currentPath === item.path) {
    tr.classList.add("selected");
  }

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = imageSelectedSet(view).has(item.path);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    const selectedSet = imageSelectedSet(view);
    if (checked) selectedSet.add(item.path);
    else selectedSet.delete(item.path);
    checkbox.checked = checked;
    if (view === "screenshots") updateImageSectionSummary(imageState.screenshots, imageState.screenshotSelectedPaths, screenshotSummary, "截图");
    if (view === "downloads") updateImageSectionSummary(imageState.downloads, imageState.downloadSelectedPaths, downloadedImageSummary, "下载图片");
    if (view === "similar") updateImageSectionSummary(imageState.similar, imageState.similarSelectedPaths, similarImageSummary, "相似图片");
    if (view === "duplicates") updateImageSectionSummary(imageState.duplicates, imageState.duplicateSelectedPaths, duplicateImageSummary, "重复图片");
    if (view === "largeOld") updateImageSectionSummary(imageState.largeOld, imageState.largeOldSelectedPaths, largeOldImageSummary, "大图 / 旧图");
    if (imageState.currentView === view && imageState.currentPath === item.path) {
      renderImageDetail(item, view);
    }
  };
  const startDrag = (event) => {
    const selectedSet = imageSelectedSet(view);
    const startedDrag = beginDragSelection(
      event,
      `images:${view}`,
      selectedSet,
      item.path,
      imageState.selectionAnchors[view],
      (value) => { imageState.selectionAnchors[view] = value; },
      imageItems(view),
      applyChecked
    );
    if (!startedDrag && event.shiftKey) {
      renderImageTables();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection(`images:${view}`, applyChecked));
  checkboxCell.appendChild(checkbox);

  const sizeCell = document.createElement("td");
  sizeCell.textContent = formatBytes(item.size_bytes || 0);

  const lastCell = document.createElement("td");
  lastCell.textContent = lastColumnText;

  tr.appendChild(checkboxCell);
  tr.appendChild(buildNameCell({ name: item.name, path: item.path }));
  tr.appendChild(sizeCell);
  tr.appendChild(lastCell);

  tr.addEventListener("click", () => {
    imageState.currentView = view;
    imageState.currentPath = item.path;
    renderImageTables();
  });

  tr.addEventListener("dblclick", async () => {
    imageState.currentView = view;
    imageState.currentPath = item.path;
    renderImageTables();
    await revealImageItem();
  });

  return tr;
}

function renderImageTable(body, items, view, emptyText, labelBuilder) {
  body.innerHTML = "";
  if (!items.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty";
    cell.textContent = emptyText;
    row.appendChild(cell);
    body.appendChild(row);
    return;
  }
  items.forEach((item) => body.appendChild(buildImageRow(item, view, labelBuilder(item))));
}

function renderImageTables() {
  renderImageTable(
    screenshotTableBody,
    imageState.screenshots,
    "screenshots",
    "扫描后，这里会优先显示截图。",
    (item) => item.reason || formatAge(item.age_days)
  );
  renderImageTable(
    downloadedImagesTableBody,
    imageState.downloads,
    "downloads",
    "扫描后，这里会显示 Downloads 目录里的图片。",
    (item) => item.reason || formatAge(item.age_days)
  );
  renderImageTable(
    similarImagesTableBody,
    imageState.similar,
    "similar",
    "扫描后，这里会显示第一版启发式判断出的相似图片。",
    (item) => item.group_label || item.reason || "相似图片"
  );
  renderImageTable(
    duplicateImagesTableBody,
    imageState.duplicates,
    "duplicates",
    "扫描后，这里会显示内容完全一致的重复图片。",
    (item) => item.group_label || "完全重复"
  );
  renderImageTable(
    largeOldImagesTableBody,
    imageState.largeOld,
    "largeOld",
    "扫描后，这里会显示大图和长期未使用图片。",
    (item) => item.reason || formatAge(item.age_days)
  );

  updateImageSectionSummary(imageState.screenshots, imageState.screenshotSelectedPaths, screenshotSummary, "截图");
  updateImageSectionSummary(imageState.downloads, imageState.downloadSelectedPaths, downloadedImageSummary, "下载图片");
  updateImageSectionSummary(imageState.similar, imageState.similarSelectedPaths, similarImageSummary, "相似图片");
  updateImageSectionSummary(imageState.duplicates, imageState.duplicateSelectedPaths, duplicateImageSummary, "重复图片");
  updateImageSectionSummary(imageState.largeOld, imageState.largeOldSelectedPaths, largeOldImageSummary, "大图 / 旧图");
  renderImageDetail(ensureCurrentImageItem(), imageState.currentView);
}

function buildImageScanSummary(result) {
  const lines = [
    "图片管理扫描摘要",
    "",
    `总图片数: ${result.scanned_image_count || 0}`,
    `总空间: ${formatBytes(result.total_bytes || 0)}`,
    result.scan_truncated ? "提示: 图片过多，本次扫描做了上限截断。" : "提示: 本次扫描未截断。",
    "",
    "扫描目录：",
  ];
  (result.roots || []).forEach((root) => {
    lines.push(`- ${root.name}: ${root.image_count || 0} 张，${formatBytes(root.total_bytes || 0)}`);
  });
  lines.push(
    "",
    `截图: ${result.screenshots?.total_count || 0} 张`,
    `下载图片: ${result.downloads?.total_count || 0} 张`,
    `相似图片: ${result.similar?.group_count || 0} 组，共 ${result.similar?.total_count || 0} 张`,
    `完全重复图片: ${result.duplicates?.group_count || 0} 组，共 ${result.duplicates?.total_count || 0} 张`,
    `大图 / 旧图: ${result.large_old?.total_count || 0} 张`
  );
  return lines.join("\n");
}

async function scanImages() {
  try {
    setImageBusy(true, "扫描中，请稍候...");
    imageSummary.textContent = "扫描图片中，请稍候...";
    imageResultBox.textContent = "扫描图片中，请稍候...\n\n我会先把截图、下载图片、相似图片、重复图片和大图旧图拆开。";
    const result = await api("/api/scan-images", { roots: selectedImageRoots() });

    imageState.screenshots = result.screenshots?.items || [];
    imageState.downloads = result.downloads?.items || [];
    imageState.similar = result.similar?.items || [];
    imageState.duplicates = result.duplicates?.items || [];
    imageState.largeOld = result.large_old?.items || [];
    imageState.screenshotSelectedPaths.clear();
    imageState.downloadSelectedPaths.clear();
    imageState.similarSelectedPaths.clear();
    imageState.duplicateSelectedPaths.clear();
    imageState.largeOldSelectedPaths.clear();
    imageState.currentView = null;
    imageState.currentPath = null;
    imageState.selectionAnchors = { screenshots: null, downloads: null, similar: null, duplicates: null, largeOld: null };

    imageSummary.textContent =
      `扫描完成。截图 ${result.screenshots?.total_count || 0} 张；下载图片 ${result.downloads?.total_count || 0} 张；` +
      `相似图片 ${result.similar?.group_count || 0} 组；重复图片 ${result.duplicates?.group_count || 0} 组。`;
    imageResultBox.textContent = buildImageScanSummary(result);
    renderImageTables();
  } catch (error) {
    alert(error.message);
    imageSummary.textContent = "扫描图片失败，请看错误提示。";
  } finally {
    setImageBusy(false, "空闲");
  }
}

async function previewImageSelection(view, title) {
  const paths = [...imageSelectedSet(view)];
  if (!paths.length) {
    alert("请先勾选至少一张图片。");
    return;
  }
  try {
    setImageBusy(true, `${title}中，请稍候...`);
    const result = await api("/api/clean-files", { paths, dry_run: true });
    imageResultBox.textContent = buildCleanSummary(result, title);
    const item = (result.results || [])[0] || {};
    imageSummary.textContent =
      `${title}完成。涉及 ${item.deleted_files || 0} 张图片，预计释放 ${formatBytes(item.reclaimed_bytes || 0)}。`;
  } catch (error) {
    alert(error.message);
  } finally {
    setImageBusy(false, "空闲");
  }
}

async function deleteImageSelection(view, title) {
  const paths = [...imageSelectedSet(view)];
  if (!paths.length) {
    alert("请先勾选至少一张图片。");
    return;
  }
  if (!confirm(`即将删除 ${paths.length} 张你勾选的图片，是否继续？`)) return;
  try {
    setImageBusy(true, `${title}中，请稍候...`);
    const result = await api("/api/clean-files", { paths, dry_run: false });
    imageResultBox.textContent = buildCleanSummary(result, title);
    const item = (result.results || [])[0] || {};
    if (item.dry_run === false) {
      const deleted = new Set(item.deleted_paths || []);
      imageState.screenshots = imageState.screenshots.filter((entry) => !deleted.has(entry.path));
      imageState.downloads = imageState.downloads.filter((entry) => !deleted.has(entry.path));
      imageState.similar = imageState.similar.filter((entry) => !deleted.has(entry.path));
      imageState.duplicates = imageState.duplicates.filter((entry) => !deleted.has(entry.path));
      imageState.largeOld = imageState.largeOld.filter((entry) => !deleted.has(entry.path));
      imageState.screenshotSelectedPaths = new Set([...imageState.screenshotSelectedPaths].filter((path) => !deleted.has(path)));
      imageState.downloadSelectedPaths = new Set([...imageState.downloadSelectedPaths].filter((path) => !deleted.has(path)));
      imageState.similarSelectedPaths = new Set([...imageState.similarSelectedPaths].filter((path) => !deleted.has(path)));
      imageState.duplicateSelectedPaths = new Set([...imageState.duplicateSelectedPaths].filter((path) => !deleted.has(path)));
      imageState.largeOldSelectedPaths = new Set([...imageState.largeOldSelectedPaths].filter((path) => !deleted.has(path)));
      if (imageState.currentPath && deleted.has(imageState.currentPath)) {
        imageState.currentPath = null;
        imageState.currentView = null;
      }
      const skippedCount = (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0);
      imageSummary.textContent = `${title}完成，实际删除 ${item.deleted_files || 0} 张，跳过 ${skippedCount} 张。`;
      renderImageTables();
    } else {
      imageSummary.textContent = "后端返回的是预演结果，没有真实删除。";
    }
  } catch (error) {
    alert(error.message);
  } finally {
    setImageBusy(false, "空闲");
  }
}

async function revealImageItem() {
  const current = getCurrentImageItem();
  if (!current) {
    alert("请先选择一张图片。");
    return;
  }
  try {
    setImageBusy(true, "正在访达中定位图片...");
    await api("/api/reveal-file", { path: current.path });
    imageSummary.textContent = `已在访达中显示：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setImageBusy(false, "空闲");
  }
}

async function openImageItem() {
  const current = getCurrentImageItem();
  if (!current) {
    alert("请先选择一张图片。");
    return;
  }
  try {
    setImageBusy(true, "正在尝试打开图片...");
    await api("/api/open-file", { path: current.path });
    imageSummary.textContent = `已尝试打开：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setImageBusy(false, "空闲");
  }
}

function getCurrentDiskItem() {
  if (!diskState.currentPath) return null;
  return diskState.largeFiles.find((item) => item.path === diskState.currentPath) || null;
}

function ensureCurrentDiskItem() {
  const current = getCurrentDiskItem();
  if (current) return current;
  if (diskState.largeFiles.length) {
    diskState.currentPath = diskState.largeFiles[0].path;
    return diskState.largeFiles[0];
  }
  diskState.currentPath = null;
  return null;
}

function renderDiskDetail(item) {
  if (!item) {
    revealDiskBtn.disabled = true;
    openDiskBtn.disabled = true;
    diskDetailBox.textContent = "扫描后，点击某个大文件，就会在这里显示路径、来源目录和大小。";
    return;
  }
  revealDiskBtn.disabled = false;
  openDiskBtn.disabled = false;
  const checked = diskState.selectedPaths.has(item.path) ? "已勾选" : "未勾选";
  diskDetailBox.textContent = [
    `文件名: ${item.name}`,
    `来源目录: ${item.source_root}`,
    `状态: ${checked}`,
    `大小: ${formatBytes(item.size_bytes || 0)}`,
    `项目类型: 文件`,
    "",
    "完整路径:",
    item.path,
  ].join("\n");
}

function updateDiskSummary() {
  const selectedItems = diskState.largeFiles.filter((item) => diskState.selectedPaths.has(item.path));
  const selectedBytes = selectedItems.reduce((sum, item) => sum + Number(item.size_bytes || 0), 0);
  diskLargeFilesSummary.textContent =
    `大文件：${diskState.largeFiles.length} 个；已勾选 ${selectedItems.length} 个，共 ${formatBytes(selectedBytes)}`;
  diskRootsSummary.textContent =
    `根目录：${diskState.roots.length} 个，总空间 ${formatBytes(diskState.roots.reduce((sum, item) => sum + Number(item.total_bytes || 0), 0))}`;
}

function renderDiskRoots() {
  diskRootsGroups.innerHTML = "";
  if (!diskState.roots.length) {
    diskState.expandedGroups.clear();
    diskState.groupScrollTop.clear();
    diskRootsGroups.innerHTML = '<div class="empty-block">扫描后，这里会显示 Desktop、Downloads、Documents、Library 的占用概览和大子目录。</div>';
    updateDiskSummary();
    return;
  }

  const hasSavedExpandedGroups = diskState.expandedGroups.size > 0;
  diskState.roots.forEach((root, index) => {
    const details = document.createElement("details");
    details.className = "group-card";
    details.dataset.group = root.key;
    details.open = diskState.expandedGroups.has(root.key) || (!hasSavedExpandedGroups && index === 0);
    details.addEventListener("toggle", () => {
      if (details.open) diskState.expandedGroups.add(root.key);
      else diskState.expandedGroups.delete(root.key);
    });

    const summaryEl = document.createElement("summary");
    const title = document.createElement("span");
    title.textContent = root.name;
    const meta = document.createElement("span");
    meta.className = "group-meta";
    meta.textContent = `${formatBytes(root.total_bytes || 0)} · ${root.file_count || 0} 个文件`;
    summaryEl.appendChild(title);
    summaryEl.appendChild(meta);
    details.appendChild(summaryEl);

    const body = document.createElement("div");
    body.className = "group-body";
    body.dataset.group = root.key;
    body.addEventListener("scroll", () => {
      diskState.groupScrollTop.set(root.key, body.scrollTop);
    }, { passive: true });

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>名称</th>
        <th>大小</th>
        <th>类型</th>
      </tr>
    `;
    table.appendChild(thead);
    const tbody = document.createElement("tbody");
    (root.children || []).forEach((child) => {
      const tr = document.createElement("tr");
      const nameCell = buildNameCell({ name: child.name, path: child.path });
      const sizeCell = document.createElement("td");
      sizeCell.textContent = formatBytes(child.size_bytes || 0);
      const typeCell = document.createElement("td");
      typeCell.textContent = child.kind;
      tr.appendChild(nameCell);
      tr.appendChild(sizeCell);
      tr.appendChild(typeCell);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    body.appendChild(table);
    details.appendChild(body);
    diskRootsGroups.appendChild(details);

    const savedScrollTop = diskState.groupScrollTop.get(root.key);
    if (savedScrollTop) body.scrollTop = savedScrollTop;
  });

  updateDiskSummary();
}

function buildDiskLargeFileRow(item) {
  const tr = document.createElement("tr");
  if (diskState.currentPath === item.path) tr.classList.add("selected");

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = diskState.selectedPaths.has(item.path);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    if (checked) diskState.selectedPaths.add(item.path);
    else diskState.selectedPaths.delete(item.path);
    checkbox.checked = checked;
    updateDiskSummary();
    if (diskState.currentPath === item.path) renderDiskDetail(item);
  };
  const startDrag = (event) => {
    const startedDrag = beginDragSelection(
      event,
      "disk:large",
      diskState.selectedPaths,
      item.path,
      diskState.selectionAnchor,
      (value) => { diskState.selectionAnchor = value; },
      diskState.largeFiles,
      applyChecked
    );
    if (!startedDrag && event.shiftKey) {
      renderDiskLargeFiles();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection("disk:large", applyChecked));
  checkboxCell.appendChild(checkbox);

  const sizeCell = document.createElement("td");
  sizeCell.textContent = formatBytes(item.size_bytes || 0);

  const sourceCell = document.createElement("td");
  sourceCell.textContent = item.source_root || "未知";

  tr.appendChild(checkboxCell);
  tr.appendChild(buildNameCell({ name: item.name, path: item.path }));
  tr.appendChild(sizeCell);
  tr.appendChild(sourceCell);

  tr.addEventListener("click", () => {
    diskState.currentPath = item.path;
    renderDiskLargeFiles();
  });

  tr.addEventListener("dblclick", async () => {
    diskState.currentPath = item.path;
    renderDiskLargeFiles();
    await revealDiskItem();
  });
  return tr;
}

function renderDiskLargeFiles() {
  diskLargeFilesTableBody.innerHTML = "";
  if (!diskState.largeFiles.length) {
    diskLargeFilesTableBody.innerHTML = '<tr><td colspan="4" class="empty">扫描后，这里会显示所选目录里最占空间的大文件。</td></tr>';
    updateDiskSummary();
    renderDiskDetail(null);
    return;
  }
  diskState.largeFiles.forEach((item) => diskLargeFilesTableBody.appendChild(buildDiskLargeFileRow(item)));
  updateDiskSummary();
  renderDiskDetail(ensureCurrentDiskItem());
}

function buildDiskScanSummary(result) {
  const lines = [
    "磁盘空间扫描摘要",
    "",
    `扫描根目录数: ${result.root_count || 0}`,
    `统计到的文件数: ${result.total_file_count || 0}`,
    `总空间: ${formatBytes(result.total_bytes || 0)}`,
    "",
    "根目录概览：",
  ];
  (result.roots || []).forEach((root) => {
    lines.push(`- ${root.name}: ${formatBytes(root.total_bytes || 0)}，${root.file_count || 0} 个文件`);
    (root.children || []).slice(0, 5).forEach((child) => {
      lines.push(`  · ${child.name} | ${formatBytes(child.size_bytes || 0)} | ${child.kind}`);
    });
  });
  if ((result.large_files || []).length) {
    lines.push("", "占空间的大文件：");
    result.large_files.slice(0, 15).forEach((file) => {
      lines.push(`- [${file.source_root}] ${file.path} | ${formatBytes(file.size_bytes || 0)}`);
    });
  }
  return lines.join("\n");
}

async function scanDiskUsage() {
  try {
    setDiskBusy(true, "扫描中，请稍候...");
    diskSummary.textContent = "扫描磁盘空间中，请稍候...";
    diskResultBox.textContent = "扫描磁盘空间中，请稍候...\n\n我会先统计根目录占用，再列出最占空间的大文件。";
    const result = await api("/api/scan-disk-usage", { roots: selectedDiskRoots() });
    diskState.roots = result.roots || [];
    diskState.largeFiles = result.large_files || [];
    diskState.selectedPaths.clear();
    diskState.currentPath = null;
    diskState.expandedGroups.clear();
    diskState.groupScrollTop.clear();
    diskState.selectionAnchor = null;
    diskSummary.textContent =
      `扫描完成。共统计 ${result.root_count || 0} 个根目录，总空间 ${formatBytes(result.total_bytes || 0)}。`;
    diskResultBox.textContent = buildDiskScanSummary(result);
    renderDiskRoots();
    renderDiskLargeFiles();
  } catch (error) {
    alert(error.message);
    diskSummary.textContent = "扫描磁盘空间失败，请看错误提示。";
  } finally {
    setDiskBusy(false, "空闲");
  }
}

async function previewDiskLargeFiles() {
  const paths = [...diskState.selectedPaths];
  if (!paths.length) {
    alert("请先勾选至少一个大文件。");
    return;
  }
  try {
    setDiskBusy(true, "预演大文件中，请稍候...");
    const result = await api("/api/clean-files", { paths, dry_run: true });
    diskResultBox.textContent = buildCleanSummary(result, "预演大文件");
    const item = (result.results || [])[0] || {};
    diskSummary.textContent =
      `预演大文件完成。涉及 ${item.deleted_files || 0} 个文件，预计释放 ${formatBytes(item.reclaimed_bytes || 0)}。`;
  } catch (error) {
    alert(error.message);
  } finally {
    setDiskBusy(false, "空闲");
  }
}

async function deleteDiskLargeFiles() {
  const paths = [...diskState.selectedPaths];
  if (!paths.length) {
    alert("请先勾选至少一个大文件。");
    return;
  }
  if (!confirm(`即将删除 ${paths.length} 个你勾选的大文件，是否继续？`)) return;
  try {
    setDiskBusy(true, "删除大文件中，请稍候...");
    const result = await api("/api/clean-files", { paths, dry_run: false });
    diskResultBox.textContent = buildCleanSummary(result, "删除大文件");
    const item = (result.results || [])[0] || {};
    if (item.dry_run === false) {
      const deleted = new Set(item.deleted_paths || []);
      diskState.largeFiles = diskState.largeFiles.filter((entry) => !deleted.has(entry.path));
      diskState.selectedPaths = new Set([...diskState.selectedPaths].filter((path) => !deleted.has(path)));
      if (diskState.currentPath && deleted.has(diskState.currentPath)) {
        diskState.currentPath = null;
      }
      const skippedCount = (item.skipped_paths || []).length + Number(item.skipped_paths_truncated || 0);
      diskSummary.textContent = `删除大文件完成，实际删除 ${item.deleted_files || 0} 个，跳过 ${skippedCount} 个。`;
      renderDiskLargeFiles();
    } else {
      diskSummary.textContent = "后端返回的是预演结果，没有真实删除。";
    }
  } catch (error) {
    alert(error.message);
  } finally {
    setDiskBusy(false, "空闲");
  }
}

async function revealDiskItem() {
  const current = getCurrentDiskItem();
  if (!current) {
    alert("请先选择一个大文件。");
    return;
  }
  try {
    setDiskBusy(true, "正在访达中定位大文件...");
    await api("/api/reveal-file", { path: current.path });
    diskSummary.textContent = `已在访达中显示：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setDiskBusy(false, "空闲");
  }
}

async function openDiskItem() {
  const current = getCurrentDiskItem();
  if (!current) {
    alert("请先选择一个大文件。");
    return;
  }
  try {
    setDiskBusy(true, "正在尝试打开目标...");
    await api("/api/open-file", { path: current.path });
    diskSummary.textContent = `已尝试打开：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setDiskBusy(false, "空闲");
  }
}

function getCurrentApplicationItem() {
  if (!applicationState.currentPath) return null;
  return applicationState.items.find((item) => item.path === applicationState.currentPath) || null;
}

function ensureCurrentApplicationItem() {
  const current = getCurrentApplicationItem();
  if (current) return current;
  if (applicationState.items.length) {
    applicationState.currentPath = applicationState.items[0].path;
    return applicationState.items[0];
  }
  applicationState.currentPath = null;
  return null;
}

function markCurrentApplicationRow() {
  applicationGroups.querySelectorAll("tbody tr[data-path]").forEach((row) => {
    row.classList.toggle("selected", row.dataset.path === applicationState.currentPath);
  });
}

function renderApplicationDetail(item) {
  if (!item) {
    revealApplicationBtn.disabled = true;
    openApplicationBtn.disabled = true;
    applicationDetailBox.textContent = "扫描后，点击某个残留项目，就会在这里显示它的路径、风险等级和判断依据。";
    return;
  }

  revealApplicationBtn.disabled = false;
  openApplicationBtn.disabled = false;
  const checked = applicationState.selectedPaths.has(item.path) ? "已勾选" : "未勾选";
  applicationDetailBox.textContent = [
    `疑似所属应用: ${item.group}`,
    `名称: ${item.name}`,
    `标识符: ${item.identifier}`,
    `目录类型: ${item.location_type}`,
    `风险等级: ${item.risk_level}`,
    `状态: ${checked}`,
    `项目类型: ${item.is_directory ? "目录" : "文件"}`,
    `大小: ${formatBytes(item.size_bytes || 0)}`,
    `判断依据: ${item.reason}`,
    `目录说明: ${item.location_description}`,
    "",
    "完整路径:",
    item.path,
  ].join("\n");
}

function updateApplicationSummary() {
  const selectedItems = applicationState.items.filter((item) => applicationState.selectedPaths.has(item.path));
  const selectedBytes = selectedItems.reduce((sum, item) => sum + Number(item.size_bytes || 0), 0);
  const highRiskCount = applicationState.items.filter((item) => item.risk_level === "高").length;
  applicationItemsSummary.textContent =
    `应用残留：${applicationState.items.length} 个；高风险 ${highRiskCount} 个；` +
    `已勾选 ${selectedItems.length} 个，共 ${formatBytes(selectedBytes)}`;
}

function groupApplicationItems() {
  const grouped = new Map();
  applicationState.items.forEach((item) => {
    if (!grouped.has(item.group)) grouped.set(item.group, []);
    grouped.get(item.group).push(item);
  });
  return [...grouped.entries()].map(([group, items]) => {
    items.sort((left, right) => {
      const leftRisk = { "高": 0, "中": 1, "低": 2 }[left.risk_level] ?? 3;
      const rightRisk = { "高": 0, "中": 1, "低": 2 }[right.risk_level] ?? 3;
      return leftRisk - rightRisk || Number(right.size_bytes || 0) - Number(left.size_bytes || 0);
    });
    return {
      group,
      items,
      totalBytes: items.reduce((sum, item) => sum + Number(item.size_bytes || 0), 0),
      highRiskCount: items.filter((item) => item.risk_level === "高").length,
    };
  }).sort((left, right) => right.totalBytes - left.totalBytes || left.group.localeCompare(right.group));
}

function buildApplicationNameCell(item) {
  const cell = document.createElement("td");
  const strong = document.createElement("strong");
  strong.textContent = item.name;
  const lineBreak = document.createElement("br");
  const sub = document.createElement("span");
  sub.textContent = item.path;
  cell.appendChild(strong);
  cell.appendChild(lineBreak);
  cell.appendChild(sub);
  return cell;
}

function buildApplicationRow(item) {
  const tr = document.createElement("tr");
  tr.dataset.path = item.path;
  if (applicationState.currentPath === item.path) tr.classList.add("selected");

  const checkboxCell = document.createElement("td");
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = applicationState.selectedPaths.has(item.path);
  checkbox.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
  });
  const applyChecked = (checked) => {
    if (checked) applicationState.selectedPaths.add(item.path);
    else applicationState.selectedPaths.delete(item.path);
    checkbox.checked = checked;
    updateApplicationSummary();
    if (applicationState.currentPath === item.path) {
      renderApplicationDetail(item);
    }
  };
  const startDrag = (event) => {
    const startedDrag = beginDragSelection(
      event,
      `applications:${item.group}`,
      applicationState.selectedPaths,
      item.path,
      applicationState.selectionAnchor,
      (value) => { applicationState.selectionAnchor = value; },
      applicationState.items,
      applyChecked
    );
    if (!startedDrag && event.shiftKey) {
      renderApplicationGroups();
    }
  };
  checkbox.addEventListener("mousedown", startDrag);
  checkboxCell.addEventListener("mousedown", startDrag);
  tr.addEventListener("mouseenter", () => continueDragSelection(`applications:${item.group}`, applyChecked));
  checkboxCell.appendChild(checkbox);

  const sizeCell = document.createElement("td");
  sizeCell.textContent = formatBytes(item.size_bytes || 0);

  const locationCell = document.createElement("td");
  locationCell.textContent = item.location_type;

  const riskCell = document.createElement("td");
  riskCell.textContent = item.risk_level;

  const reasonCell = document.createElement("td");
  reasonCell.textContent = item.reason;

  tr.appendChild(checkboxCell);
  tr.appendChild(buildApplicationNameCell(item));
  tr.appendChild(sizeCell);
  tr.appendChild(locationCell);
  tr.appendChild(riskCell);
  tr.appendChild(reasonCell);

  tr.addEventListener("click", () => {
    applicationState.currentPath = item.path;
    markCurrentApplicationRow();
    renderApplicationDetail(item);
  });

  tr.addEventListener("dblclick", async () => {
    applicationState.currentPath = item.path;
    markCurrentApplicationRow();
    renderApplicationDetail(item);
    await revealApplicationItem();
  });

  return tr;
}

function renderApplicationGroups() {
  applicationGroups.innerHTML = "";
  if (!applicationState.items.length) {
    applicationState.expandedGroups.clear();
    applicationState.groupScrollTop.clear();
    applicationGroups.innerHTML = '<div class="empty-block">扫描后，这里会按应用分组显示疑似残留文件。</div>';
    updateApplicationSummary();
    renderApplicationDetail(null);
    return;
  }

  const grouped = groupApplicationItems();
  const hasSavedExpandedGroups = applicationState.expandedGroups.size > 0;

  grouped.forEach((entry, index) => {
    const details = document.createElement("details");
    details.className = "group-card";
    details.dataset.group = entry.group;
    const containsCurrent = entry.items.some((item) => item.path === applicationState.currentPath);
    details.open = applicationState.expandedGroups.has(entry.group) ||
      (!hasSavedExpandedGroups && (containsCurrent || index === 0));
    details.addEventListener("toggle", () => {
      if (details.open) applicationState.expandedGroups.add(entry.group);
      else applicationState.expandedGroups.delete(entry.group);
    });

    const summaryEl = document.createElement("summary");
    const title = document.createElement("span");
    title.textContent = entry.group;
    const meta = document.createElement("span");
    meta.className = "group-meta";
    meta.textContent = `${entry.items.length} 个项目 · ${formatBytes(entry.totalBytes)} · 高风险 ${entry.highRiskCount} 个`;
    summaryEl.appendChild(title);
    summaryEl.appendChild(meta);
    details.appendChild(summaryEl);

    const body = document.createElement("div");
    body.className = "group-body";
    body.dataset.group = entry.group;
    body.addEventListener("scroll", () => {
      applicationState.groupScrollTop.set(entry.group, body.scrollTop);
    }, { passive: true });

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    thead.innerHTML = `
      <tr>
        <th>选择</th>
        <th>名称</th>
        <th>大小</th>
        <th>目录类型</th>
        <th>风险</th>
        <th>判断依据</th>
      </tr>
    `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    entry.items.forEach((item) => tbody.appendChild(buildApplicationRow(item)));
    table.appendChild(tbody);
    body.appendChild(table);
    details.appendChild(body);
    applicationGroups.appendChild(details);

    const savedScrollTop = applicationState.groupScrollTop.get(entry.group);
    if (savedScrollTop) {
      body.scrollTop = savedScrollTop;
    }
  });

  updateApplicationSummary();
  renderApplicationDetail(ensureCurrentApplicationItem());
  markCurrentApplicationRow();
}

function buildApplicationScanSummary(result) {
  const lines = [
    "应用残留扫描摘要",
    "",
    `疑似残留总数: ${result.total_count || 0}`,
    `总空间: ${formatBytes(result.total_bytes || 0)}`,
    `高风险项目: ${result.high_risk_count || 0}`,
    "",
    "按应用统计：",
  ];
  (result.groups || []).forEach((group) => {
    lines.push(`- ${group.name}: ${group.count || 0} 个，${formatBytes(group.total_bytes || 0)}，高风险 ${group.high_risk_count || 0} 个`);
  });
  return lines.join("\n");
}

function buildApplicationCleanSummary(result) {
  const lines = [
    "删除应用残留结果",
    "",
    `成功: ${result.deleted_count || 0}`,
    `失败: ${result.failed_count || 0}`,
    `释放空间: ${formatBytes(result.reclaimed_bytes || 0)}`,
    "",
  ];
  (result.results || []).forEach((item) => {
    lines.push(`- ${item.name}: ${item.success ? "成功" : "失败"} | ${item.message}`);
  });
  return lines.join("\n");
}

async function scanApplications() {
  try {
    setApplicationBusy(true, "扫描中，请稍候...");
    applicationSummary.textContent = "扫描应用残留中，请稍候...";
    applicationResultBox.textContent = "扫描应用残留中，请稍候...\n\n我会优先扫描用户目录里看起来像已卸载应用残留的项目。";
    const result = await api("/api/scan-app-residuals");
    applicationState.items = result.items || [];
    applicationState.selectedPaths.clear();
    applicationState.currentPath = null;
    applicationState.expandedGroups.clear();
    applicationState.groupScrollTop.clear();
    applicationState.selectionAnchor = null;
    applicationSummary.textContent =
      `扫描完成。共发现 ${result.total_count || 0} 个疑似残留，总空间 ${formatBytes(result.total_bytes || 0)}，高风险 ${result.high_risk_count || 0} 个。`;
    applicationResultBox.textContent = buildApplicationScanSummary(result);
    renderApplicationGroups();
  } catch (error) {
    alert(error.message);
    applicationSummary.textContent = "扫描应用残留失败，请看错误提示。";
  } finally {
    setApplicationBusy(false, "空闲");
  }
}

async function deleteApplications() {
  const items = applicationState.items.filter((item) => applicationState.selectedPaths.has(item.path));
  if (!items.length) {
    alert("请先勾选至少一个残留项目。");
    return;
  }
  if (!confirm(`即将删除 ${items.length} 个你勾选的残留项目，是否继续？`)) return;
  try {
    setApplicationBusy(true, "删除残留中，请稍候...");
    const result = await api("/api/clean-app-residuals", { items });
    const deletedPaths = new Set((result.results || []).filter((item) => item.success).map((item) => item.path));
    applicationState.items = applicationState.items.filter((item) => !deletedPaths.has(item.path));
    applicationState.selectedPaths = new Set([...applicationState.selectedPaths].filter((path) => !deletedPaths.has(path)));
    if (applicationState.currentPath && deletedPaths.has(applicationState.currentPath)) {
      applicationState.currentPath = null;
    }
    applicationSummary.textContent =
      `删除完成。成功 ${result.deleted_count || 0} 个，失败 ${result.failed_count || 0} 个。`;
    applicationResultBox.textContent = buildApplicationCleanSummary(result);
    renderApplicationGroups();
  } catch (error) {
    alert(error.message);
  } finally {
    setApplicationBusy(false, "空闲");
  }
}

async function revealApplicationItem() {
  const current = getCurrentApplicationItem();
  if (!current) {
    alert("请先选择一个残留项目。");
    return;
  }
  try {
    setApplicationBusy(true, "正在访达中定位残留项目...");
    await api("/api/reveal-file", { path: current.path });
    applicationSummary.textContent = `已在访达中显示：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setApplicationBusy(false, "空闲");
  }
}

async function openApplicationItem() {
  const current = getCurrentApplicationItem();
  if (!current) {
    alert("请先选择一个残留项目。");
    return;
  }
  try {
    setApplicationBusy(true, "正在尝试打开目标...");
    await api("/api/open-file", { path: current.path });
    applicationSummary.textContent = `已尝试打开：${current.name}`;
  } catch (error) {
    alert(error.message);
  } finally {
    setApplicationBusy(false, "空闲");
  }
}

async function loadVersion() {
  const response = await fetch("/api/version");
  const data = await response.json();
  versionLine.textContent = `版本：${data.version}`;
}

overviewTab.addEventListener("click", () => goToRoute("overview"));
fileCleaningTab.addEventListener("click", () => goToRoute("file"));
appCachesTab.addEventListener("click", () => goToRoute("app"));
startupTab.addEventListener("click", () => goToRoute("startup"));
memoryTab.addEventListener("click", () => goToRoute("memory"));
imagesTab.addEventListener("click", () => goToRoute("images"));
spaceTab.addEventListener("click", () => goToRoute("space"));
applicationsTab.addEventListener("click", () => goToRoute("applications"));

scanOverviewBtn.addEventListener("click", scanOverview);
clearOverviewSelectionBtn.addEventListener("click", () => {
  overviewState.selectedIds.clear();
  overviewState.selectionAnchors = {};
  renderOverviewCards(overviewState.cards);
});
executeOverviewBtn.addEventListener("click", executeOverviewSelection);

scanBtn.addEventListener("click", scanFileCleaning);
executeCategoryBtn.addEventListener("click", executeFileCleaningCategories);
selectAllCandidatesBtn.addEventListener("click", () => {
  fileCleaningState.candidateSelectedPaths = new Set(fileCleaningState.candidates.map((item) => item.path));
  renderFileCleaningTables();
});
clearCandidateSelectionBtn.addEventListener("click", () => {
  fileCleaningState.candidateSelectedPaths.clear();
  renderFileCleaningTables();
});
deleteCandidateBtn.addEventListener("click", () => deleteFileCleaningSelection("candidate", "删除候选文件"));
selectAllInstallersBtn.addEventListener("click", () => {
  fileCleaningState.installerSelectedPaths = new Set(fileCleaningState.installers.map((item) => item.path));
  renderFileCleaningTables();
});
clearInstallerSelectionBtn.addEventListener("click", () => {
  fileCleaningState.installerSelectedPaths.clear();
  renderFileCleaningTables();
});
deleteInstallerBtn.addEventListener("click", () => deleteFileCleaningSelection("installer", "删除安装文件"));
selectAllDownloadsBtn.addEventListener("click", () => {
  fileCleaningState.downloadSelectedPaths = new Set(fileCleaningState.downloads.map((item) => item.path));
  renderFileCleaningTables();
});
clearDownloadSelectionBtn.addEventListener("click", () => {
  fileCleaningState.downloadSelectedPaths.clear();
  renderFileCleaningTables();
});
deleteDownloadBtn.addEventListener("click", () => deleteFileCleaningSelection("download", "删除下载文件"));
selectAllLargeBtn.addEventListener("click", () => {
  fileCleaningState.largeSelectedPaths = new Set(fileCleaningState.largeFiles.map((item) => item.path));
  renderFileCleaningTables();
});
clearLargeSelectionBtn.addEventListener("click", () => {
  fileCleaningState.largeSelectedPaths.clear();
  renderFileCleaningTables();
});
deleteLargeBtn.addEventListener("click", () => deleteFileCleaningSelection("large", "删除大型文件"));
revealFileBtn.addEventListener("click", revealFileCleaningItem);
openFileBtn.addEventListener("click", openFileCleaningItem);

scanAppCachesBtn.addEventListener("click", scanAppCaches);
executeAppCategoriesBtn.addEventListener("click", executeAppCacheCategories);
selectAllAppCacheBtn.addEventListener("click", () => {
  appCacheState.selectedPaths = new Set(appCacheState.files.map((item) => item.path));
  renderAppCacheGroups();
});
clearAppCacheSelectionBtn.addEventListener("click", () => {
  appCacheState.selectedPaths.clear();
  renderAppCacheGroups();
});
deleteAppCacheBtn.addEventListener("click", deleteAppCacheSelection);
revealAppCacheBtn.addEventListener("click", revealAppCacheItem);
openAppCacheBtn.addEventListener("click", openAppCacheItem);

scanStartupBtn.addEventListener("click", scanStartupItems);
disableStartupBtn.addEventListener("click", disableStartupSelection);
selectAllStartupBtn.addEventListener("click", () => {
  startupState.selectedIds = new Set(startupState.items.map((item) => item.id));
  updateStartupSummary();
  renderStartupDetail(getCurrentStartupItem());
  markCurrentStartupRow();
});
clearStartupSelectionBtn.addEventListener("click", () => {
  startupState.selectedIds.clear();
  updateStartupSummary();
  renderStartupDetail(getCurrentStartupItem());
  markCurrentStartupRow();
});
revealStartupBtn.addEventListener("click", revealStartupItem);
openStartupBtn.addEventListener("click", openStartupItem);

scanMemoryBtn.addEventListener("click", scanMemoryProcesses);
terminateMemoryBtn.addEventListener("click", terminateMemorySelection);
selectAllMemoryBtn.addEventListener("click", () => {
  memoryState.selectedIds = new Set(memoryState.items.filter((item) => item.can_terminate).map((item) => item.id));
  renderMemoryTable();
});
clearMemorySelectionBtn.addEventListener("click", () => {
  memoryState.selectedIds.clear();
  renderMemoryTable();
});
revealMemoryBtn.addEventListener("click", revealMemoryItem);
openMemoryBtn.addEventListener("click", openMemoryItem);

scanImagesBtn.addEventListener("click", scanImages);
selectAllScreenshotsBtn.addEventListener("click", () => {
  imageState.screenshotSelectedPaths = new Set(imageState.screenshots.map((item) => item.path));
  renderImageTables();
});
clearScreenshotSelectionBtn.addEventListener("click", () => {
  imageState.screenshotSelectedPaths.clear();
  renderImageTables();
});
deleteScreenshotsBtn.addEventListener("click", () => deleteImageSelection("screenshots", "删除截图"));
selectAllDownloadedImagesBtn.addEventListener("click", () => {
  imageState.downloadSelectedPaths = new Set(imageState.downloads.map((item) => item.path));
  renderImageTables();
});
clearDownloadedImageSelectionBtn.addEventListener("click", () => {
  imageState.downloadSelectedPaths.clear();
  renderImageTables();
});
deleteDownloadedImagesBtn.addEventListener("click", () => deleteImageSelection("downloads", "删除下载图片"));
selectAllSimilarImagesBtn.addEventListener("click", () => {
  imageState.similarSelectedPaths = new Set(imageState.similar.map((item) => item.path));
  renderImageTables();
});
clearSimilarImageSelectionBtn.addEventListener("click", () => {
  imageState.similarSelectedPaths.clear();
  renderImageTables();
});
deleteSimilarImagesBtn.addEventListener("click", () => deleteImageSelection("similar", "删除相似图片"));
selectAllDuplicateImagesBtn.addEventListener("click", () => {
  imageState.duplicateSelectedPaths = new Set(imageState.duplicates.map((item) => item.path));
  renderImageTables();
});
clearDuplicateImageSelectionBtn.addEventListener("click", () => {
  imageState.duplicateSelectedPaths.clear();
  renderImageTables();
});
deleteDuplicateImagesBtn.addEventListener("click", () => deleteImageSelection("duplicates", "删除重复图片"));
selectAllLargeOldImagesBtn.addEventListener("click", () => {
  imageState.largeOldSelectedPaths = new Set(imageState.largeOld.map((item) => item.path));
  renderImageTables();
});
clearLargeOldImageSelectionBtn.addEventListener("click", () => {
  imageState.largeOldSelectedPaths.clear();
  renderImageTables();
});
deleteLargeOldImagesBtn.addEventListener("click", () => deleteImageSelection("largeOld", "删除大图旧图"));
revealImageBtn.addEventListener("click", revealImageItem);
openImageBtn.addEventListener("click", openImageItem);

scanDiskBtn.addEventListener("click", scanDiskUsage);
selectAllDiskLargeFilesBtn.addEventListener("click", () => {
  diskState.selectedPaths = new Set(diskState.largeFiles.map((item) => item.path));
  renderDiskLargeFiles();
});
clearDiskLargeFilesSelectionBtn.addEventListener("click", () => {
  diskState.selectedPaths.clear();
  renderDiskLargeFiles();
});
deleteDiskLargeFilesBtn.addEventListener("click", deleteDiskLargeFiles);
revealDiskBtn.addEventListener("click", revealDiskItem);
openDiskBtn.addEventListener("click", openDiskItem);

scanApplicationsBtn.addEventListener("click", scanApplications);
deleteApplicationsBtn.addEventListener("click", deleteApplications);
selectAllApplicationsBtn.addEventListener("click", () => {
  applicationState.selectedPaths = new Set(applicationState.items.map((item) => item.path));
  updateApplicationSummary();
  renderApplicationDetail(getCurrentApplicationItem());
  markCurrentApplicationRow();
});
clearApplicationSelectionBtn.addEventListener("click", () => {
  applicationState.selectedPaths.clear();
  updateApplicationSummary();
  renderApplicationDetail(getCurrentApplicationItem());
  markCurrentApplicationRow();
});
revealApplicationBtn.addEventListener("click", revealApplicationItem);
openApplicationBtn.addEventListener("click", openApplicationItem);

revealFileBtn.disabled = true;
openFileBtn.disabled = true;
revealAppCacheBtn.disabled = true;
openAppCacheBtn.disabled = true;
revealStartupBtn.disabled = true;
openStartupBtn.disabled = true;
revealMemoryBtn.disabled = true;
openMemoryBtn.disabled = true;
revealImageBtn.disabled = true;
openImageBtn.disabled = true;
revealDiskBtn.disabled = true;
openDiskBtn.disabled = true;
revealApplicationBtn.disabled = true;
openApplicationBtn.disabled = true;
document.addEventListener("mouseup", stopDragSelection);
window.addEventListener("blur", stopDragSelection);
window.addEventListener("hashchange", syncRoute);
syncRoute();

loadVersion().catch((error) => {
  versionLine.textContent = `版本信息加载失败：${error.message}`;
});
