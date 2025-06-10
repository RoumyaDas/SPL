// Season tabs switching
document.querySelectorAll(".season-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".season-tab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".season-content").forEach(c => c.classList.remove("active"));
  
      btn.classList.add("active");
      document.getElementById("season-" + btn.dataset.season).classList.add("active");
    });
  });
  
  // Load the text file for a given season, type, and match number
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
  
  const tabDisplayNames = [
    "Orange-cap leaderboard", "Purple-cap leaderboard", "points table", "MVP", "Fantasy pts","Bowler ranking","Batter ranking",
     "Fielding","Most Dots",
    "Most 4s", "Most 6s", "Most_Run_Contribution", "Most_Wkt_Contribution", "Most_3wkt_hauls","Most_50+",
    "Lowest_Economy", "Best_Strike_Rate", "Team_best_Performance", "Match_Summary", "exit_pt_stats",
    "phase_bowl_stats", "Phase_wise_team_bowling", "Phase_wise_team_batting"
  ];

  
  // Create match selector dropdown
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

  function openMainTab(evt, tabName) {
    let tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    let tablinks = document.getElementsByTagName("a");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].classList.remove("active");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.classList.add("active");

    if (tabName === "Stats") {
        loadStatsTabs("s01"); // default load
    }
}

function openStatsSubTab(evt, subTabName) {
    let buttons = document.querySelectorAll("#Stats .subtabs button");
    buttons.forEach(btn => btn.classList.remove("active"));
    evt.currentTarget.classList.add("active");
    loadStatsTabs(subTabName);
}

function loadStatsTabs(seasonId) {
  const buttonContainer = document.getElementById("CSVTabButtons");
  const tableContainer = document.getElementById("CSVTableOutput");

  buttonContainer.innerHTML = "";
  tableContainer.innerHTML = "";

  for (let i = 1; i <= 23; i++) {
      let tabId = `TAB${String(i).padStart(2, '0')}`;
      let button = document.createElement("button");
      button.textContent = tabDisplayNames[i - 1] || tabId; // fallback if name missing
      button.onclick = () => loadCSVData(seasonId, tabId);
      buttonContainer.appendChild(button);
  }

  loadCSVData(seasonId, "TAB01");
}



function loadCSVData(seasonId, tabId) {
  const csvPath = `https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/${seasonId}/${tabId}.csv`;

  fetch(csvPath)
      .then(response => response.text())
      .then(data => {
          renderCSV(data);
      })
      .catch(error => {
          document.getElementById("CSVTableOutput").innerHTML = `<div>Error loading ${tabId}: ${error}</div>`;
      });
}

function renderFilteredTable(headers, rows) {
  const tableDiv = document.getElementById("csv-table-container");
  let html = `<table id="csv-table" border="1"><thead><tr>`;
  headers.forEach(header => html += `<th>${header}</th>`);
  html += `</tr></thead><tbody>`;
  for (let i = 0; i < rows.length; i++) {
      html += `<tr>`;
      rows[i].forEach(cell => html += `<td>${cell}</td>`);
      html += `</tr>`;
  }
  html += `</tbody></table>`;
  tableDiv.innerHTML = html;
}

function filterTable(query, headers, allRows) {
  const filtered = allRows.filter(row =>
      row.some(cell => cell.toLowerCase().includes(query))
  );
  renderFilteredTable(headers, filtered);
}


function renderCSV(csvText) {
  const tableContainer = document.getElementById("CSVTableOutput");
  tableContainer.innerHTML = "";

  const rows = csvText.trim().split("\n").map(row => row.split(","));
  const headers = rows[0];
  const dataRows = rows.slice(1);

  // 🔍 Create filter input box
  const filterInput = document.createElement("input");
  filterInput.type = "text";
  filterInput.placeholder = "Type to filter rows...";
  filterInput.style.marginBottom = "10px";
  filterInput.style.display = "block";
  filterInput.oninput = () => {
      filterTable(filterInput.value.toLowerCase(), headers, dataRows);
  };

  tableContainer.appendChild(filterInput);

  // Table rendering container
  const tableDiv = document.createElement("div");
  tableDiv.id = "csv-table-container";
  tableContainer.appendChild(tableDiv);

  renderFilteredTable(headers, dataRows); // initial full render
}

