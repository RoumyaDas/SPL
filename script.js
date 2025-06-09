// Tab switching: season tabs
document.querySelectorAll(".season-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".season-tab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".season-content").forEach(c => c.classList.remove("active"));
  
      btn.classList.add("active");
      document.getElementById("season-" + btn.dataset.season).classList.add("active");
    });
  });
  
  // Utility: Create match selector dropdown
  function createMatchSelector(seasonId, container, type, maxMatches) {
    if (container.querySelector(".match-select")) return;
  
    const select = document.createElement("select");
    select.classList.add("match-select");
    select.style.margin = "10px 0";
    for (let i = 1; i <= maxMatches; i++) {
      let option = document.createElement("option");
      option.value = i;
      option.textContent = `Match ${i.toString().padStart(3, "0")}`;
      select.appendChild(option);
    }
  
    select.addEventListener("change", () => {
      loadSeasonSubtabContent(seasonId, type, select.value, container);
    });
  
    container.prepend(select);
  }
  
  // Utility: Load the text file
  function loadSeasonSubtabContent(seasonId, type, matchNum, container) {
    container.textContent = "Loading...";
  
    let baseUrl = `https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_${seasonId}/`;
  
    let fileUrl = "";
    if (type === "flow") {
      fileUrl = `${baseUrl}Match_flows/ball-by-ball_${matchNum}.txt`;
    } else if (type === "scorecard") {
      const seasonPadded = seasonId.padStart(2, "0");
      const matchPadded = matchNum.toString().padStart(3, "0");
      fileUrl = `${baseUrl}Scorecards/matchcard_S${seasonPadded}M${matchPadded}.txt`;
    } else if (type === "graphs") {
      container.textContent = "Graphs will be shown here soon.";
      return;
    }
  
    fetch(fileUrl)
      .then(res => {
        if (!res.ok) throw new Error("File not found");
        return res.text();
      })
      .then(text => {
        container.textContent = text;
      })
      .catch(err => {
        container.textContent = "Error loading file.";
        console.error("Error loading file:", fileUrl, err);
      });
  }
  
  // Season subtabs logic
  document.querySelectorAll(".season-subtab").forEach(btn => {
    btn.addEventListener("click", () => {
      const parentTabs = btn.parentNode;
      parentTabs.querySelectorAll(".season-subtab").forEach(b => b.classList.remove("active"));
      const container = parentTabs.nextElementSibling.parentNode;
      container.querySelectorAll(".season-subtab-content").forEach(c => c.classList.remove("active"));
  
      btn.classList.add("active");
      const activeSubtabId = btn.dataset.subtab;
      const activeSubtabContent = container.querySelector("#" + activeSubtabId);
      activeSubtabContent.classList.add("active");
  
      const seasonContainer = btn.closest(".season-content");
      const seasonId = seasonContainer.id.split("-")[1];
  
      const existingSelect = activeSubtabContent.querySelector(".match-select");
      if (existingSelect) {
        existingSelect.remove();
      }
  
      if (activeSubtabId === "flow" || activeSubtabId === "scorecard") {
        const maxMatches = 74;
        createMatchSelector(seasonId, activeSubtabContent, activeSubtabId, maxMatches);
        loadSeasonSubtabContent(seasonId, activeSubtabId, 1, activeSubtabContent);
      } else if (activeSubtabId === "graphs") {
        activeSubtabContent.textContent = "Graphs will be shown here soon.";
      }
    });
  });
  