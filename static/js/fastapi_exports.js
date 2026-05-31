(function (global) {
  var STORAGE_KEY = "ai_ra_user_config";

  function loadConfig() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return {};
      return JSON.parse(raw);
    } catch (e) {
      return {};
    }
  }

  function backendBaseUrl() {
    var cfg = loadConfig();
    var trimmed = (cfg.backend_base_url || "").trim();
    if (trimmed) return trimmed.replace(/\/$/, "");
    return "http://127.0.0.1:8001";
  }

  function showToast(msg, isError) {
    var el = document.getElementById("raToast");
    if (!el) {
      if (isError) alert(msg);
      return;
    }
    el.textContent = msg;
    el.classList.remove("ra-toast--hidden");
    el.classList.toggle("ra-toast--error", !!isError);
    clearTimeout(showToast._t);
    showToast._t = setTimeout(function () {
      el.classList.add("ra-toast--hidden");
    }, 4200);
  }

  async function parseError(response) {
    try {
      var body = await response.json();
      if (body.detail) {
        return typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
      }
    } catch (e) {
      /* ignore */
    }
    return response.statusText || "Istek basarisiz.";
  }

  function missingJiraFields(cfg) {
    var labels = {
      jira_base_url: "Jira Base URL",
      jira_email: "Jira Email",
      jira_api_token: "Jira API Token",
      jira_project_key: "Jira proje anahtari",
    };
    var missing = [];
    Object.keys(labels).forEach(function (key) {
      if (!(cfg[key] || "").trim()) missing.push(labels[key]);
    });
    return missing;
  }

  function init(options) {
    var sessionId = options.sessionId;
    var analysisId = options.analysisId;
    if (!sessionId || !analysisId) return;

    var base = backendBaseUrl();

    function openExport(path) {
      window.open(base + path + "/" + encodeURIComponent(sessionId) + "/" + encodeURIComponent(analysisId), "_blank");
    }

    var pdfBtn = document.getElementById("exportPdfBtn");
    var wordBtn = document.getElementById("exportWordBtn");
    var jiraBtn = document.getElementById("exportJiraBtn");
    var githubBtn = document.getElementById("exportGithubBtn");

    if (pdfBtn) pdfBtn.addEventListener("click", function () { openExport("/export/pdf"); });
    if (wordBtn) wordBtn.addEventListener("click", function () { openExport("/export/word"); });

    if (jiraBtn) {
      jiraBtn.addEventListener("click", async function () {
        var s = loadConfig();
        var missing = missingJiraFields(s);
        if (missing.length) {
          showToast("Jira export icin eksik alanlar: " + missing.join(", "), true);
          return;
        }
        var jiraBase = (s.jira_base_url || "").trim();
        var email = (s.jira_email || "").trim();
        var token = (s.jira_api_token || "").trim();
        var projectKey = (s.jira_project_key || "").trim();
        jiraBtn.disabled = true;
        try {
          var res = await fetch(base + "/export/jira/" + encodeURIComponent(sessionId), {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Jira-Base-Url": jiraBase,
              "X-Jira-Email": email,
              "X-Jira-Api-Token": token,
              "X-Jira-Project-Key": projectKey,
            },
            body: JSON.stringify({
              analysis_id: analysisId,
              jira_base_url: jiraBase,
              email: email,
              api_token: token,
              project_key: projectKey,
              issue_type: "Task",
            }),
          });
          if (!res.ok) throw new Error(await parseError(res));
          var data = await res.json();
          showToast("Jira: " + (data.jira_issue_key || "OK"), false);
        } catch (err) {
          showToast(err.message, true);
        } finally {
          jiraBtn.disabled = false;
        }
      });
    }

    if (githubBtn) {
      githubBtn.addEventListener("click", async function () {
        var s = loadConfig();
        var repo = (s.github_repo || "").trim();
        var ghToken = (s.github_token || "").trim();
        var filePath = (s.github_default_path || "exports/analysis.md").trim() || "exports/analysis.md";
        var branch = (s.github_branch || "main").trim() || "main";
        if (!repo || !ghToken) {
          showToast("GitHub export icin Ayarlar'daki repository ve token gerekir.", true);
          return;
        }
        githubBtn.disabled = true;
        try {
          var res = await fetch(base + "/export/github/" + encodeURIComponent(sessionId), {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-Github-Token": ghToken,
              "X-Github-Repository": repo,
            },
            body: JSON.stringify({
              analysis_id: analysisId,
              repository: repo,
              token: ghToken,
              file_path: filePath,
              branch: branch,
              commit_message: "Add AI-RA analysis export",
            }),
          });
          if (!res.ok) throw new Error(await parseError(res));
          var data = await res.json();
          showToast("GitHub: " + (data.path || repo), false);
        } catch (err) {
          showToast(err.message, true);
        } finally {
          githubBtn.disabled = false;
        }
      });
    }
  }

  global.AiRaExports = { init: init, backendBaseUrl: backendBaseUrl };
})(window);
