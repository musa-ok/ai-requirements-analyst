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
const micBtn = document.getElementById("micBtn");

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
analyzeBtn.addEventListener("click", () => {
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analiz Ediliyor...";

    bddOutput.classList.add("hidden");
    placeholderText.classList.add("hidden");
    skeleton.classList.remove("hidden");

    window.setTimeout(() => {
        skeleton.classList.add("hidden");
        bddOutput.classList.remove("hidden");

        bddOutput.textContent = [
            "Feature: Gereksinim Analizi",
            "",
            "  Scenario: Kullanıcı giriş gereksinimlerinin doğrulanması",
            "    Given sistemde kimlik doğrulama gereksinimleri tanımlıdır",
            "    When kullanıcı 'Analiz Et (BDD)' aksiyonunu tetikler",
            "    Then sistem Given/When/Then formatında kabul kriterlerini üretir",
            "    And çıktı Jira ekipleriyle paylaşılabilir formatta sunulur"
        ].join("\n");

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analiz Et (BDD)";
    }, 1500);
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

/* Jira success state with checkmark animation */
jiraBtn.addEventListener("click", () => {
    if (jiraBtn.dataset.success === "1") return;

    const originalText = jiraBtn.textContent;
    jiraBtn.classList.add("success");
    jiraBtn.textContent = "✓ Jira Senkronlandı";
    jiraBtn.dataset.success = "1";

    window.setTimeout(() => {
        jiraBtn.classList.remove("success");
        jiraBtn.textContent = originalText;
        jiraBtn.dataset.success = "0";
    }, 2200);
});

renderProject("musteri-portali");
