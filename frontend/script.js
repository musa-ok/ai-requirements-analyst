const userInput = document.getElementById("userInput");
const inputShell = document.getElementById("inputShell");
const analyzeBtn = document.getElementById("analyzeBtn");
const shortcutToast = document.getElementById("shortcutToast");
const pageTitle = document.getElementById("pageTitle");
const inputSection = document.getElementById("inputSection");
const outputSection = document.getElementById("outputSection");
const newAnalysisBtn = document.getElementById("newAnalysisBtn");
const projectItems = document.querySelectorAll("[data-project]");
const settingsBtn = document.getElementById("settingsBtn");
const settingsModal = document.getElementById("settingsModal");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const saveSettingsBtn = document.getElementById("saveSettingsBtn");

const appRoot = document.getElementById("appRoot");
const navBackdrop = document.getElementById("navBackdrop");
const navMenuToggle = document.getElementById("navMenuToggle");
const sidebarCloseBtn = document.getElementById("sidebarCloseBtn");

const resultDisplay = document.getElementById("resultDisplay");
const placeholderText = resultDisplay.querySelector(".placeholder-text");
const skeleton = document.getElementById("skeleton");
const bddOutput = document.getElementById("bddOutput");

const jiraBtn = document.getElementById("jiraBtn");
const githubBtn = document.getElementById("githubBtn");
const pdfBtn = document.getElementById("pdfBtn");
const wordBtn = document.getElementById("wordBtn");
const micBtn = document.getElementById("micBtn");
const ragUploadInput = document.getElementById("rag-upload");

const settingModelType = document.getElementById("settingModelType");
const settingLlmApiKey = document.getElementById("settingLlmApiKey");
const settingJiraUrl = document.getElementById("settingJiraUrl");
const settingJiraEmail = document.getElementById("settingJiraEmail");
const settingJiraToken = document.getElementById("settingJiraToken");
const settingGithubToken = document.getElementById("settingGithubToken");
const settingBackendUrl = document.getElementById("settingBackendUrl");
const settingRagCollection = document.getElementById("settingRagCollection");
const settingJiraProject = document.getElementById("settingJiraProject");
const settingGithubRepo = document.getElementById("settingGithubRepo");
const settingGithubPath = document.getElementById("settingGithubPath");
const settingGithubBranch = document.getElementById("settingGithubBranch");

const SESSION_STORAGE_KEY = "ai_ra_session_id";
const SETTINGS_STORAGE_KEY = "ai_ra_user_config";
const LLM_API_KEY_GUARD_MESSAGE =
    "Lütfen analiz yapmadan önce Ayarlar menüsünden seçtiğiniz model için API anahtarınızı girin.";

const sessionId = localStorage.getItem(SESSION_STORAGE_KEY) || crypto.randomUUID();
localStorage.setItem(SESSION_STORAGE_KEY, sessionId);

let lastAnalysisId = null;

function closeNavDrawer() {
    if (!appRoot) return;
    appRoot.classList.remove("is-nav-open");
    document.body.classList.remove("nav-drawer-open");
    if (navMenuToggle) {
        navMenuToggle.setAttribute("aria-expanded", "false");
        navMenuToggle.setAttribute("aria-label", "Menüyü aç");
    }
    if (navBackdrop) navBackdrop.setAttribute("aria-hidden", "true");
}

function openNavDrawer() {
    if (!appRoot) return;
    appRoot.classList.add("is-nav-open");
    document.body.classList.add("nav-drawer-open");
    if (navMenuToggle) {
        navMenuToggle.setAttribute("aria-expanded", "true");
        navMenuToggle.setAttribute("aria-label", "Menüyü kapat");
    }
    if (navBackdrop) navBackdrop.setAttribute("aria-hidden", "false");
}

function toggleNavDrawer() {
    if (!appRoot) return;
    if (appRoot.classList.contains("is-nav-open")) closeNavDrawer();
    else openNavDrawer();
}

