// Tab navigation for main tabs
document.querySelectorAll(".main-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".main-tab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
    });
  });
  
  // CSV File URLs
  const csvUrls = {
    batting: "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_03/career/batting.csv",
    bowling: "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_03/career/bowling.csv",
    fielding: "https://raw.githubusercontent.com/RoumyaDas/SPL/main/SPL/data/Season_03/career/fielding.csv"
  };
  
  const csvData = {};
  
  // Parse CSV text into headers + rows of objects
  function parseCSV(csvText) {
    const lines = csvText.trim().split("\n");
    const headers = lines[0].split(",");
    const rows = lines.slice(1).map(line => {
      const values = line.split(",");
      return Object.fromEntries(headers.map((h, i) => [h, values[i]]));
    });
    return { headers, rows };
  }
  
  // Render career section table with sorting and filtering
  function renderCareerSection(type, data, searchTerm = "", sortConfig = {}) {
    const head = document.getElementById(`${type}Head`);
    const body = document.getElementById(`${type}Body`);
    head.innerHTML = "";
    body.innerHTML = "";
  
    // Header row with clickable sorting
    const tr = document.createElement("tr");
    data.headers.forEach((h, idx) => {
      const th = document.createElement("th");
      th.textContent = h;
      th.style.cursor = "pointer";
  
      // Add sort indicator
      if (sortConfig.column === idx) {
        th.textContent += sortConfig.order === "asc" ? " ▲" : " ▼";
      }
  
      th.addEventListener("click", () => {
        const currentOrder = (sortConfig.column === idx && sortConfig.order === "asc") ? "desc" : "asc";
  
        const sortedRows = [...data.rows].sort((a, b) => {
          const aVal = a[h] || "";
          const bVal = b[h] || "";
          const aNum = parseFloat(aVal);
          const bNum = parseFloat(bVal);
          const isNumeric = !isNaN(aNum) && !isNaN(bNum);
  
          if (isNumeric) {
            return currentOrder === "asc" ? aNum - bNum : bNum - aNum;
          } else {
            return currentOrder === "asc"
              ? aVal.localeCompare(bVal)
              : bVal.localeCompare(aVal);
          }
        });
  
        renderCareerSection(type, { headers: data.headers, rows: sortedRows }, document.getElementById("careerSearch").value, {
          column: idx,
          order: currentOrder
        });
      });
  
      tr.appendChild(th);
    });
    head.appendChild(tr);
  
    // Filter rows based on searchTerm on first column (player name)
    let filtered = data.rows;
    if (searchTerm) {
      filtered = filtered.filter(row =>
        row[data.headers[0]].toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
  
    // Show max 20 rows
    filtered.slice(0, 20).forEach(row => {
      const tr = document.createElement("tr");
      data.headers.forEach(h => {
        const td = document.createElement("td");
        td.textContent = row[h] || "";
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
  }
  
  // Fetch all CSV data initially
  for (let type in csvUrls) {
    fetch(csvUrls[type])
      .then(res => res.text())
      .then(text => {
        const parsed = parseCSV(text);
        csvData[type] = parsed;
        if (type === "batting") {
          renderCareerSection("batting", parsed);
        }
      });
  }
  
  // Sub-tab switching inside career tab
  document.querySelectorAll(".career-subtab").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".career-subtab").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".career-table").forEach(t => t.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(btn.dataset.tab).classList.add("active");
  
      renderCareerSection(btn.dataset.tab, csvData[btn.dataset.tab], document.getElementById("careerSearch").value);
    });
  });
  
  // Player name search input
  document.getElementById("careerSearch").addEventListener("input", () => {
    const tab = document.querySelector(".career-subtab.active").dataset.tab;
    renderCareerSection(tab, csvData[tab], document.getElementById("careerSearch").value);
  });
  