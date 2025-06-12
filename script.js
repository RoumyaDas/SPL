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

function renderSpecialTable(tabKey, searchTerm = "") {
  const container = document.getElementById("special-table-container");
  container.innerHTML = "";

  const { headers, rows } = specialCsvData[tabKey] || {};
  if (!headers || !rows) {
    container.innerHTML = "<p>No data loaded.</p>";
    return;
  }

  let filteredRows = rows;
  if (searchTerm) {
    filteredRows = rows.filter(row =>
      headers.some(h => row[h]?.toLowerCase().includes(searchTerm.toLowerCase()))
    );
  }

  // Sorting
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

  // Table render
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

    // Add click handler
    th.addEventListener("click", () => {
      if (specialSortConfig.tabKey === tabKey && specialSortConfig.column === idx) {
        // Toggle order
        specialSortConfig.order = specialSortConfig.order === "asc" ? "desc" : "asc";
      } else {
        specialSortConfig = { tabKey, column: idx, order: "asc" };
      }
      renderSpecialTable(tabKey, document.getElementById("specialSearch").value);
    });

    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  filteredRows.slice(0, 20).forEach(row => {
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
    loadScorecard(matchNum);
  
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
  "Pitch-wise Bowler", "Bowl-type wise Batter", "stats7", "stats8",
  "stats9", "stats10", "stats11", "stats12", "stats13", "stats14",
  "stats15", "stats16", "stats17", "stats18",
  "stats19", "stats20", "stats21", "stats22", "stats23", "stats24",
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
  renderSpecialTable(tabKey, document.getElementById("specialSearch").value);
}

});




const tabDisplayNames = [
  "Orange-cap leaderboard", "Purple-cap leaderboard", "points table", "MVP", 
  "Impact_pts","Fantasy pts","Bowler ranking","Batter ranking",
   "Fielding","Most Dots",
  "Most 4s", "Most 6s", "Most_Run_Contribution", "Most_Wkt_Contribution", "Most_3wkt_hauls","Most_50+",
  "Lowest_Economy", "Best_Strike_Rate", "Team_best_Performance", "Match_Summary", 
  "exit_pt_stats",
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

    if (activeSubtabId.startsWith("flow") || activeSubtabId.startsWith("scorecard")) {

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
      loadStatsTabs("S01"); // default load
  }
}

function openStatsSubTab(evt, subTabName) {
  // 1. Remove active class from all subtab buttons
  let buttons = document.querySelectorAll("#Stats .subtabs button");
  buttons.forEach(btn => btn.classList.remove("active"));

  // 2. Add active class to the clicked button
  evt.currentTarget.classList.add("active");

  // 3. Hide all tab contents inside #StatsSubContent
  const allTabSections = document.querySelectorAll("#StatsSubContent > div");
  allTabSections.forEach(div => div.style.display = "none");

  // 4. Show the selected subTab content if it exists
  const activeTab = document.getElementById(subTabName);
  if (activeTab) activeTab.style.display = "block";

  // 5. Load the data
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