if (navMenuToggle) navMenuToggle.addEventListener("click", toggleNavDrawer);
if (navBackdrop) navBackdrop.addEventListener("click", closeNavDrawer);
if (sidebarCloseBtn) sidebarCloseBtn.addEventListener("click", closeNavDrawer);

window.matchMedia("(min-width: 769px)").addEventListener("change", (e) => {
    if (e.matches) closeNavDrawer();
});

function defaultSettings() {
    return {
        model_type: "gemini",
        llm_api_key: "",
        gemini_api_key: "",
        backend_base_url: "",
        jira_base_url: "",
        jira_email: "",
        jira_api_token: "",
        jira_project_key: "",
        github_token: "",
        github_repo: "",
        github_default_path: "exports/analysis.md",
        github_branch: "main",
        rag_collection: "default",
    };
}

function loadSettings() {
    try {
        const raw = localStorage.getItem(SETTINGS_STORAGE_KEY);
        if (!raw) return defaultSettings();
        const merged = { ...defaultSettings(), ...JSON.parse(raw) };
        if (!merged.llm_api_key && merged.gemini_api_key) {
            merged.llm_api_key = merged.gemini_api_key;
        }
        if (!merged.model_type) merged.model_type = "gemini";
        return merged;
    } catch {
        return defaultSettings();
    }
}

function persistSettings(partial) {
    const merged = { ...loadSettings(), ...partial };
    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(merged));
    return merged;
}

/** Analiz öncesi: yalnızca localStorage üzerinden doğrulama */
function getLlmApiKeyFromStorage() {
    const s = loadSettings();
    return String(s.llm_api_key || s.gemini_api_key || "").trim();
}

function syncApiKeyPlaceholder() {
    if (!settingLlmApiKey || !settingModelType) return;
    const mt = settingModelType.value || "gemini";
    const placeholders = {
        gemini: "Google AI Studio / Gemini API anahtarı",
        claude: "Anthropic API Key girin",
        openai: "OpenAI API Key girin",
    };
    settingLlmApiKey.placeholder = placeholders[mt] || placeholders.gemini;
}

function getBackendBaseUrl() {
    const trimmed = loadSettings().backend_base_url.trim();
    if (trimmed) return trimmed.replace(/\/$/, "");
    return "http://127.0.0.1:8001";
}

function populateSettingsForm() {
    const s = loadSettings();
    if (settingModelType) {
        settingModelType.value = ["gemini", "claude", "openai"].includes(s.model_type)
            ? s.model_type
            : "gemini";
    }
    if (settingLlmApiKey) {
        settingLlmApiKey.value = (s.llm_api_key || s.gemini_api_key || "").trim();
    }
    syncApiKeyPlaceholder();
    settingJiraUrl.value = s.jira_base_url;
    settingJiraEmail.value = s.jira_email;
    settingJiraToken.value = s.jira_api_token;
    settingGithubToken.value = s.github_token;
    settingBackendUrl.value = s.backend_base_url;
    settingRagCollection.value = s.rag_collection || "default";
    settingJiraProject.value = s.jira_project_key;
    settingGithubRepo.value = s.github_repo;
    settingGithubPath.value = s.github_default_path || "exports/analysis.md";
    settingGithubBranch.value = s.github_branch || "main";
}

const projectData = {
    "musteri-portali": {
        title: "Gereksinim Analizi - Musteri Portali",
        prompt:
            "Musteri portali icin kayit, giris, profil guncelleme ve rol tabanli erisim kurallarini analiz et.",
    },
    "odeme-sistemi": {
        title: "Gereksinim Analizi - Odeme Sistemi",
        prompt:
            "Odeme sistemi icin kart dogrulama, basarisiz odeme tekrar deneme ve fatura olusturma adimlarini analiz et.",
    },
};

function showToast(message, variant = "info") {
    const host = document.getElementById("toastHost");
    if (!host) return;
    const el = document.createElement("div");
    el.className = `toast toast--${variant}`;
    el.textContent = message;
    host.appendChild(el);
    requestAnimationFrame(() => el.classList.add("toast--show"));
    window.setTimeout(() => {
        el.classList.remove("toast--show");
        window.setTimeout(() => el.remove(), 280);
    }, 4200);
}

