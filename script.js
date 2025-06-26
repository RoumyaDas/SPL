// news section
let currentPage = 1;
const pageSize = 10;


// Season tabs switching
document.querySelectorAll(".season-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".season-tab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".season-content").forEach(c => c.classList.remove("active"));

    btn.classList.add("active");
    document.getElementById("season-" + btn.dataset.season).classList.add("active");
  });
});

const specialCsvBase = "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/special_stats/";
let specialCsvData = {}; // cache

const tabKeys = Array.from({ length: 25 }, (_, i) => `tab${i + 1}`);
// tabs for special stats, change if length needs to be changed

const parseCustomCSV = (csv) => {
  const lines = [];
  let currentLine = "";
  let insideQuotes = false;

  const chars = csv.trim().split("");

  for (let i = 0; i < chars.length; i++) {
    const c = chars[i];

    if (c === '"') {
      insideQuotes = !insideQuotes;
    }

    if (c === '\n' && !insideQuotes) {
      lines.push(currentLine);
      currentLine = "";
    } else {
      currentLine += c;
    }
  }

  if (currentLine) lines.push(currentLine); // last line

  const headers = splitSafe(lines[0]);

  const rows = lines.slice(1).map(line => {
    const values = splitSafe(line);
    return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
  });

  return rows;
};
function parseCSV(text) {
  const lines = text.trim().split("\n");
  const headers = lines[0].split(",");
  const rows = lines.slice(1).map(line => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
  });
  return { headers, rows };
}

function openTab(evt, tabName) {
  // Hide all tab content sections
  const tabcontent = document.getElementsByClassName("tabcontent");
  for (let i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }

  // Remove "active" class from all tab buttons
  const tablinks = document.getElementsByClassName("tablinks");
  for (let i = 0; i < tablinks.length; i++) {
    tablinks[i].classList.remove("active");
  }

  // Show the clicked tab
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.classList.add("active");
}


function splitSafe(line) {
  const parts = [];
  let current = "";
  let insideQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const c = line[i];

    if (c === '"') {
      insideQuotes = !insideQuotes;
    }

    if (line[i] === "$" && !insideQuotes) {
      parts.push(current);
      current = "";
    } else {
      current += c;
    }
  }

  parts.push(current);
  return parts.map(p => p.replace(/^"|"$/g, "")); // remove outer quotes
}


let specialSortConfig = { tabKey: "", column: null, order: "asc" };

