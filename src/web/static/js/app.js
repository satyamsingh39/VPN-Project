/**
 * VPN Traffic Classifier — Client-side logic
 * Tab switching · Chart.js rendering · Drag-and-drop file upload
 */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initFileUpload();
  initCharts();
});

/* ================================================================
   TAB SWITCHING
   ================================================================ */
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanels = document.querySelectorAll(".tab-panel");

  if (!tabBtns.length) return;

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.tab;

      // Toggle buttons
      tabBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      // Toggle panels
      tabPanels.forEach((panel) => {
        panel.classList.toggle("active", panel.id === `tab-${target}`);
      });
    });
  });
}

/* ================================================================
   FILE UPLOAD (DRAG & DROP)
   ================================================================ */
function initFileUpload() {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("csvFileInput");
  const fileName = document.getElementById("fileName");
  const submitBtn = document.getElementById("batchSubmitBtn");

  if (!dropZone || !fileInput) return;

  // Show file name when selected
  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      fileName.textContent = `📄 ${fileInput.files[0].name}`;
      submitBtn.disabled = false;
    } else {
      fileName.textContent = "";
      submitBtn.disabled = true;
    }
  });

  // Drag-over styling
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");

    if (e.dataTransfer.files.length > 0) {
      fileInput.files = e.dataTransfer.files;
      fileName.textContent = `📄 ${e.dataTransfer.files[0].name}`;
      submitBtn.disabled = false;
    }
  });
}

/* ================================================================
   CHART.JS RENDERING
   ================================================================ */

/** Shared dark-theme palette for chart segments */
const CHART_COLORS = [
  "#06b6d4", // cyan
  "#3b82f6", // blue
  "#22c55e", // green
  "#f59e0b", // amber
  "#a855f7", // purple
  "#ef4444", // red
  "#ec4899", // pink
  "#14b8a6", // teal
  "#f97316", // orange
  "#6366f1", // indigo
];

/** Shared Chart.js default overrides */
const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: {
      labels: {
        color: "#94a3b8",
        font: { family: "Inter", size: 12 },
        padding: 16,
      },
    },
  },
};

function initCharts() {
  renderTrafficChart();
  renderAppChart();
  renderPlotlyVpnAppChart();
  renderPlotlyNonVpnAppChart();
  renderPlotlyConfidenceDistChart();
  renderPlotlyScatterChart();
}

/* ================================================================
   PLOTLY VISUALIZATIONS
   ================================================================ */

const PLOTLY_LAYOUT_DEFAULTS = {
  paper_bgcolor: 'transparent',
  plot_bgcolor: 'transparent',
  font: { family: 'Inter', color: '#94a3b8', size: 12 },
  margin: { t: 20, r: 20, b: 40, l: 40 },
  autosize: true
};

function renderPlotlyVpnAppChart() {
  const container = document.getElementById("plotlyVpnAppChart");
  if (!container || !window.__vpnAppStats || typeof Plotly === 'undefined') return;

  const stats = window.__vpnAppStats;
  if (!stats.length) {
    container.innerHTML = "<p style='color:#64748b; padding:20px;'>No VPN traffic flows detected in batch sample.</p>";
    return;
  }

  const labels = stats.map(s => s["Application"]);
  const values = stats.map(s => s["Count"]);

  const data = [{
    type: 'pie',
    labels: labels,
    values: values,
    hole: 0.4,
    marker: { colors: CHART_COLORS },
    textinfo: 'label+percent',
    textposition: 'outside',
    automargin: true
  }];

  const layout = {
    ...PLOTLY_LAYOUT_DEFAULTS,
    showlegend: false
  };

  Plotly.newPlot(container, data, layout, { responsive: true, displayModeBar: false });
}

function renderPlotlyNonVpnAppChart() {
  const container = document.getElementById("plotlyNonVpnAppChart");
  if (!container || !window.__nonVpnAppStats || typeof Plotly === 'undefined') return;

  const stats = window.__nonVpnAppStats;
  if (!stats.length) {
    container.innerHTML = "<p style='color:#64748b; padding:20px;'>No Non-VPN traffic flows detected in batch sample.</p>";
    return;
  }

  const labels = stats.map(s => s["Application"]);
  const values = stats.map(s => s["Count"]);

  const data = [{
    type: 'bar',
    x: labels,
    y: values,
    marker: { color: CHART_COLORS.slice(2, 2 + labels.length) }
  }];

  const layout = {
    ...PLOTLY_LAYOUT_DEFAULTS,
    xaxis: { title: 'Application', tickcolor: '#64748b' },
    yaxis: { title: 'Flow Count', gridcolor: 'rgba(148,163,184,0.08)' }
  };

  Plotly.newPlot(container, data, layout, { responsive: true, displayModeBar: false });
}