async function parseErrorResponse(response) {
    try {
        const errBody = await response.json();
        if (errBody.detail !== undefined) {
            return typeof errBody.detail === "string" ? errBody.detail : JSON.stringify(errBody.detail);
        }
    } catch {
        /* ignore */
    }
    return response.statusText || "Istek basarisiz.";
}

function renderProject(projectKey) {
    const project = projectData[projectKey];
    if (!project) return;

    pageTitle.textContent = project.title;
    userInput.value = project.prompt;
    lastAnalysisId = null;
    bddOutput.textContent = "";
    bddOutput.classList.add("hidden");
    skeleton.classList.add("hidden");
    placeholderText.classList.remove("hidden");
}

function toggleSwitchAnimation() {
    inputSection.classList.add("is-switching");
    outputSection.classList.add("is-switching");
    window.setTimeout(() => {
        inputSection.classList.remove("is-switching");
        outputSection.classList.remove("is-switching");
    }, 220);
}

function setActiveProject(activeItem) {
    projectItems.forEach((item) => item.classList.remove("active"));
    if (activeItem) activeItem.classList.add("active");
}

userInput.addEventListener("focus", () => {
    inputShell.classList.add("is-focused");
});

userInput.addEventListener("blur", () => {
    inputShell.classList.remove("is-focused");
});

micBtn.addEventListener("click", () => {
    micBtn.classList.toggle("active");
});

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        if (!settingsModal.classList.contains("hidden")) {
            settingsModal.classList.add("hidden");
            event.preventDefault();
            return;
        }
        closeNavDrawer();
        return;
    }

    const isEnter = event.key === "Enter";
    const isModifierPressed = event.metaKey || event.ctrlKey;

    if (isEnter && isModifierPressed) {
        event.preventDefault();
        analyzeBtn.click();
        showShortcutToast();
    }
});

function showShortcutToast() {
    shortcutToast.classList.add("show");
    window.clearTimeout(showShortcutToast._timer);
    showShortcutToast._timer = window.setTimeout(() => {
        shortcutToast.classList.remove("show");
    }, 900);
}

analyzeBtn.addEventListener("click", async () => {
    const requirementText = userInput.value.trim();
    if (!requirementText) {
        showToast("Lutfen once bir gereksinim metni girin.", "error");
        return;
    }

    if (!getLlmApiKeyFromStorage()) {
        showToast(LLM_API_KEY_GUARD_MESSAGE, "error");
        return;
    }

    const settings = loadSettings();
    const apiKey = getLlmApiKeyFromStorage();
    const modelType = ["gemini", "claude", "openai"].includes(settings.model_type)
        ? settings.model_type
        : "gemini";

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analiz Ediliyor...";

    bddOutput.classList.add("hidden");
    placeholderText.classList.add("hidden");
    skeleton.classList.remove("hidden");

    const base = getBackendBaseUrl();
    const headers = {
        "Content-Type": "application/json",
        "X-Llm-Api-Key": apiKey,
        "X-Gemini-Api-Key": apiKey,
        "X-Model-Type": modelType,
    };

    try {
        const response = await fetch(`${base}/analyze`, {
            method: "POST",
            headers,
            body: JSON.stringify({
                session_id: sessionId,
                project_name: pageTitle.textContent.replace("Gereksinim Analizi - ", ""),
                requirement_text: requirementText,
                rag_collection: (settings.rag_collection || "default").trim() || "default",
                api_key: apiKey,
                model_type: modelType,
            }),
        });
        if (!response.ok) {
            throw new Error(await parseErrorResponse(response));
        }
        const data = await response.json();
        lastAnalysisId = data.analysis_id;
        skeleton.classList.add("hidden");
        bddOutput.classList.remove("hidden");
        const qaLabel =
            data.qa_status === "passed" ? "Onaylandi" : "Inceleme gerekli";
        bddOutput.textContent = [
            "BDD Kabul Kriterleri:",
            ...data.acceptance_criteria.map((item) => `- ${item}`),
            "",
            "Gherkin Senaryolari:",
            ...data.gherkin_scenarios,
            "",
            `Story Point: ${data.story_points}`,
            `QA (${qaLabel}): ${data.qa_feedback}`,
        ].join("\n");
        showToast("Analiz tamamlandi.", "success");
    } catch (error) {
        skeleton.classList.add("hidden");
        bddOutput.classList.remove("hidden");
        bddOutput.textContent = `Hata: ${error.message}`;
        showToast(error.message, "error");
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analiz Et (BDD)";
    }
});

