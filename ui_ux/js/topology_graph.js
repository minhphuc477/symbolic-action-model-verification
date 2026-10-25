/**
 * Interactive Canvas State-Transition Graph & Topology Collapse Visualizer
 * Search-Tree Topology Analyst Module
 */

class TopologyGraphVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width = this.canvas.parentElement.clientWidth;
    this.height = this.canvas.height = 480;

    // Simulation State
    this.heuristicSeductionActive = true;
    this.hoveredNode = null;
    this.particles = [];
    this.animationFrame = null;

    // Define Graph Structure TS = (S, E)
    this.nodes = [
      { id: 's0', label: 's₀ (Initial State)', x: 90, y: 240, r: 24, type: 'init', g: 0, h_star: 4, h_hat: 2, isDeadEnd: false },
      { id: 's1_real', label: 's₁ (Valid Step)', x: 260, y: 150, r: 20, type: 'real', g: 1, h_star: 3, h_hat: 3, isDeadEnd: false },
      { id: 's2_real', label: 's₂ (Subgoal Set)', x: 440, y: 150, r: 20, type: 'real', g: 2, h_star: 2, h_hat: 2, isDeadEnd: false },
      { id: 'sG', label: 'S_G (Goal State)', x: 620, y: 240, r: 26, type: 'goal', g: 4, h_star: 0, h_hat: 0, isDeadEnd: false },
      // Spurious shortcut branch
      { id: 's_phantom', label: 's_phantom (Shortcut Bypass)', x: 280, y: 350, r: 22, type: 'phantom', g: 1, h_star: 99, h_hat: 1, isDeadEnd: false },
      { id: 's_trap1', label: 's_trap (Unrecognized Dead-End)', x: 460, y: 350, r: 22, type: 'trap', g: 2, h_star: 99, h_hat: 0.5, isDeadEnd: true },
      { id: 's_trap2', label: 's_trap₂ (Search Explosion)', x: 580, y: 410, r: 18, type: 'trap', g: 3, h_star: 99, h_hat: 0.2, isDeadEnd: true },
    ];

    this.edges = [
      // Physical valid trajectory
      { from: 's0', to: 's1_real', action: 'setup-key (Valid)', cost: 1, valid: true },
      { from: 's1_real', to: 's2_real', action: 'carry-resource (Valid)', cost: 1, valid: true },
      { from: 's2_real', to: 'sG', action: 'unlock-goal (Valid)', cost: 2, valid: true },
      // Spurious shortcut trajectory
      { from: 's0', to: 's_phantom', action: 'unlock-door [MISSING (has-key)]', cost: 1, valid: false },
      { from: 's_phantom', to: 's_trap1', action: 'phantom-advance', cost: 1, valid: false },
      { from: 's_trap1', to: 's_trap2', action: 'branch-divergence Ω(b^(D-d))', cost: 1, valid: false },
    ];

    this.initEvents();
    this.initParticles();
    this.animate();
  }

  initEvents() {
    window.addEventListener('resize', () => {
      if (!this.canvas.parentElement) return;
      this.width = this.canvas.width = this.canvas.parentElement.clientWidth;
      this.draw();
    });

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let found = null;
      for (const n of this.nodes) {
        const dx = mx - n.x;
        const dy = my - n.y;
        if (Math.sqrt(dx * dx + dy * dy) <= n.r) {
          found = n;
          break;
        }
      }
      this.hoveredNode = found;
      this.canvas.style.cursor = found ? 'pointer' : 'crosshair';
      this.draw();
    });
  }

  initParticles() {
    this.particles = [];
    for (let i = 0; i < 20; i++) {
      this.particles.push({
        edgeIndex: Math.floor(Math.random() * this.edges.length),
        progress: Math.random(),
        speed: 0.006 + Math.random() * 0.008,
      });
    }
  }

  toggleSeduction(active) {
    this.heuristicSeductionActive = active;
    this.draw();
  }

  draw() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Draw Grid Background
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    this.ctx.lineWidth = 1;
    for (let x = 0; x < this.width; x += 40) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.height);
      this.ctx.stroke();
    }
    for (let y = 0; y < this.height; y += 40) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
      this.ctx.stroke();
    }

    // Draw Edges
    this.edges.forEach((edge) => {
      const u = this.nodes.find(n => n.id === edge.from);
      const v = this.nodes.find(n => n.id === edge.to);
      if (!u || !v) return;

      this.ctx.beginPath();
      this.ctx.moveTo(u.x, u.y);
      this.ctx.lineTo(v.x, v.y);

      if (edge.valid) {
        this.ctx.strokeStyle = 'rgba(16, 185, 129, 0.65)';
        this.ctx.lineWidth = 2.5;
        this.ctx.setLineDash([]);
      } else {
        this.ctx.strokeStyle = this.heuristicSeductionActive ? 'rgba(244, 63, 94, 0.85)' : 'rgba(244, 63, 94, 0.25)';
        this.ctx.lineWidth = 2.5;
        this.ctx.setLineDash([6, 4]);
      }
      this.ctx.stroke();
      this.ctx.setLineDash([]);

      // Draw Action Label
      const midX = (u.x + v.x) / 2;
      const midY = (u.y + v.y) / 2 - 8;
      this.ctx.fillStyle = edge.valid ? '#34d399' : '#fb7185';
      this.ctx.font = '10px Fira Code, monospace';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(edge.action, midX, midY);
    });

    // Draw Animated Particles
    this.particles.forEach((p) => {
      const edge = this.edges[p.edgeIndex];
      // When seduction active, bias particles heavily toward shortcut branch
      if (this.heuristicSeductionActive && edge.valid && Math.random() < 0.02) {
        p.edgeIndex = 3 + Math.floor(Math.random() * 3);
      }
      const u = this.nodes.find(n => n.id === edge.from);
      const v = this.nodes.find(n => n.id === edge.to);
      if (!u || !v) return;

      const px = u.x + (v.x - u.x) * p.progress;
      const py = u.y + (v.y - u.y) * p.progress;

      this.ctx.beginPath();
      this.ctx.arc(px, py, edge.valid ? 3.5 : 4.5, 0, Math.PI * 2);
      this.ctx.fillStyle = edge.valid ? '#10b981' : '#f43f5e';
      this.ctx.shadowColor = edge.valid ? '#10b981' : '#f43f5e';
      this.ctx.shadowBlur = 8;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
    });

    // Draw Nodes
    this.nodes.forEach((n) => {
      this.ctx.beginPath();
      this.ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);

      let fillColor = '#1e293b';
      let strokeColor = '#64748b';

      if (n.type === 'init') {
        fillColor = '#1e3a8a';
        strokeColor = '#3b82f6';
      } else if (n.type === 'goal') {
        fillColor = '#064e3b';
        strokeColor = '#10b981';
      } else if (n.type === 'real') {
        fillColor = '#134e4a';
        strokeColor = '#14b8a6';
      } else if (n.type === 'phantom') {
        fillColor = '#881337';
        strokeColor = '#f43f5e';
      } else if (n.type === 'trap') {
        fillColor = '#4c0519';
        strokeColor = '#fb7185';
      }

      this.ctx.fillStyle = fillColor;
      this.ctx.fill();
      this.ctx.lineWidth = 2.5;
      this.ctx.strokeStyle = strokeColor;
      this.ctx.stroke();

      // Node Label
      this.ctx.fillStyle = '#f8fafc';
      this.ctx.font = '11px Inter, sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(n.id, n.x, n.y + 4);

      // f-value annotation: f(s) = g(s) + h(s)
      const h_used = this.heuristicSeductionActive ? n.h_hat : n.h_star;
      const f_val = n.g + (h_used >= 99 ? '∞' : h_used);
      this.ctx.fillStyle = n.type === 'trap' || n.type === 'phantom' ? '#fda4af' : '#6ee7b7';
      this.ctx.font = 'bold 10px Fira Code, monospace';
      this.ctx.fillText(`f=${f_val}`, n.x, n.y + n.r + 14);
    });

    // Hover Tooltip
    if (this.hoveredNode) {
      const n = this.hoveredNode;
      const ttW = 220;
      const ttH = 95;
      const ttX = Math.min(n.x + 15, this.width - ttW - 10);
      const ttY = Math.max(n.y - ttH - 10, 10);

      this.ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
      this.ctx.strokeStyle = '#6366f1';
      this.ctx.lineWidth = 1.5;
      this.ctx.beginPath();
      this.ctx.roundRect(ttX, ttY, ttW, ttH, 6);
      this.ctx.fill();
      this.ctx.stroke();

      this.ctx.fillStyle = '#fff';
      this.ctx.font = 'bold 12px Inter, sans-serif';
      this.ctx.textAlign = 'left';
      this.ctx.fillText(n.label, ttX + 10, ttY + 20);

      this.ctx.font = '11px Fira Code, monospace';
      this.ctx.fillStyle = '#94a3b8';
      this.ctx.fillText(`g(s) = ${n.g} (accumulated cost)`, ttX + 10, ttY + 40);
      this.ctx.fillText(`h*(s) = ${n.h_star >= 99 ? '∞ (dead-end)' : n.h_star} (true dist)`, ttX + 10, ttY + 58);
      this.ctx.fillStyle = this.heuristicSeductionActive && n.h_hat < n.h_star ? '#f43f5e' : '#10b981';
      this.ctx.fillText(`ĥ(s) = ${n.h_hat} (seduced heuristic)`, ttX + 10, ttY + 76);
    }
  }

  animate() {
    this.particles.forEach((p) => {
      p.progress += p.speed;
      if (p.progress >= 1.0) {
        p.progress = 0;
        p.edgeIndex = Math.floor(Math.random() * this.edges.length);
      }
    });

    this.draw();
    this.animationFrame = requestAnimationFrame(() => this.animate());
  }
}

window.TopologyGraphVisualizer = TopologyGraphVisualizer;