function renderSpecialTable(tabKey, searchTerm = "", page = 1) {
  const container = document.getElementById("special-table-container");
  container.innerHTML = "";

  const { headers, rows } = specialCsvData[tabKey] || {};
  if (!headers || !rows) {
    container.innerHTML = "<p>No data loaded.</p>";
    return;
  }

  // 🔍 Filter rows
  let filteredRows = rows;
  if (searchTerm) {
    filteredRows = rows.filter(row =>
      headers.some(h => row[h]?.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }

  // 🔃 Sort if configured
  if (specialSortConfig.tabKey === tabKey && specialSortConfig.column !== null) {
    const h = headers[specialSortConfig.column];
    const order = specialSortConfig.order;
    filteredRows.sort((a, b) => {
      const aVal = a[h], bVal = b[h];
      const isNum = !isNaN(parseFloat(aVal)) && !isNaN(parseFloat(bVal));
      if (isNum) {
        return order === "asc" ? aVal - bVal : bVal - aVal;
      }
      return order === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }

  // 📄 Create table
  const table = document.createElement("table");
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  headers.forEach((h, idx) => {
    const th = document.createElement("th");
    th.textContent = h;
    th.style.cursor = "pointer";
    th.style.border = "1px solid #ccc";
    th.style.padding = "4px";

    // Add sort indicator
    if (specialSortConfig.tabKey === tabKey && specialSortConfig.column === idx) {
      th.textContent += specialSortConfig.order === "asc" ? " ▲" : " ▼";
    }

    th.addEventListener("click", () => {
      if (specialSortConfig.tabKey === tabKey && specialSortConfig.column === idx) {
        specialSortConfig.order = specialSortConfig.order === "asc" ? "desc" : "asc";
      } else {
        specialSortConfig = { tabKey, column: idx, order: "asc" };
      }
      renderSpecialTable(tabKey, document.getElementById("specialSearch").value, 1);
    });

    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  // ⬇️ Paginate rows
  const rowsPerPage = 20;
  const start = (page - 1) * rowsPerPage;
  const currentRows = filteredRows.slice(start, start + rowsPerPage);

  const tbody = document.createElement("tbody");
  currentRows.forEach(row => {
    const tr = document.createElement("tr");
    headers.forEach(h => {
      const td = document.createElement("td");
      td.textContent = row[h];
      td.style.border = "1px solid #ccc";
      td.style.padding = "4px";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.appendChild(table);

  // 📌 Pagination controls
  const pagination = document.getElementById("special-pagination");
  pagination.innerHTML = renderPagination(filteredRows.length, rowsPerPage, page);
  pagination.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", () => {
      const newPage = parseInt(btn.dataset.page);
      renderSpecialTable(tabKey, searchTerm, newPage);
    });
  });
}




function loadSeasonSubtabContent(seasonId, type, matchNum, container) {
  container.textContent = "Loading...";

  let baseUrl = `https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_${seasonId}/`;
  let fileUrl = "";

  if (type.toLowerCase().startsWith("flow")) {
    // Clear the container
    container.innerHTML = "";
  
    // Create match number dropdown
    const matchSelector = document.createElement("select");
    for (let i = 1; i <= 74; i++) {
      const option = document.createElement("option");
      const matchId = `${i}`;

      option.value = matchId;
      option.textContent = `Match ${matchId}`;
      if (matchId === matchNum) option.selected = true;
      matchSelector.appendChild(option);
    }
  
    // Create search input
    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = "Search within flow...";
    searchInput.style.margin = "10px";
  
    // Create display area (using <pre> for proper formatting)
    const flowDisplay = document.createElement("pre");
    flowDisplay.style.whiteSpace = "pre-wrap";
    flowDisplay.style.border = "1px solid #ccc";
    flowDisplay.style.padding = "10px";
    flowDisplay.textContent = "Loading...";
  
    container.appendChild(matchSelector);
    container.appendChild(searchInput);
    container.appendChild(flowDisplay);
  
    const loadMatchFlow = (matchId) => {
      const fileUrl = `${baseUrl}Match_flows/ball-by-ball_${matchId}.txt`;
  
      fetch(fileUrl)
        .then(res => {
          if (!res.ok) throw new Error("File not found");
          return res.text();
        })
        .then(text => {
          flowDisplay.textContent = text;
          flowDisplay.dataset.raw = text; // store original for search
        })
        .catch(err => {
          flowDisplay.textContent = "Error loading file.";
          console.error("Error loading file:", fileUrl, err);
        });
    };
  
    // Initial load
    loadMatchFlow(matchNum);
  
    // Match number selection change
    matchSelector.addEventListener("change", () => {
      const selected = matchSelector.value;
      loadMatchFlow(selected);
    });
  
    // Search filtering
    searchInput.addEventListener("input", () => {
      const rawText = flowDisplay.dataset.raw || "";
      const query = searchInput.value.toLowerCase();
      if (!query) {
        flowDisplay.textContent = rawText;
      } else {
        const filtered = rawText
          .split("\n")
          .filter(line => line.toLowerCase().includes(query))
          .join("\n");
        flowDisplay.textContent = filtered;
      }
    });
  }


  else if (type.toLowerCase().startsWith("scorecard")) {
    // Clear container
    container.innerHTML = "";
  
    // Match selector dropdown
    const matchSelector = document.createElement("select");
    for (let i = 1; i <= 74; i++) {
      const option = document.createElement("option");
      const matchId = i < 10 ? `0${i}` : `${i}`;
      option.value = matchId;
      option.textContent = `Match ${matchId}`;
      if (matchId === matchNum) option.selected = true;
      matchSelector.appendChild(option);
    }
  
    // Search input
    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = "Search scorecard...";
    searchInput.style.margin = "10px";
  
    // Text display area
    const scorecardDisplay = document.createElement("pre");
    scorecardDisplay.style.whiteSpace = "pre-wrap";
    scorecardDisplay.style.border = "1px solid #ccc";
    scorecardDisplay.style.padding = "10px";
    scorecardDisplay.textContent = "Loading...";
  
    // Append UI
    container.appendChild(matchSelector);
    container.appendChild(searchInput);
    container.appendChild(scorecardDisplay);
  
    // Load scorecard from txt
    const loadScorecard = (matchId) => {
      
      let fileUrl = "";

      if (String(seasonId).startsWith("01")) {
        fileUrl = `${baseUrl}Scorecards/matchcard_M0${matchId}.txt`;
      } else {
        fileUrl = `${baseUrl}Scorecards/matchcard_S${seasonId}M0${matchId}.txt`;
      }

  
      fetch(fileUrl)
        .then(res => {
          if (!res.ok) throw new Error("File not found");
          return res.text();
        })
        .then(text => {
          scorecardDisplay.textContent = text;
          scorecardDisplay.dataset.raw = text;
        })
        .catch(err => {
          scorecardDisplay.textContent = "Error loading file.";
          console.error("Scorecard file error:", fileUrl, err);
        });
    };
  
    // Initial load
    //loadScorecard(matchNum);
    loadScorecard('01');
  
    // Match selector change
    matchSelector.addEventListener("change", () => {
      const selected = matchSelector.value;
      loadScorecard(selected);
      searchInput.value = "";
    });
  
    // Search inside scorecard
    searchInput.addEventListener("input", () => {
      const rawText = scorecardDisplay.dataset.raw || "";
      const query = searchInput.value.toLowerCase();
      if (!query) {
        scorecardDisplay.textContent = rawText;
      } else {
        const filtered = rawText
          .split("\n")
          .filter(line => line.toLowerCase().includes(query))
          .join("\n");
        scorecardDisplay.textContent = filtered;
      }
    });
  }
   else if (type === "graphs") {
    container.textContent = "Graphs will be shown here soon.";
  }
}

const tabSpecialstatsnames = [
  "Phase-wise Batter", "Phase-wise Bowler", "Inning-wise Bowler", "Inning-wise Batter",
  "Pitch-wise Bowler", "Bowl-type wise Batter", "Fastest-100", "Fastest-50",
  "Fastest-5W-haul", "Fastest_3W-haul", "Pitch-Inning-wise Win%", 
  "Form_inning_1 Batter", "Form_inning_2 Batter", "Form_inning_1 Bowler",
  "Form_inning_2 Bowler", "Venue stats", "Pos.n-wise Batter (min. 100 balls)", "H2H stats (min. 15 balls)",
  "Partnership stats (min. 50 balls)", "Home-Away record", "Venue-wise Bowler", "Venue-wise Batter",
  "Indi. Impact list (>=50 pts)", "stats24",
  "stats25" // fill with whatever name you want
];



const specialSubtabs = document.getElementById("special-subtabs");

tabKeys.forEach((tabKey, i) => {
  const displayName = tabSpecialstatsnames[i] || tabKey;

  const button = document.createElement("button");
  button.textContent = displayName;
  button.dataset.tabkey = tabKey;

  button.addEventListener("click", () => {
    document.querySelectorAll("#special-subtabs button").forEach(b => b.classList.remove("active"));
    button.classList.add("active");
    renderSpecialTable(tabKey, document.getElementById("specialSearch").value);
  });

  specialSubtabs.appendChild(button);

  fetch(`${specialCsvBase}${tabKey}.csv`)
    .then(res => res.text())
    .then(text => {
      specialCsvData[tabKey] = parseCSV(text);
      if (i === 0) {
        button.classList.add("active");
        renderSpecialTable(tabKey);
      }
    });
});


document.getElementById("specialSearch").addEventListener("input", () => {
  const activeTab = document.querySelector("#special-subtabs button.active");
const tabKey = activeTab?.dataset.tabkey;
if (tabKey) {
  // renderSpecialTable(tabKey, document.getElementById("specialSearch").value);
  renderSpecialTable(tabKey, document.getElementById("specialSearch").value, 1);

}

});




// Stats tab data
const statsCsvBase = "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/";
const statsDisplayNames = [
  "Orange-cap leaderboard", "Purple-cap leaderboard", "points table", "MVP", 
  "Impact_pts","Fantasy pts","Bowler ranking","Batter ranking",
  "Fielding","Most Dots",
  "Most 4s", "Most 6s", "Most_Run_Contribution", "Most_Wkt_Contribution", "Most_3wkt_hauls","Most_50+",
  "Lowest_Economy (min. 4 ovs)", "Best_Strike_Rate (min. 50 runs)", 
  "Team_best_Performance", "Match_Summary", 
  "exit_pt_stats",
  "phase_bowl_stats", "Phase_wise_team_bowling", "Phase_wise_team_batting",
  "Partnership_stats (min. 20 balls)"
];


let statsCsvData = {}; // cache
let statsSortConfig = { season: "", tab: "", column: null, order: "asc" };

// Initialize Stats tab
function initStatsTab() {
  const seasonTabs = document.getElementById("stats-season-tabs");
  const statsSubtabs = document.getElementById("stats-subtabs");
  
  // Create season tabs
  ['S01', 'S02', 'S03'].forEach(season => {
    const btn = document.createElement("button");
    btn.textContent = `Season ${season.slice(1)}`;
    btn.dataset.season = season;
    btn.addEventListener("click", () => switchStatsSeason(season));
    seasonTabs.appendChild(btn);
  });

  // Create stats subtabs
  statsDisplayNames.forEach((name, i) => {
    const tabId = `TAB${String(i+1).padStart(2, '0')}`;
    const btn = document.createElement("button");
    btn.textContent = name;
    btn.dataset.tab = tabId;
    btn.addEventListener("click", function() {
      // Remove active from all stats subtabs
      document.querySelectorAll("#stats-subtabs button").forEach(b => b.classList.remove("active"));
      // Add active to this button
      btn.classList.add("active");
      renderStatsTable(
        document.querySelector("#stats-season-tabs button.active").dataset.season,
        tabId
      );
    });
    statsSubtabs.appendChild(btn);
  });

  // Set up search
  document.getElementById("statsSearch").addEventListener("input", () => {
    const activeSeason = document.querySelector("#stats-season-tabs button.active").dataset.season;
    const activeTab = document.querySelector("#stats-subtabs button.active").dataset.tab;
    if (activeSeason && activeTab) {
      renderStatsTable(activeSeason, activeTab, document.getElementById("statsSearch").value);
    }
  });

  // Load initial data
  switchStatsSeason('S01');
}

function switchStatsSeason(season) {
  // Update active season tab
  document.querySelectorAll("#stats-season-tabs button").forEach(btn => 
    btn.classList.toggle("active", btn.dataset.season === season)
  );

  // Remove "active" from all stats subtabs
  document.querySelectorAll("#stats-subtabs button").forEach(b => b.classList.remove("active"));

  // Load first tab for this season and set it active
  const firstTab = document.querySelector("#stats-subtabs button");
  if (firstTab) {
    firstTab.classList.add("active");
    renderStatsTable(season, firstTab.dataset.tab);
  }
}



function renderStatsTable(season, tabId, searchTerm = "") {
  const container = document.getElementById("stats-table-container");
  container.innerHTML = "";

  // Check if data is cached
  const cacheKey = `${season}_${tabId}`;
  if (statsCsvData[cacheKey]) {
    renderStatsTableFromCache(cacheKey, searchTerm);
    return;
  }

  // Fetch data if not cached
  const url = `${statsCsvBase}${season}/${tabId}.csv`;
  fetch(url)
    .then(res => res.text())
    .then(text => {
      const data = parseCSV(text);
      statsCsvData[cacheKey] = data;
      renderStatsTableFromCache(cacheKey, searchTerm);
    })
    .catch(err => {
      container.innerHTML = `<p>Error loading data: ${err.message}</p>`;
    });
}

function renderStatsTableFromCache(cacheKey, searchTerm = "", page = 1) {
  const container = document.getElementById("stats-table-container");
  container.innerHTML = "";

  const { headers, rows } = statsCsvData[cacheKey] || {};
  if (!headers || !rows) {
    container.innerHTML = "<p>No data loaded.</p>";
    return;
  }

  // 🔍 Filter
  let filteredRows = rows;
  if (searchTerm) {
    filteredRows = rows.filter(row =>
      headers.some(h => row[h]?.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }

  // 🔃 Sort
  if (statsSortConfig.column !== null) {
    const h = headers[statsSortConfig.column];
    const order = statsSortConfig.order;
    filteredRows.sort((a, b) => {
      const aVal = a[h], bVal = b[h];
      const isNum = !isNaN(parseFloat(aVal)) && !isNaN(parseFloat(bVal));
      if (isNum) {
        return order === "asc" ? aVal - bVal : bVal - aVal;
      }
      return order === "asc"
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }

  // 📄 Table
  const table = document.createElement("table");
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  headers.forEach((h, idx) => {
    const th = document.createElement("th");
    th.textContent = h;
    th.style.cursor = "pointer";
    th.style.border = "1px solid #ccc";
    th.style.padding = "4px";

    // Sort indicator
    if (statsSortConfig.column === idx) {
      th.textContent += statsSortConfig.order === "asc" ? " ▲" : " ▼";
    }

    th.addEventListener("click", () => {
      if (statsSortConfig.column === idx) {
        statsSortConfig.order = statsSortConfig.order === "asc" ? "desc" : "asc";
      } else {
        statsSortConfig.column = idx;
        statsSortConfig.order = "asc";
      }
      renderStatsTableFromCache(cacheKey, searchTerm, 1); // reset to page 1 on sort
    });

    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  // ⬇️ Pagination logic
  const rowsPerPage = 20;
  const start = (page - 1) * rowsPerPage;
  const currentRows = filteredRows.slice(start, start + rowsPerPage);

  const tbody = document.createElement("tbody");
  currentRows.forEach(row => {
    const tr = document.createElement("tr");
    headers.forEach(h => {
      const td = document.createElement("td");
      td.textContent = row[h];
      td.style.border = "1px solid #ccc";
      td.style.padding = "4px";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.appendChild(table);

  // ➕ Pagination control
  const pagination = document.getElementById("stats-pagination");
  pagination.innerHTML = renderPagination(filteredRows.length, rowsPerPage, page);
  pagination.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", () => {
      const newPage = parseInt(btn.dataset.page);
      renderStatsTableFromCache(cacheKey, searchTerm, newPage);
    });
  });
}


// Initialize when DOM is loaded
// document.addEventListener("DOMContentLoaded", initStatsTab);

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

    // Remove existing select dropdowns (Flow, Scorecard, Impact)
    const existingSelect = activeSubtabContent.querySelector(".match-select");
    if (existingSelect) {
      existingSelect.remove();
    }

    const maxMatches = 74;

    if (activeSubtabId.startsWith("flow") || activeSubtabId.startsWith("scorecard")) {
      createMatchSelector(seasonId, activeSubtabContent, activeSubtabId, maxMatches);
      loadSeasonSubtabContent(seasonId, activeSubtabId, 1, activeSubtabContent);
    } 
    
    else if (activeSubtabId.startsWith("impact")) {
      // Create dropdown dynamically
      const select = document.createElement("select");
      select.className = "match-select";
      select.style.marginBottom = "10px";
      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "-- Select a match --";
      select.appendChild(defaultOption);

      for (let i = 1; i <= maxMatches; i++) {
        const matchNum = i.toString().padStart(3, '0');
        const matchId = `S03M${matchNum}`;
        const opt = document.createElement("option");
        opt.value = matchId;
        opt.textContent = `Match ${matchNum}`;
        select.appendChild(opt);
      }

      const pre = activeSubtabContent.querySelector("pre") || document.createElement("pre");
      pre.id = "impactContent";
      pre.className = "subtab-pre-content";

      activeSubtabContent.innerHTML = ""; // Clear old content
      activeSubtabContent.appendChild(select);
      activeSubtabContent.appendChild(pre);

      pre.textContent = "Please select a match.";

      select.addEventListener("change", () => {
        const matchId = select.value;
        if (!matchId) {
          pre.textContent = "Please select a match.";
          return;
        }

        const url = `https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_03/total_impact/${matchId}_impact.txt`;

        fetch(url)
          .then(res => {
            if (!res.ok) throw new Error("File not found");
            return res.text();
          })
          .then(text => {
            pre.textContent = text;
          })
          .catch(() => {
            pre.textContent = "Impact file not found for " + matchId;
          });
      });
    }

    // If future subtabs like "graphs" return:
    else if (activeSubtabId === "graphs") {
      activeSubtabContent.textContent = "Graphs will be shown here soon.";
    }
  });
});







function setupSearch(headers, data) {
  const searchInput = document.getElementById("csv-search");
  const tableDiv = document.getElementById("csv-table-container");

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();

    const filteredRows = data.filter(row =>
      row.some(cell => cell.toLowerCase().includes(query))
    );

    renderFilteredTable(headers, filteredRows); // Renders all matched rows
  });
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

let currentSort = { columnIndex: null, ascending: true };

function renderFilteredTable(headers, rows, onlyFirstRow = false) {

const tableDiv = document.getElementById("csv-table-container");

// Show only first 20 rows
const visibleRows = onlyFirstRow ? rows.slice(0, 1) : rows;


let html = `
  <table id="csv-table" style="
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
    font-family: Arial, sans-serif;
    font-size: 14px;
  ">
    <thead>
      <tr style="background-color: #f2f2f2;">
`;

headers.forEach((header, index) => {
  html += `<th style="
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
    cursor: pointer;
  " onclick="sortTable(${index})">${header} &#x25B4;&#x25BE;</th>`;
});

html += `</tr></thead><tbody>`;

for (let i = 0; i < visibleRows.length; i++) {
  html += `<tr style="background-color: ${i % 2 === 0 ? '#ffffff' : '#fafafa'};">`;
  visibleRows[i].forEach(cell => {
    html += `<td style="
      border: 1px solid #ddd;
      padding: 8px;
    ">${cell}</td>`;
  });
  html += `</tr>`;
}

html += `</tbody></table>`;
tableDiv.innerHTML = html;

// Store latest headers & full rows for future sorting
tableDiv.dataset.headers = JSON.stringify(headers);
tableDiv.dataset.rows = JSON.stringify(rows);
}

function sortTable(colIndex) {
  const tableDiv = document.getElementById("csv-table-container");
  const headers = JSON.parse(tableDiv.dataset.headers);
  let rows = JSON.parse(tableDiv.dataset.rows);

  // Determine current sort direction (asc/desc) by tracking it per column
  if (!sortTable.directions) sortTable.directions = {};
  sortTable.directions[colIndex] = !sortTable.directions[colIndex]; // toggle

  const isAsc = sortTable.directions[colIndex];

  rows.sort((a, b) => {
    const valA = a[colIndex].toLowerCase();
    const valB = b[colIndex].toLowerCase();
    
    if (!isNaN(valA) && !isNaN(valB)) {
      return isAsc ? valA - valB : valB - valA;
    }

    return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
  });

  // Re-render with sorted rows (again only showing first 20)
  renderFilteredTable(headers, rows);
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
// Initialize Stats Tab when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  initStatsTab();



// Enhanced main tab switching (hides everything else)
document.querySelectorAll(".main-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    // Deactivate all main tabs
    document.querySelectorAll(".main-tab").forEach(b => b.classList.remove("active"));

    // Hide all tab content blocks
    document.querySelectorAll(".tab-content").forEach(t => {
      t.classList.remove("active");
      t.style.display = "none";
    });

    // Activate the clicked tab
    btn.classList.add("active");

    const targetTab = document.getElementById(btn.dataset.tab);
    targetTab.classList.add("active");
    targetTab.style.display = "block";
  });
});
});


// --- Schedule Tab Functionality ---

const scheduleCSVs = {
  "sch-s01": "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Fixtures/schedule_S01.csv",
  "sch-s02": "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Fixtures/schedule_S02.csv",
  "sch-s03": "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Fixtures/schedule_S03.csv"
};

const scheduleCache = {};  // to store loaded CSVs

function parseScheduleCSV(csvText) {
  const lines = csvText.trim().split("\n");
  const headers = lines[0].split(",");
  const rows = lines.slice(1).map(line => line.split(","));
  return { headers, rows };
}

function renderScheduleTable(tabId, data) {
  const container = document.getElementById(tabId);
  container.innerHTML = "";

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  const headerRow = document.createElement("tr");
  data.headers.forEach(h => {
    const th = document.createElement("th");
    th.textContent = h;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  data.rows.forEach(row => {
    const tr = document.createElement("tr");
    row.forEach(val => {
      const td = document.createElement("td");
      td.textContent = val;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  container.appendChild(table);
}

// Subtab switching for schedule
document.querySelectorAll(".schedule-subtab").forEach(btn => {
  btn.addEventListener("click", () => {
    const tabId = btn.dataset.tab;

    // Toggle active classes
    document.querySelectorAll(".schedule-subtab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".schedule-table-container").forEach(div => div.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(tabId).classList.add("active");

    // Lazy-load if not already loaded
    if (!scheduleCache[tabId]) {
      fetch(scheduleCSVs[tabId])
        .then(res => res.text())
        .then(csv => {
          const parsed = parseScheduleCSV(csv);
          scheduleCache[tabId] = parsed;
          renderScheduleTable(tabId, parsed);
        });
    }
  });
});

// Default: show only S01 tab and trigger its load
document.querySelector(".schedule-subtab.active").click();

// Current Squads tab
const teamList = ["CSK", "DC", "GT", "KKR", "LSG", "MI", "PBKS", "RR", "RCB", "SRH"];
const squadBaseUrl = "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Squads/";

function renderSquadTable(team, data) {
  const container = document.getElementById(team);
  const table = document.createElement("table");

  // Create table header
  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  data.headers.forEach((h, idx) => {
    const th = document.createElement("th");
    th.textContent = h;
    th.style.cursor = "pointer";

    th.addEventListener("click", () => {
      const sortedRows = [...data.rows].sort((a, b) => {
        const aVal = a[h] ?? "";
        const bVal = b[h] ?? "";
        const isNumeric = !isNaN(aVal) && !isNaN(bVal);
        return isNumeric
          ? parseFloat(aVal) - parseFloat(bVal)
          : aVal.localeCompare(bVal);
      });

      renderSquadTable(team, { headers: data.headers, rows: sortedRows });
    });

    headRow.appendChild(th);
  });
  thead.appendChild(headRow);

  // Create table body
  const tbody = document.createElement("tbody");
  data.rows.forEach(row => {
    const tr = document.createElement("tr");
    data.headers.forEach(h => {
      const td = document.createElement("td");
      td.textContent = row[h] ?? "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);

  container.innerHTML = "";
  container.appendChild(table);
}


// Load all team CSVs once
teamList.forEach(team => {
  fetch(`${squadBaseUrl}${team}.csv`)
    .then(res => res.text())
    .then(text => {
      const data = parseCSV(text);
      renderSquadTable(team, data);
    });
});

// Subtab switching logic
document.querySelectorAll(".squad-subtab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".squad-subtab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".squad-table-container").forEach(div => div.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
  });
});

// --- Combined Points Table Tab ---
const combinedCsvUrl = "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/combined_pts_table.csv";

function renderCombinedTable(headers, rows, searchTerm = "") {
  const container = document.getElementById("combined-table-container");
  container.innerHTML = "";

  // Filter rows by search
  const filtered = searchTerm
    ? rows.filter(row => row[0].toLowerCase().includes(searchTerm.toLowerCase()))
    : rows;

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  // Header row
  const trHead = document.createElement("tr");
  headers.forEach(h => {
    const th = document.createElement("th");
    th.textContent = h;
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);

  // All rows (no slicing)
  filtered.forEach(row => {
    const tr = document.createElement("tr");
    row.forEach(val => {
      const td = document.createElement("td");
      td.textContent = val;
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  container.appendChild(table);
}

// Load and render combined CSV
fetch(combinedCsvUrl)
  .then(res => res.text())
  .then(csv => {
    const lines = csv.trim().split("\n");
    const headers = lines[0].split(",");
    const rows = lines.slice(1).map(line => line.split(","));

    renderCombinedTable(headers, rows);

    document.getElementById("combinedSearch").addEventListener("input", (e) => {
      renderCombinedTable(headers, rows, e.target.value);
    });
  });



function renderPagination(totalRows, rowsPerPage, currentPage, onPageChange) {
  const totalPages = Math.ceil(totalRows / rowsPerPage);
  if (totalPages <= 1) return "";

  let html = `<div class="pagination-buttons">`;
  if (currentPage > 1) html += `<button data-page="${currentPage - 1}">Prev</button>`;
  for (let i = 1; i <= totalPages; i++) {
    html += `<button data-page="${i}" ${i === currentPage ? "class='active'" : ""}>${i}</button>`;
  }
  if (currentPage < totalPages) html += `<button data-page="${currentPage + 1}">Next</button>`;
  html += `</div>`;

  return html;
}
  
/// NEWS tab stuff
document.addEventListener("DOMContentLoaded", () => {
  const newsList = document.getElementById("news-list");
  const detailTitle = document.querySelector(".news-detail-title");
  const detailBody = document.querySelector(".news-detail-body");
  const searchInput = document.getElementById("newsSearch");

  const newsFiles = [
    "240625_MI_injury.txt",
    "250625_PBKS_GT_thriller.txt",
    "260625_LSG_Stokes_missing.txt",
    "230625_GT_RCB_thriller.txt",
    "250625_recap.txt",
    "160625_SRH_MI_recap.txt"
  ];

  const newsData = []; // will store all stories

  // Sort by date in filename
  const sortedNewsFiles = [...newsFiles].sort((a, b) => {
    const getSortableDate = (filename) => {
      const match = filename.match(/^(\d{2})(\d{2})(\d{2})_/); // captures DDMMYY_
      if (!match) return new Date(0); // fail-safe
      const [_, dd, mm, yy] = match;
      return new Date(`20${yy}-${mm}-${dd}`);
    };
    return getSortableDate(b) - getSortableDate(a); // Newest first
  });
  

  sortedNewsFiles.forEach(filename => {
    fetch(`https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/news/${filename}`)
      .then(res => res.ok ? res.text() : null)
      .then(text => {
        if (!text) return;
        const lines = text.trim().split("\n");
        const title = lines[0] || "Untitled";
        const body = lines.slice(1).join("\n");

        newsData.push({ filename, title, body });
        renderNewsList(newsData, searchInput.value.trim().toLowerCase());
      });
  });

  function renderNewsList(data, filter) {
    const newsList = document.getElementById("news-list");
    const pagination = document.getElementById("news-pagination");
  
    const filtered = data.filter(story =>
      story.title.toLowerCase().includes(filter) ||
      story.body.toLowerCase().includes(filter)
    );
  
    const totalPages = Math.ceil(filtered.length / pageSize);
    currentPage = Math.min(currentPage, totalPages) || 1;
  
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedData = filtered.slice(startIndex, endIndex);
  
    newsList.innerHTML = "";
    pagination.innerHTML = "";
  
    paginatedData.forEach(({ filename, title, body }) => {
      const card = document.createElement("div");
      card.className = "news-card";
      card.textContent = title;
  
      card.addEventListener("click", () => {
        detailTitle.textContent = title;
        detailBody.textContent = body;
        window.location.hash = filename.replace(".txt", "");
      });
  
      newsList.appendChild(card);
    });
  
    if (filtered.length === 0) {
      newsList.innerHTML = `<div style="color:#666; font-style: italic;">No news matched your search.</div>`;
      detailTitle.textContent = "Select a news item";
      detailBody.textContent = "Full story will appear here.";
      return;
    }
  
    // Pagination controls
    if (totalPages > 1) {
      const prevBtn = document.createElement("button");
      prevBtn.textContent = "← Prev";
      prevBtn.disabled = currentPage === 1;
      prevBtn.onclick = () => {
        currentPage--;
        renderNewsList(data, filter);
      };
  
      const nextBtn = document.createElement("button");
      nextBtn.textContent = "Next →";
      nextBtn.disabled = currentPage === totalPages;
      nextBtn.onclick = () => {
        currentPage++;
        renderNewsList(data, filter);
      };
  
      pagination.appendChild(prevBtn);
  
      const pageInfo = document.createElement("span");
      pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
      pageInfo.style.padding = "0 10px";
      pagination.appendChild(pageInfo);
  
      pagination.appendChild(nextBtn);
    }
  }
  

  searchInput.addEventListener("input", () => {
    currentPage = 1;  // reset to first page on new search
    const filter = searchInput.value.trim().toLowerCase();
    renderNewsList(newsData, filter);
  });
  

  // Optional: Load story from URL hash
  const hash = window.location.hash.replace("#", "");
  if (hash) {
    fetch(`https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/news/${hash}.txt`)
      .then(res => res.ok ? res.text() : null)
      .then(text => {
        if (!text) return;
        const lines = text.trim().split("\n");
        detailTitle.textContent = lines[0];
        detailBody.textContent = lines.slice(1).join("\n");
      });
  }
});
