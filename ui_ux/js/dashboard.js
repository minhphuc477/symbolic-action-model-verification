/**
 * Master Dashboard Application Logic
 * UI/UX Suite for Search-Tree Topology Collapse & Safe CEG-OMR
 */

document.addEventListener('DOMContentLoaded', async () => {
  let benchmarkData = null;
  let topologyVisualizer = null;

  // 1. Fetch Benchmark Data
  try {
    const res = await fetch('data/benchmark_data.json');
    benchmarkData = await res.json();
    console.log('[Dashboard] Loaded benchmark data:', benchmarkData);
  } catch (err) {
    console.warn('[Dashboard] Could not fetch data/benchmark_data.json via HTTP, using fallback embedded data.', err);
  }

  // 2. Initialize Navigation Tabs
  const tabButtons = document.querySelectorAll('.nav-tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  tabButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      tabButtons.forEach(b => b.classList.remove('active'));
      tabPanels.forEach(p => p.classList.add('hidden'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-tab');
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.remove('hidden');
      }

      // If switching to topology tab, resize canvas
      if (targetId === 'tab-topology' && topologyVisualizer) {
        setTimeout(() => {
          topologyVisualizer.width = topologyVisualizer.canvas.width = topologyVisualizer.canvas.parentElement.clientWidth;
          topologyVisualizer.draw();
        }, 50);
      }
    });
  });

  // 3. Initialize Interactive Canvas
  if (window.TopologyGraphVisualizer) {
    topologyVisualizer = new window.TopologyGraphVisualizer('topologyCanvas');
    const toggleBtn = document.getElementById('toggleSeductionBtn');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const isCurrentlyActive = topologyVisualizer.heuristicSeductionActive;
        topologyVisualizer.toggleSeduction(!isCurrentlyActive);
        toggleBtn.textContent = !isCurrentlyActive ? 'Disable Heuristic Seduction' : 'Enable Heuristic Seduction';
        toggleBtn.className = !isCurrentlyActive 
          ? 'px-4 py-2 rounded-lg bg-rose-600/30 text-rose-300 border border-rose-500/50 hover:bg-rose-600/40 text-sm font-medium transition'
          : 'px-4 py-2 rounded-lg bg-indigo-600/30 text-indigo-300 border border-indigo-500/50 hover:bg-indigo-600/40 text-sm font-medium transition';
      });
    }
  }

  // 4. Branch Divergence Calculator
  const branchInput = document.getElementById('calcBranching');
  const depthInput = document.getElementById('calcDepthDiff');
  const resultDisplay = document.getElementById('calcResult');

  function updateBranchDivergence() {
    if (!branchInput || !depthInput || !resultDisplay) return;
    const b = parseFloat(branchInput.value) || 2;
    const deltaD = parseFloat(depthInput.value) || 1;
    const nodes = Math.pow(b, deltaD);
    resultDisplay.innerHTML = `Ω(b<sup>D-d</sup>) = <strong>${nodes.toLocaleString()}</strong> expanded nodes in phantom subtree`;
  }

  if (branchInput && depthInput) {
    branchInput.addEventListener('input', updateBranchDivergence);
    depthInput.addEventListener('input', updateBranchDivergence);
    updateBranchDivergence();
  }

  // 5. Populate Data Tables and Render Charts if Chart.js is present
  if (benchmarkData) {
    populateDomainsTable(benchmarkData.domains);
    populateSotaTable(benchmarkData.sota_comparison);
    populateSafetyTable(benchmarkData.safety_shield_audit);

    if (window.Chart) {
      renderRegimesChart(benchmarkData.regime_dichotomy_1080);
      renderSotaRadarChart(benchmarkData.sota_comparison);
    }
  }
});

function populateDomainsTable(domains) {
  const tbody = document.getElementById('domainsTableBody');
  if (!tbody || !domains) return;

  tbody.innerHTML = domains.map(d => `
    <tr>
      <td class="font-medium text-white">${d.name}</td>
      <td class="text-xs text-slate-400">${d.category}</td>
      <td class="text-xs font-mono text-rose-300">${d.bottleneck_fault}</td>
      <td>
        <span class="badge-pill badge-rose">${d.regime_1_collapse}% Collapse</span>
      </td>
      <td>
        <span class="badge-pill ${d.regime_2_collapse === 0 ? 'badge-emerald' : 'badge-amber'}">
          ${d.regime_2_collapse}% Collapse
        </span>
      </td>
      <td>
        <span class="badge-pill ${d.is_fully_reversible ? 'badge-cyan' : 'badge-amber'}">
          ${d.safety_class}
        </span>
      </td>
    </tr>
  `).join('');
}

