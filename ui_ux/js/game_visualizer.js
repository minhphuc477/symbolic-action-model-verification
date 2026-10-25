/**
 * Interactive 2D Game World & Agent Mind-vs-Reality Visualizer
 * Core Game AI Engine for Thesis:
 * "Self-Adaptive Symbolic World Models for Intelligent Agents in Game Environments"
 */

class GameAIVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width = 640;
    this.height = this.canvas.height = 400;

    // Game Mode: 'dungeon_escape', 'pitch_black', 'sokoban'
    this.currentLevel = 'dungeon_escape';
    // Model Mode: 'flawed' (attempts shortcut exploit) vs 'repaired' (CEG-OMR valid play)
    this.modelMode = 'flawed';

    // Playback state
    this.currentStep = 0;
    this.isPlaying = false;
    this.playTimer = null;
    this.lastActionStatus = 'READY'; // 'READY', 'RUNNING', 'FAILED_GLITCH', 'GOAL_WON'

    this.initLevels();
    this.initControls();
    this.render();
  }

  initLevels() {
    this.levels = {
      dungeon_escape: {
        name: 'Dungeon Escape (Keys & Gates)',
        gridW: 5,
        gridH: 3,
        tileSize: 80,
        offsetX: 120,
        offsetY: 80,
        rooms: {
          entrance: { x: 0, y: 1, label: 'Entrance', type: 'floor' },
          hallway:  { x: 1, y: 1, label: 'Hallway',  type: 'floor' },
          treasury: { x: 1, y: 0, label: 'Treasury', type: 'item_room' },
          gate:     { x: 2, y: 1, label: 'Gate',     type: 'door_locked' },
          exit:     { x: 3, y: 1, label: 'Exit',     type: 'exit_goal' },
        },
        initialState: {
          heroLoc: 'entrance',
          keyLoc: 'treasury',
          hasKey: false,
          gateLocked: true,
        },
        // Flawed Model Plan (Thinks it can unlock gate without key - phantom sequence break)
        flawedPlan: [
          { action: 'move(entrance -> hallway)', heroLoc: 'hallway', keyLoc: 'treasury', hasKey: false, gateLocked: true, success: true, log: 'Hero moves into Hallway.' },
          { action: 'unlock-door(gate) [NO KEY!]', heroLoc: 'hallway', keyLoc: 'treasury', hasKey: false, gateLocked: true, success: false, log: '🚨 GAME OVER: Action Failed! Door is locked. (has-key bronze_key) missing!' },
        ],
        // Repaired Model Plan (CEG-OMR learned precondition -> gathers key first)
        repairedPlan: [
          { action: 'move(entrance -> hallway)', heroLoc: 'hallway', keyLoc: 'treasury', hasKey: false, gateLocked: true, success: true, log: 'Hero moves into Hallway.' },
          { action: 'move(hallway -> treasury)', heroLoc: 'treasury', keyLoc: 'treasury', hasKey: false, gateLocked: true, success: true, log: 'Hero enters Treasury.' },
          { action: 'pickup-key(bronze_key)', heroLoc: 'treasury', keyLoc: 'inventory', hasKey: true, gateLocked: true, success: true, log: '🔑 Hero picks up Bronze Key!' },
          { action: 'move(treasury -> hallway)', heroLoc: 'hallway', keyLoc: 'inventory', hasKey: true, gateLocked: true, success: true, log: 'Hero returns to Hallway.' },
          { action: 'unlock-door(gate)', heroLoc: 'hallway', keyLoc: 'inventory', hasKey: true, gateLocked: false, success: true, log: '🔓 Gate unlocked successfully!' },
          { action: 'move(hallway -> gate)', heroLoc: 'gate', keyLoc: 'inventory', hasKey: true, gateLocked: false, success: true, log: 'Hero passes through open gate.' },
          { action: 'move(gate -> exit)', heroLoc: 'exit', keyLoc: 'inventory', hasKey: true, gateLocked: false, success: true, log: '🏆 VICTORY: Hero escapes the dungeon!' },
        ]
      },

      pitch_black: {
        name: 'Pitch Black (Visibility & Pitfalls)',
        gridW: 3,
        gridH: 2,
        tileSize: 100,
        offsetX: 170,
        offsetY: 100,
        rooms: {
          r00: { x: 0, y: 0, label: 'Start (Lit)', type: 'floor' },
          r01: { x: 1, y: 0, label: 'Pitfall (Dark)', type: 'hazard_dark' },
          r02: { x: 2, y: 0, label: 'Exit (Lit)', type: 'exit_goal' },
          r10: { x: 0, y: 1, label: 'Hall (Lit)', type: 'floor' },
          r11: { x: 1, y: 1, label: 'Switch (Lit)', type: 'floor' },
          r12: { x: 2, y: 1, label: 'Hall (Lit)', type: 'floor' },
        },
        initialState: { heroLoc: 'r00', isLit01: false },
        flawedPlan: [
          { action: 'move(r00 -> r01) [DARK PIT!]', heroLoc: 'r01', success: false, log: '💀 TRAP DEATH: Hero walked into dark hazard without light!' }
        ],
        repairedPlan: [
          { action: 'move(r00 -> r10)', heroLoc: 'r10', success: true, log: 'Hero takes safe lower detour.' },
          { action: 'move(r10 -> r11)', heroLoc: 'r11', success: true, log: 'Hero moves along lit path.' },
          { action: 'move(r11 -> r12)', heroLoc: 'r12', success: true, log: 'Hero reaches east hallway.' },
          { action: 'move(r12 -> r02)', heroLoc: 'r02', success: true, log: '🏆 VICTORY: Hero safely reaches Goal without stepping into dark pit!' }
        ]
      },

      sokoban: {
        name: 'Sokoban (Deadlock Puzzle)',
        gridW: 4,
        gridH: 3,
        tileSize: 80,
        offsetX: 160,
        offsetY: 80,
        rooms: {
          p0: { x: 1, y: 1, label: 'Hero', type: 'floor' },
          c0: { x: 2, y: 1, label: 'Box', type: 'box' },
          t0: { x: 3, y: 1, label: 'Target', type: 'target' },
          w0: { x: 2, y: 0, label: 'Wall', type: 'wall' },
          w1: { x: 3, y: 0, label: 'Corner Deadlock', type: 'deadlock' },
        },
        initialState: { heroLoc: {x: 1, y: 1}, boxLoc: {x: 2, y: 1} },
        flawedPlan: [
          { action: 'push(box -> corner) [IRREVERSIBLE!]', success: false, log: '🚫 IRREVERSIBLE DEADLOCK: Box pushed into corner; cannot be retrieved!' }
        ],
        repairedPlan: [
          { action: 'push(box -> target)', success: true, log: '🏆 VICTORY: Box pushed safely onto Target goal!' }
        ]
      }
    };
  }

  initControls() {
    // Level selection
    const levelSelect = document.getElementById('gameLevelSelect');
    if (levelSelect) {
      levelSelect.addEventListener('change', (e) => {
        this.currentLevel = e.target.value;
        this.resetGame();
      });
    }

    // Model mode toggle
    const modelSelect = document.getElementById('gameModelSelect');
    if (modelSelect) {
      modelSelect.addEventListener('change', (e) => {
        this.modelMode = e.target.value;
        this.resetGame();
      });
    }

    // Playback buttons
    const playBtn = document.getElementById('gamePlayBtn');
    const stepBtn = document.getElementById('gameStepBtn');
    const resetBtn = document.getElementById('gameResetBtn');

    if (playBtn) {
      playBtn.addEventListener('click', () => {
        if (this.isPlaying) {
          this.pause();
          playBtn.textContent = '▶ Auto Play';
        } else {
          this.play();
          playBtn.textContent = '⏸ Pause';
        }
      });
    }

    if (stepBtn) {
      stepBtn.addEventListener('click', () => {
        this.pause();
        if (playBtn) playBtn.textContent = '▶ Auto Play';
        this.stepForward();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.pause();
        if (playBtn) playBtn.textContent = '▶ Auto Play';
        this.resetGame();
      });
    }
  }

  resetGame() {
    this.currentStep = 0;
    this.lastActionStatus = 'READY';
    this.updateLog('Game reset to initial state.');
    this.render();
  }

  play() {
    this.isPlaying = true;
    this.playTimer = setInterval(() => {
      const activePlan = this.getActivePlan();
      if (this.currentStep < activePlan.length) {
        this.stepForward();
      } else {
        this.pause();
        const playBtn = document.getElementById('gamePlayBtn');
        if (playBtn) playBtn.textContent = '▶ Auto Play';
      }
    }, 1200);
  }

  pause() {
    this.isPlaying = false;
    if (this.playTimer) {
      clearInterval(this.playTimer);
      this.playTimer = null;
    }
  }

  getActivePlan() {
    const lvl = this.levels[this.currentLevel];
    return this.modelMode === 'flawed' ? lvl.flawedPlan : lvl.repairedPlan;
  }

  stepForward() {
    const activePlan = this.getActivePlan();
    if (this.currentStep < activePlan.length) {
      const stepData = activePlan[this.currentStep];
      this.currentStep++;
      this.updateLog(`[Step ${this.currentStep}/${activePlan.length}] ${stepData.action} -> ${stepData.log}`);
      this.render();
    }
  }

  updateLog(msg) {
    const logBox = document.getElementById('gameConsoleLog');
    if (logBox) {
      const line = document.createElement('div');
      line.className = 'py-0.5 border-b border-slate-800/50';
      if (msg.includes('🚨') || msg.includes('💀') || msg.includes('🚫')) {
        line.className += ' text-rose-400 font-semibold';
      } else if (msg.includes('🏆') || msg.includes('🔑') || msg.includes('🔓')) {
        line.className += ' text-emerald-400 font-semibold';
      } else {
        line.className += ' text-slate-300';
      }
      line.textContent = msg;
      logBox.appendChild(line);
      logBox.scrollTop = logBox.scrollHeight;
    }
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Draw Dark Fantasy / Sci-fi Game Grid Background
    this.ctx.fillStyle = '#0b0f19';
    this.ctx.fillRect(0, 0, this.width, this.height);

    if (this.currentLevel === 'dungeon_escape') {
      this.renderDungeonEscape();
    } else if (this.currentLevel === 'pitch_black') {
      this.renderPitchBlack();
    } else if (this.currentLevel === 'sokoban') {
      this.renderSokoban();
    }
  }

  renderDungeonEscape() {
    const lvl = this.levels.dungeon_escape;
    const plan = this.getActivePlan();
    const currentState = this.currentStep === 0 
      ? lvl.initialState 
      : plan[Math.min(this.currentStep - 1, plan.length - 1)];

    const { tileSize, offsetX, offsetY } = lvl;

    // Draw Connecting Hallways
    this.ctx.strokeStyle = 'rgba(75, 85, 99, 0.4)';
    this.ctx.lineWidth = 6;
    this.drawHallway(0, 1, 1, 1, tileSize, offsetX, offsetY); // Entrance <-> Hallway
    this.drawHallway(1, 1, 1, 0, tileSize, offsetX, offsetY); // Hallway <-> Treasury
    this.drawHallway(1, 1, 2, 1, tileSize, offsetX, offsetY); // Hallway <-> Gate
    this.drawHallway(2, 1, 3, 1, tileSize, offsetX, offsetY); // Gate <-> Exit

    // Draw Rooms
    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      // Room Floor Box
      this.ctx.fillStyle = '#1e293b';
      this.ctx.strokeStyle = '#475569';
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.roundRect(rx, ry, tileSize - 8, tileSize - 8, 8);
      this.ctx.fill();
      this.ctx.stroke();

      // Room Specific Icons / Features
      if (roomId === 'treasury') {
        this.ctx.fillStyle = '#f59e0b';
        this.ctx.font = '24px sans-serif';
        this.ctx.textAlign = 'center';
        // If key not picked up yet
        if (!currentState.hasKey) {
          this.ctx.fillText('🗝️', rx + (tileSize - 8) / 2, ry + 42);
        } else {
          this.ctx.fillText('📦', rx + (tileSize - 8) / 2, ry + 42);
        }
      } else if (roomId === 'gate') {
        this.ctx.font = '24px sans-serif';
        this.ctx.textAlign = 'center';
        if (currentState.gateLocked) {
          this.ctx.fillText('🔒', rx + (tileSize - 8) / 2, ry + 42);
        } else {
          this.ctx.fillText('🚪', rx + (tileSize - 8) / 2, ry + 42);
        }
      } else if (roomId === 'exit') {
        this.ctx.font = '24px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('🏆', rx + (tileSize - 8) / 2, ry + 42);
      }

      // Room Title
      this.ctx.fillStyle = '#94a3b8';
      this.ctx.font = '10px Inter, sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(r.label, rx + (tileSize - 8) / 2, ry + tileSize - 14);
    }

    // Draw Hero Sprite
    const heroRoom = lvl.rooms[currentState.heroLoc];
    if (heroRoom) {
      const hx = offsetX + heroRoom.x * tileSize + (tileSize - 8) / 2;
      const hy = offsetY + heroRoom.y * tileSize + (tileSize - 8) / 2;

      this.ctx.beginPath();
      this.ctx.arc(hx, hy, 18, 0, Math.PI * 2);
      this.ctx.fillStyle = '#3b82f6';
      this.ctx.shadowColor = '#60a5fa';
      this.ctx.shadowBlur = 10;
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
      this.ctx.strokeStyle = '#fff';
      this.ctx.lineWidth = 2;
      this.ctx.stroke();

      this.ctx.font = '16px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('🧙', hx, hy + 5);
    }

    // Header Mode Overlay on Canvas
    this.renderHeaderOverlay();
  }

  renderPitchBlack() {
    const lvl = this.levels.pitch_black;
    const plan = this.getActivePlan();
    const currentState = this.currentStep === 0 
      ? lvl.initialState 
      : plan[Math.min(this.currentStep - 1, plan.length - 1)];

    const { tileSize, offsetX, offsetY } = lvl;

    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      // Dark pitfall room styling
      if (r.type === 'hazard_dark') {
        this.ctx.fillStyle = '#020617';
        this.ctx.strokeStyle = '#dc2626';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.roundRect(rx, ry, tileSize - 8, tileSize - 8, 8);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.font = '28px sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('💀', rx + (tileSize - 8) / 2, ry + 50);

        this.ctx.fillStyle = '#f87171';
        this.ctx.font = '10px Inter, sans-serif';
        this.ctx.fillText('PIT HAZARD', rx + (tileSize - 8) / 2, ry + tileSize - 14);
      } else {
        this.ctx.fillStyle = '#1e293b';
        this.ctx.strokeStyle = '#475569';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.roundRect(rx, ry, tileSize - 8, tileSize - 8, 8);
        this.ctx.fill();
        this.ctx.stroke();

        if (r.type === 'exit_goal') {
          this.ctx.font = '28px sans-serif';
          this.ctx.textAlign = 'center';
          this.ctx.fillText('🏆', rx + (tileSize - 8) / 2, ry + 50);
        } else {
          this.ctx.font = '24px sans-serif';
          this.ctx.textAlign = 'center';
          this.ctx.fillText('💡', rx + (tileSize - 8) / 2, ry + 46);
        }

        this.ctx.fillStyle = '#cbd5e1';
        this.ctx.font = '10px Inter, sans-serif';
        this.ctx.textAlign = 'center';
        this.ctx.fillText(r.label, rx + (tileSize - 8) / 2, ry + tileSize - 14);
      }
    }

    // Hero in Pitch Black
    const heroRoom = lvl.rooms[currentState.heroLoc];
    if (heroRoom) {
      const hx = offsetX + heroRoom.x * tileSize + (tileSize - 8) / 2;
      const hy = offsetY + heroRoom.y * tileSize + (tileSize - 8) / 2;

      this.ctx.beginPath();
      this.ctx.arc(hx, hy, 20, 0, Math.PI * 2);
      this.ctx.fillStyle = heroRoom.type === 'hazard_dark' ? '#ef4444' : '#3b82f6';
      this.ctx.fill();
      this.ctx.font = '18px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(heroRoom.type === 'hazard_dark' ? '💥' : '🧙', hx, hy + 6);
    }

    this.renderHeaderOverlay();
  }

  renderSokoban() {
    this.ctx.fillStyle = '#1e293b';
    this.ctx.font = '14px Inter, sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('📦 Sokoban Reversibility Shield: Corner Deadlock Prevention Active', this.width / 2, this.height / 2 - 20);
    this.ctx.fillStyle = '#10b981';
    this.ctx.fillText('Safety Shield intercepts non-reversible corner pushes with K_env = 0', this.width / 2, this.height / 2 + 15);
    this.renderHeaderOverlay();
  }

  drawHallway(x1, y1, x2, y2, size, ox, oy) {
    const cx1 = ox + x1 * size + (size - 8) / 2;
    const cy1 = oy + y1 * size + (size - 8) / 2;
    const cx2 = ox + x2 * size + (size - 8) / 2;
    const cy2 = oy + y2 * size + (size - 8) / 2;

    this.ctx.beginPath();
    this.ctx.moveTo(cx1, cy1);
    this.ctx.lineTo(cx2, cy2);
    this.ctx.stroke();
  }

  renderHeaderOverlay() {
    const isFlawed = this.modelMode === 'flawed';
    this.ctx.fillStyle = isFlawed ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)';
    this.ctx.strokeStyle = isFlawed ? '#ef4444' : '#10b981';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.roundRect(14, 14, 310, 36, 6);
    this.ctx.fill();
    this.ctx.stroke();

    this.ctx.fillStyle = isFlawed ? '#fca5a5' : '#6ee7b7';
    this.ctx.font = 'bold 12px Inter, sans-serif';
    this.ctx.textAlign = 'left';
    const title = isFlawed 
      ? '⚠️ FLAWED MODEL: Sequence-Break Exploit' 
      : '🛡️ CEG-OMR: Self-Adaptive Verified Play';
    this.ctx.fillText(title, 26, 36);
  }
}

window.GameAIVisualizer = GameAIVisualizer;