projectItems.forEach((item) => {
    item.addEventListener("click", () => {
        const projectKey = item.dataset.project;
        if (!projectKey) return;
        setActiveProject(item);
        toggleSwitchAnimation();
        renderProject(projectKey);
        closeNavDrawer();
    });
});

newAnalysisBtn.addEventListener("click", () => {
    setActiveProject(null);
    toggleSwitchAnimation();
    pageTitle.textContent = "Gereksinim Analizi - Yeni Analiz";
    userInput.value = "";
    bddOutput.textContent = "";
    bddOutput.classList.add("hidden");
    skeleton.classList.add("hidden");
    placeholderText.classList.remove("hidden");
    lastAnalysisId = null;
    closeNavDrawer();
});

settingsBtn.addEventListener("click", () => {
    closeNavDrawer();
    populateSettingsForm();
    settingsModal.classList.remove("hidden");
});

closeSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
});

if (settingModelType) {
    settingModelType.addEventListener("change", syncApiKeyPlaceholder);
}

saveSettingsBtn.addEventListener("click", () => {
    const prev = loadSettings();
    const keyVal = settingLlmApiKey ? settingLlmApiKey.value.trim() : "";
    const mt = settingModelType && ["gemini", "claude", "openai"].includes(settingModelType.value)
        ? settingModelType.value
        : "gemini";
    persistSettings({
        ...prev,
        model_type: mt,
        llm_api_key: keyVal,
        gemini_api_key: keyVal,
        jira_base_url: settingJiraUrl.value.trim(),
        jira_email: settingJiraEmail.value.trim(),
        jira_api_token: settingJiraToken.value.trim(),
        github_token: settingGithubToken.value.trim(),
        backend_base_url: settingBackendUrl.value.trim(),
        rag_collection: settingRagCollection.value.trim() || "default",
        jira_project_key: settingJiraProject.value.trim(),
        github_repo: settingGithubRepo.value.trim(),
        github_default_path: settingGithubPath.value.trim() || "exports/analysis.md",
        github_branch: settingGithubBranch.value.trim() || "main",
    });
    showToast("Ayarlar kaydedildi.", "success");
    settingsModal.classList.add("hidden");
});

settingsModal.addEventListener("click", (event) => {
    if (event.target === settingsModal) {
        settingsModal.classList.add("hidden");
    }
});

ragUploadInput.addEventListener("change", async () => {
    const file = ragUploadInput.files[0];
    if (!file) return;
    const settings = loadSettings();
    const formData = new FormData();
    formData.append("file", file);
    const collectionName = (settings.rag_collection || "default").trim() || "default";
    const base = getBackendBaseUrl();
    try {
        const res = await fetch(
            `${base}/rag/upload?session_id=${encodeURIComponent(sessionId)}&collection_name=${encodeURIComponent(collectionName)}`,
            {
                method: "POST",
                body: formData,
            }
        );
        if (!res.ok) {
            throw new Error(await parseErrorResponse(res));
        }
        showToast("PDF RAG indeksine yuklendi.", "success");
    } catch (e) {
        showToast(e.message || "RAG yukleme basarisiz.", "error");
    }
    ragUploadInput.value = "";
});