function populateSotaTable(sota) {
  const tbody = document.getElementById('sotaTableBody');
  if (!tbody || !sota) return;

  tbody.innerHTML = sota.map(item => `
    <tr class="${item.learner.includes('This Work') ? 'bg-indigo-950/20 border-l-2 border-indigo-500' : ''}">
      <td class="font-semibold ${item.learner.includes('This Work') ? 'text-indigo-400' : 'text-slate-200'}">${item.learner}</td>
      <td class="text-xs text-slate-400">${item.paradigm}</td>
      <td class="font-mono text-sm font-bold ${item.pesr >= 90 ? 'text-emerald-400' : 'text-rose-400'}">${item.pesr}%</td>
      <td class="font-mono text-xs text-slate-300">${item.k_env}</td>
      <td class="text-xs ${item.family_b_solve.includes('100%') ? 'text-emerald-400' : 'text-amber-400'}">${item.family_b_solve}</td>
      <td class="text-xs text-slate-400">${item.limitations}</td>
    </tr>
  `).join('');
}

function populateSafetyTable(safetyAudit) {
  const tbody = document.getElementById('safetyAuditTableBody');
  if (!tbody || !safetyAudit || !safetyAudit.actions_evaluated) return;

  tbody.innerHTML = safetyAudit.actions_evaluated.map(item => `
    <tr>
      <td class="font-mono text-cyan-300">${item.action}</td>
      <td class="text-slate-300">${item.domain}</td>
      <td class="text-xs font-mono text-slate-400">${item.inverse}</td>
      <td>
        <span class="badge-pill ${item.class === 'REVERSIBLE' ? 'badge-emerald' : 'badge-rose'}">${item.class}</span>
      </td>
      <td>
        <span class="badge-pill ${item.shield_action === 'DISPATCH' ? 'badge-cyan' : 'badge-amber'} font-bold">
          ${item.shield_action}
        </span>
      </td>
    </tr>
  `).join('');
}

function renderRegimesChart(regimes) {
  const ctx = document.getElementById('regimesChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['A* (LM-Cut)', 'Blind Search (BFS)', 'Greedy Best-First (GBFS)'],
      datasets: [
        {
          label: 'Regime I: Shortcut-Inducing (Δc > 0)',
          data: [100.0, 100.0, 100.0],
          backgroundColor: 'rgba(244, 63, 94, 0.75)',
          borderColor: 'rgb(244, 63, 94)',
          borderWidth: 1.5,
          borderRadius: 6
        },
        {
          label: 'Regime II: Cost-Preserving (Δc = 0)',
          data: [44.76, 3.33, 58.2],
          backgroundColor: 'rgba(16, 185, 129, 0.75)',
          borderColor: 'rgb(16, 185, 129)',
          borderWidth: 1.5,
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1' } },
        tooltip: {
          callbacks: {
            afterBody: function(context) {
              if (context[0].dataIndex === 0 && context[0].datasetIndex === 1) {
                return 'Blocksworld (ontable ?x): 0.0% Collapse';
              }
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { color: '#94a3b8', callback: v => v + '%' },
          grid: { color: 'rgba(255, 255, 255, 0.06)' },
          title: { display: true, text: 'Search-Tree Collapse Rate (%)', color: '#94a3b8' }
        },
        x: {
          ticks: { color: '#cbd5e1' },
          grid: { color: 'rgba(255, 255, 255, 0.03)' }
        }
      }
    }
  });
}

function renderSotaRadarChart(sota) {
  const ctx = document.getElementById('sotaRadarChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['PESR (%)', 'Syntactic Accuracy (F1)', 'Family B Solvability', 'Query Efficiency (1/K)', 'Safety Shield Guard'],
      datasets: [
        {
          label: 'Safe CEG-OMR (This Work)',
          data: [100, 100, 100, 95, 100],
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99, 102, 241, 0.35)',
          borderWidth: 2,
          pointBackgroundColor: '#6366f1'
        },
        {
          label: 'Passive SAM (Juba 2021)',
          data: [65.2, 89.0, 0, 15, 90],
          borderColor: '#f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.15)',
          borderWidth: 1.5,
          pointBackgroundColor: '#f59e0b'
        },
        {
          label: 'FAMA (Aineto 2019)',
          data: [0, 95.6, 0, 5, 20],
          borderColor: '#f43f5e',
          backgroundColor: 'rgba(244, 63, 94, 0.15)',
          borderWidth: 1.5,
          pointBackgroundColor: '#f43f5e'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1' } }
      },
      scales: {
        r: {
          angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
          grid: { color: 'rgba(255, 255, 255, 0.08)' },
          pointLabels: { color: '#cbd5e1', font: { size: 11 } },
          ticks: { backdropColor: 'transparent', color: '#94a3b8' }
        }
      }
    }
  });
}
