// Season tabs switching
document.querySelectorAll(".season-tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".season-tab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".season-content").forEach(c => c.classList.remove("active"));

    btn.classList.add("active");
    document.getElementById("season-" + btn.dataset.season).classList.add("active");
  });
});

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



function loadSeasonSubtabContent(seasonId, type, matchNum, container) {
  container.textContent = "Loading...";

  let baseUrl = `https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_${seasonId}/`;
  let fileUrl = "";

  if (type === "flow") {
    fileUrl = `${baseUrl}Match_flows/ball-by-ball_${matchNum}.txt`;

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

  } else if (type.toLowerCase().startsWith("scorecard")) {
    const csvUrl = `https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Matchcards/Season_${seasonId}.csv`;

    fetch(csvUrl)
      .then(res => {
        if (!res.ok) throw new Error("CSV not found");
        return res.text();
      })
      .then(csv => {
        const rows = parseCustomCSV(csv);

        // Add filter input
        const searchInput = document.createElement("input");
        searchInput.type = "text";
        searchInput.placeholder = "Search...";
        searchInput.style.margin = "10px 0";
        container.innerHTML = "";
        container.appendChild(searchInput);

        // Add table
        const table = document.createElement("table");
        table.style.width = "100%";
        table.style.borderCollapse = "collapse";
        table.style.marginTop = "10px";

        const thead = document.createElement("thead");
        const tbody = document.createElement("tbody");
        table.appendChild(thead);
        table.appendChild(tbody);

        container.appendChild(table);

        const renderTable = (filteredRows) => {
          thead.innerHTML = "";
          tbody.innerHTML = "";

          const trHead = document.createElement("tr");
          headers.forEach(h => {
            const th = document.createElement("th");
            th.textContent = h;
            th.style.border = "1px solid #ddd";
            th.style.padding = "8px";
            th.style.background = "#f2f2f2";
            trHead.appendChild(th);
          });
          thead.appendChild(trHead);

          filteredRows.forEach(row => {
            const tr = document.createElement("tr");
            headers.forEach(h => {
              const td = document.createElement("td");
              td.textContent = row[h];
              td.style.border = "1px solid #ddd";
              td.style.padding = "8px";
              tr.appendChild(td);
            });
            tbody.appendChild(tr);
          });
        };

        // Initial render
        renderTable(rows);

        // Search logic
        searchInput.addEventListener("input", () => {
          const query = searchInput.value.toLowerCase();
          const filtered = rows.filter(row =>
            Object.values(row).some(val => val.toLowerCase().includes(query))
          );
          renderTable(filtered);
        });
      })
      .catch(err => {
        container.textContent = "Error loading CSV.";
        console.error("CSV fetch error:", err);
      });

  } else if (type === "graphs") {
    container.textContent = "Graphs will be shown here soon.";
  }
}




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