async function triggerFileDownload(path) {
    if (!lastAnalysisId) {
        showToast("Once bir analiz olusturun.", "error");
        return;
    }
    const base = getBackendBaseUrl();
    window.open(`${base}${path}/${sessionId}/${lastAnalysisId}`, "_blank");
}

pdfBtn.addEventListener("click", () => triggerFileDownload("/export/pdf"));
wordBtn.addEventListener("click", () => triggerFileDownload("/export/word"));

jiraBtn.addEventListener("click", async () => {
    if (!lastAnalysisId) {
        showToast("Once bir analiz olusturun.", "error");
        return;
    }
    const s = loadSettings();
    const baseUrl = s.jira_base_url.trim();
    const email = s.jira_email.trim();
    const token = s.jira_api_token.trim();
    const projectKey = s.jira_project_key.trim();
    const missing = [];
    if (!baseUrl) missing.push("Jira Base URL");
    if (!email) missing.push("Jira Email");
    if (!token) missing.push("Jira API Token");
    if (!projectKey) missing.push("Jira proje anahtari");
    if (missing.length) {
        showToast("Jira export icin eksik alanlar: " + missing.join(", "), "error");
        return;
    }

    const base = getBackendBaseUrl();
    const headers = {
        "Content-Type": "application/json",
        "X-Jira-Base-Url": baseUrl,
        "X-Jira-Email": email,
        "X-Jira-Api-Token": token,
        "X-Jira-Project-Key": projectKey,
    };

    jiraBtn.disabled = true;
    try {
        const response = await fetch(`${base}/export/jira/${sessionId}`, {
            method: "POST",
            headers,
            body: JSON.stringify({
                analysis_id: lastAnalysisId,
                jira_base_url: baseUrl,
                email,
                api_token: token,
                project_key: projectKey,
                issue_type: "Task",
            }),
        });
        if (!response.ok) {
            throw new Error(await parseErrorResponse(response));
        }
        const data = await response.json();
        showToast(`Jira olusturuldu: ${data.jira_issue_key || "OK"}`, "success");
        jiraBtn.classList.add("success");
        window.setTimeout(() => jiraBtn.classList.remove("success"), 600);
    } catch (error) {
        showToast(error.message, "error");
    } finally {
        jiraBtn.disabled = false;
    }
});

githubBtn.addEventListener("click", async () => {
    if (!lastAnalysisId) {
        showToast("Once bir analiz olusturun.", "error");
        return;
    }
    const s = loadSettings();
    const repo = s.github_repo.trim();
    const ghToken = s.github_token.trim();
    const filePath = (s.github_default_path || "exports/analysis.md").trim() || "exports/analysis.md";
    const branch = (s.github_branch || "main").trim() || "main";
    if (!repo || !ghToken) {
        showToast(
            "GitHub export icin token ve Gelişmiş bölümündeki repository (owner/repo) gerekir. Ayarlar menüsünü kontrol edin.",
            "error"
        );
        return;
    }

    const base = getBackendBaseUrl();
    const headers = {
        "Content-Type": "application/json",
        "X-Github-Token": ghToken,
        "X-Github-Repository": repo,
    };

    githubBtn.disabled = true;
    try {
        const response = await fetch(`${base}/export/github/${sessionId}`, {
            method: "POST",
            headers,
            body: JSON.stringify({
                analysis_id: lastAnalysisId,
                repository: repo,
                token: ghToken,
                file_path: filePath,
                branch,
                commit_message: "Add AI-RA analysis export",
            }),
        });
        if (!response.ok) {
            throw new Error(await parseErrorResponse(response));
        }
        const data = await response.json();
        showToast(`GitHub: ${data.path || ""} (${data.target || repo})`, "success");
        githubBtn.classList.add("success");
        window.setTimeout(() => githubBtn.classList.remove("success"), 600);
    } catch (error) {
        showToast(error.message, "error");
    } finally {
        githubBtn.disabled = false;
    }
});

const initialSidebar = document.querySelector('[data-project="musteri-portali"]');
if (initialSidebar) setActiveProject(initialSidebar);
renderProject("musteri-portali");
populateSettingsForm();
