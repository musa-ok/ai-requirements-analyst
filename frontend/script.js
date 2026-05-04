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

const settingGeminiKey = document.getElementById("settingGeminiKey");
const settingBackendUrl = document.getElementById("settingBackendUrl");
const settingJiraUrl = document.getElementById("settingJiraUrl");
const settingJiraEmail = document.getElementById("settingJiraEmail");
const settingJiraToken = document.getElementById("settingJiraToken");
const settingJiraProject = document.getElementById("settingJiraProject");
const settingGithubToken = document.getElementById("settingGithubToken");
const settingGithubRepo = document.getElementById("settingGithubRepo");
const settingGithubPath = document.getElementById("settingGithubPath");
const settingGithubBranch = document.getElementById("settingGithubBranch");
const settingRagCollection = document.getElementById("settingRagCollection");

const SESSION_STORAGE_KEY = "ai_ra_session_id";
const SETTINGS_STORAGE_KEY = "ai_ra_user_config";

const sessionId = localStorage.getItem(SESSION_STORAGE_KEY) || crypto.randomUUID();
localStorage.setItem(SESSION_STORAGE_KEY, sessionId);

let lastAnalysisId = null;

function defaultSettings() {
    return {
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
        return { ...defaultSettings(), ...JSON.parse(raw) };
    } catch {
        return defaultSettings();
    }
}

function persistSettings(partial) {
    const merged = { ...loadSettings(), ...partial };
    localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(merged));
    return merged;
}

function getBackendBaseUrl() {
    const trimmed = loadSettings().backend_base_url.trim();
    if (trimmed) return trimmed.replace(/\/$/, "");
    return "http://127.0.0.1:8000";
}

function populateSettingsForm() {
    const s = loadSettings();
    settingGeminiKey.value = s.gemini_api_key;
    settingBackendUrl.value = s.backend_base_url;
    settingJiraUrl.value = s.jira_base_url;
    settingJiraEmail.value = s.jira_email;
    settingJiraToken.value = s.jira_api_token;
    settingJiraProject.value = s.jira_project_key;
    settingGithubToken.value = s.github_token;
    settingGithubRepo.value = s.github_repo;
    settingGithubPath.value = s.github_default_path || "exports/analysis.md";
    settingGithubBranch.value = s.github_branch || "main";
    settingRagCollection.value = s.rag_collection || "default";
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

    const settings = loadSettings();
    if (!settings.gemini_api_key.trim()) {
        showToast('Gemini API anahtari eksik. "Ayarlar" icinden ekleyin.', "error");
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analiz Ediliyor...";

    bddOutput.classList.add("hidden");
    placeholderText.classList.add("hidden");
    skeleton.classList.remove("hidden");

    const base = getBackendBaseUrl();
    const headers = {
        "Content-Type": "application/json",
        "X-Gemini-Api-Key": settings.gemini_api_key.trim(),
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
                api_key: settings.gemini_api_key.trim(),
            }),
        });
        if (!response.ok) {
            throw new Error(await parseErrorResponse(response));
        }
        const data = await response.json();
        lastAnalysisId = data.analysis_id;
        skeleton.classList.add("hidden");
        bddOutput.classList.remove("hidden");
        bddOutput.textContent = [
            "BDD Acceptance Criteria:",
            ...data.acceptance_criteria.map((item) => `- ${item}`),
            "",
            "Gherkin Scenarios:",
            ...data.gherkin_scenarios,
            "",
            `Story Point: ${data.story_points}`,
            `QA (${data.qa_status}): ${data.qa_feedback}`,
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
});

settingsBtn.addEventListener("click", () => {
    populateSettingsForm();
    settingsModal.classList.remove("hidden");
});

closeSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
});

saveSettingsBtn.addEventListener("click", () => {
    persistSettings({
        gemini_api_key: settingGeminiKey.value.trim(),
        backend_base_url: settingBackendUrl.value.trim(),
        jira_base_url: settingJiraUrl.value.trim(),
        jira_email: settingJiraEmail.value.trim(),
        jira_api_token: settingJiraToken.value.trim(),
        jira_project_key: settingJiraProject.value.trim(),
        github_token: settingGithubToken.value.trim(),
        github_repo: settingGithubRepo.value.trim(),
        github_default_path: settingGithubPath.value.trim() || "exports/analysis.md",
        github_branch: settingGithubBranch.value.trim() || "main",
        rag_collection: settingRagCollection.value.trim() || "default",
    });
    showToast("Yapilandirma kaydedildi (tarayici yerel deposu).", "success");
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
    if (!baseUrl || !email || !token || !projectKey) {
        showToast("Jira icin Ayarlar'da URL, e-posta, token ve proje anahtari girin.", "error");
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
        showToast("GitHub icin Ayarlar'da repo (owner/isim) ve token girin.", "error");
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