function renderPlotlyConfidenceDistChart() {
  const container = document.getElementById("plotlyConfidenceDistChart");
  if (!container || !window.__trafficConfidences || typeof Plotly === 'undefined') return;

  const tConf = window.__trafficConfidences;
  const aConf = window.__appConfidences;

  const trace1 = {
    x: tConf,
    type: 'histogram',
    name: 'VPN Detector Confidence',
    opacity: 0.7,
    marker: { color: '#06b6d4' }
  };

  const trace2 = {
    x: aConf,
    type: 'histogram',
    name: 'App Classifier Confidence',
    opacity: 0.7,
    marker: { color: '#a855f7' }
  };

  const layout = {
    ...PLOTLY_LAYOUT_DEFAULTS,
    barmode: 'overlay',
    xaxis: { title: 'Confidence Score (0.0 - 1.0)', range: [0, 1.05] },
    yaxis: { title: 'Frequency', gridcolor: 'rgba(148,163,184,0.08)' },
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.newPlot(container, [trace1, trace2], layout, { responsive: true, displayModeBar: false });
}

function renderPlotlyScatterChart() {
  const container = document.getElementById("plotlyScatterChart");
  if (!container || !window.__scatterData || typeof Plotly === 'undefined') return;

  const sample = window.__scatterData;
  if (!sample.length) return;

  const vpnPoints = sample.filter(d => d.traffic_type === 'VPN');
  const nonVpnPoints = sample.filter(d => d.traffic_type === 'Non-VPN');

  const traceVpn = {
    x: vpnPoints.map(d => d.duration),
    y: vpnPoints.map(d => d.flowBytesPerSecond),
    text: vpnPoints.map(d => `App: ${d.application}<br>Conf: ${(d.app_confidence * 100).toFixed(1)}%`),
    mode: 'markers',
    type: 'scatter',
    name: 'VPN Flow',
    marker: { color: '#22c55e', size: 7, opacity: 0.8 }
  };

  const traceNonVpn = {
    x: nonVpnPoints.map(d => d.duration),
    y: nonVpnPoints.map(d => d.flowBytesPerSecond),
    text: nonVpnPoints.map(d => `App: ${d.application}<br>Conf: ${(d.app_confidence * 100).toFixed(1)}%`),
    mode: 'markers',
    type: 'scatter',
    name: 'Non-VPN Flow',
    marker: { color: '#f59e0b', size: 7, opacity: 0.8 }
  };

  const layout = {
    ...PLOTLY_LAYOUT_DEFAULTS,
    xaxis: { title: 'Flow Duration (s)', gridcolor: 'rgba(148,163,184,0.08)' },
    yaxis: { title: 'Flow Bytes / Sec', gridcolor: 'rgba(148,163,184,0.08)' },
    legend: { orientation: 'h', y: 1.15 }
  };

  Plotly.newPlot(container, [traceVpn, traceNonVpn], layout, { responsive: true, displayModeBar: false });
}

function renderTrafficChart() {
  const canvas = document.getElementById("trafficChart");
  if (!canvas || !window.__trafficStats) return;

  const stats = window.__trafficStats;
  const labels = stats.map((s) => s["Traffic Type"]);
  const data = stats.map((s) => s["Count"]);

  new Chart(canvas, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [
        {
          data: data,
          backgroundColor: [CHART_COLORS[2], CHART_COLORS[3]], // green + amber
          borderColor: "transparent",
          borderWidth: 0,
          hoverOffset: 8,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      cutout: "60%",
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: {
          ...CHART_DEFAULTS.plugins.legend,
          position: "bottom",
        },
      },
    },
  });
}

function renderAppChart() {
  const canvas = document.getElementById("appChart");
  if (!canvas || !window.__appStats) return;

  const stats = window.__appStats;
  const labels = stats.map((s) => s["Application"]);
  const data = stats.map((s) => s["Count"]);

  new Chart(canvas, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Count",
          data: data,
          backgroundColor: CHART_COLORS.slice(0, labels.length),
          borderRadius: 6,
          borderSkipped: false,
          barPercentage: 0.7,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: "y",
      scales: {
        x: {
          ticks: { color: "#64748b", font: { family: "JetBrains Mono", size: 11 } },
          grid: { color: "rgba(148,163,184,0.06)" },
        },
        y: {
          ticks: { color: "#94a3b8", font: { family: "Inter", size: 12 } },
          grid: { display: false },
        },
      },
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { display: false },
      },
    },
  });
}
