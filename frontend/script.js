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
const apiKeyInput = document.getElementById("apiKeyInput");
const rememberApiKey = document.getElementById("rememberApiKey");
const ragCollectionInput = document.getElementById("ragCollectionInput");

const BACKEND_URL = "http://127.0.0.1:8000";
const API_KEY_STORAGE = "ai_ra_api_key";
const SESSION_STORAGE_KEY = "ai_ra_session_id";
const sessionId = localStorage.getItem(SESSION_STORAGE_KEY) || crypto.randomUUID();
localStorage.setItem(SESSION_STORAGE_KEY, sessionId);
let lastAnalysisId = null;

const projectData = {
    "musteri-portali": {
        title: "Gereksinim Analizi - Musteri Portali",
        prompt: "Musteri portali icin kayit, giris, profil guncelleme ve rol tabanli erisim kurallarini analiz et.",
        output: [
            "Feature: Musteri Portali",
            "",
            "  Scenario: Kullanici kayit ve giris akislarinin dogrulanmasi",
            "    Given kullanici kayit formunu gecerli bilgilerle doldurur",
            "    When kullanici hesabi olusturur ve giris yapar",
            "    Then sistem kullanici panelini ve profil ozetini gosterir"
        ].join("\n")
    },
    "odeme-sistemi": {
        title: "Gereksinim Analizi - Odeme Sistemi",
        prompt: "Odeme sistemi icin kart dogrulama, basarisiz odeme tekrar deneme ve fatura olusturma adimlarini analiz et.",
        output: [
            "Feature: Odeme Sistemi",
            "",
            "  Scenario: Basarili odeme islemi",
            "    Given kullanicinin gecerliligi onaylanmis bir karti vardir",
            "    When kullanici odeme islemini tamamlar",
            "    Then sistem odemeyi onaylar ve fatura kaydi olusturur"
        ].join("\n")
    }
};

function renderProject(projectKey) {
    const project = projectData[projectKey];
    if (!project) return;

    pageTitle.textContent = project.title;
    userInput.value = project.prompt;
    placeholderText.classList.add("hidden");
    skeleton.classList.add("hidden");
    bddOutput.classList.remove("hidden");
    bddOutput.textContent = project.output;
}

function loadApiKeySettings() {
    const savedKey = localStorage.getItem(API_KEY_STORAGE) || "";
    apiKeyInput.value = savedKey;
    rememberApiKey.checked = true;
    ragCollectionInput.value = "default";
}

function persistApiKeySetting() {
    if (rememberApiKey.checked) {
        localStorage.setItem(API_KEY_STORAGE, apiKeyInput.value.trim());
    } else {
        localStorage.removeItem(API_KEY_STORAGE);
    }
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

/* Neon focus ring state */
userInput.addEventListener("focus", () => {
    inputShell.classList.add("is-focused");
});

userInput.addEventListener("blur", () => {
    inputShell.classList.remove("is-focused");
});

/* Optional mic active state */
micBtn.addEventListener("click", () => {
    micBtn.classList.toggle("active");
});

/* Keyboard shortcut: Cmd/Ctrl + Enter */
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

/* Analyze flow with shimmer skeleton */
analyzeBtn.addEventListener("click", async () => {
    const requirementText = userInput.value.trim();
    if (!requirementText) {
        alert("Lutfen once bir gereksinim metni girin.");
        return;
    }

    persistApiKeySetting();
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analiz Ediliyor...";

    bddOutput.classList.add("hidden");
    placeholderText.classList.add("hidden");
    skeleton.classList.remove("hidden");

    try {
        const response = await fetch(`${BACKEND_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId,
                project_name: pageTitle.textContent.replace("Gereksinim Analizi - ", ""),
                requirement_text: requirementText,
                rag_collection: ragCollectionInput.value.trim() || "default",
                api_key: apiKeyInput.value.trim()
            })
        });
        if (!response.ok) {
            throw new Error("Analiz servisi yanit vermedi.");
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
            `QA: ${data.qa_feedback}`
        ].join("\n");
    } catch (error) {
        skeleton.classList.add("hidden");
        bddOutput.classList.remove("hidden");
        bddOutput.textContent = `Hata: ${error.message}`;
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
});

settingsBtn.addEventListener("click", () => {
    settingsModal.classList.remove("hidden");
});

closeSettingsBtn.addEventListener("click", () => {
    settingsModal.classList.add("hidden");
});

settingsModal.addEventListener("click", (event) => {
    if (event.target === settingsModal) {
        settingsModal.classList.add("hidden");
    }
});

rememberApiKey.addEventListener("change", persistApiKeySetting);
apiKeyInput.addEventListener("input", persistApiKeySetting);

ragUploadInput.addEventListener("change", async () => {
    const file = ragUploadInput.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    const collectionName = ragCollectionInput.value.trim() || "default";
    await fetch(`${BACKEND_URL}/rag/upload?session_id=${encodeURIComponent(sessionId)}&collection_name=${encodeURIComponent(collectionName)}`, {
        method: "POST",
        body: formData
    });
    alert("PDF RAG indeksine yuklendi.");
});

async function triggerFileDownload(path) {
    if (!lastAnalysisId) {
        alert("Once bir analiz olusturun.");
        return;
    }
    window.open(`${BACKEND_URL}${path}/${sessionId}/${lastAnalysisId}`, "_blank");
}

pdfBtn.addEventListener("click", () => triggerFileDownload("/export/pdf"));
wordBtn.addEventListener("click", () => triggerFileDownload("/export/word"));

jiraBtn.addEventListener("click", async () => {
    if (!lastAnalysisId) {
        alert("Once bir analiz olusturun.");
        return;
    }
    const jiraBaseUrl = prompt("Jira Base URL (https://domain.atlassian.net)");
    const email = prompt("Jira e-posta");
    const projectKey = prompt("Jira Project Key");
    const apiToken = apiKeyInput.value.trim();
    if (!jiraBaseUrl || !email || !projectKey || !apiToken) return;
    const response = await fetch(`${BACKEND_URL}/export/jira/${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            analysis_id: lastAnalysisId,
            jira_base_url: jiraBaseUrl,
            email,
            api_token: apiToken,
            project_key: projectKey
        })
    });
    alert(response.ok ? "Jira gorevi olusturuldu." : "Jira export basarisiz.");
});

githubBtn.addEventListener("click", async () => {
    if (!lastAnalysisId) {
        alert("Once bir analiz olusturun.");
        return;
    }
    const repository = prompt("GitHub repo (owner/repo)");
    const filePath = prompt("Dosya yolu", "exports/analysis.md");
    const token = apiKeyInput.value.trim();
    if (!repository || !token) return;
    const response = await fetch(`${BACKEND_URL}/export/github/${sessionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            analysis_id: lastAnalysisId,
            repository,
            token,
            file_path: filePath || "exports/analysis.md"
        })
    });
    alert(response.ok ? "GitHub export tamamlandi." : "GitHub export basarisiz.");
});

renderProject("musteri-portali");
loadApiKeySettings();
