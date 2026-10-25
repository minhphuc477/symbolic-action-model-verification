/**
 * Professional Game AI Visualizer & Mind-vs-Reality Research Engine
 * Thesis: "Developing a Counterexample-Guided Self-Adaptive Symbolic World Model
 *         for Intelligent Agents in Game Environments"
 * 
 * Features:
 * - 100% Procedural Canvas Vector Rendering (Zero raw emojis)
 * - Smooth Animation Interpolation (position lerp via requestAnimationFrame)
 * - Mind-vs-Reality Dual Display:
 *   - Hallucinated Ghost Trajectory (Mental Model shortcut attempt)
 *   - Concrete Physical Barrier Shockwave & Rejection Telemetry
 * - Clean SVG/Vector Sprites for Hero, Ghost, Key, Gate, Portal, and Hazards
 */

class GameAIVisualizer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.width = 640;
    this.height = this.canvas.height = 400;

    // Active configuration
    this.currentLevel = 'dungeon_escape'; // 'dungeon_escape', 'pitch_black', 'sokoban'
    this.modelMode = 'flawed';            // 'flawed' vs 'repaired'

    // Playback state
    this.currentStep = 0;
    this.isPlaying = false;
    this.playTimer = null;

    // Animation interpolation state
    this.agentPos = { x: 0, y: 0 };
    this.targetPos = { x: 0, y: 0 };
    this.ghostPos = { x: 0, y: 0 };
    this.targetGhostPos = { x: 0, y: 0 };
    this.animFrameId = null;
    this.animTime = 0;
    this.rejectionPulse = 0; // Shockwave timer when action is rejected

    this.initLevels();
    this.initControls();
    this.resetPositions();
    this.startAnimationLoop();
  }

  initLevels() {
    this.levels = {
      dungeon_escape: {
        name: 'Dungeon Escape',
        subtitle: 'Sequential Key & Locked Barrier Progression',
        gridW: 4,
        gridH: 2,
        tileSize: 84,
        offsetX: 150,
        offsetY: 100,
        rooms: {
          entrance: { x: 0, y: 1, label: 'Entrance', type: 'floor' },
          hallway:  { x: 1, y: 1, label: 'Hallway',  type: 'floor' },
          treasury: { x: 1, y: 0, label: 'Treasury', type: 'item_room' },
          gate:     { x: 2, y: 1, label: 'Iron Gate', type: 'door_locked' },
          exit:     { x: 3, y: 1, label: 'Portal',    type: 'exit_goal' },
        },
        initialState: {
          heroLoc: 'entrance',
          keyLoc: 'treasury',
          hasKey: false,
          gateLocked: true,
          rejection: false,
        },
        // Flawed Model: Omits (has-key hero bronze_key). Hallucinates 3-step speedrun shortcut!
        flawedPlan: [
          {
            action: 'move(entrance -> hallway)',
            heroLoc: 'hallway',
            ghostLoc: 'hallway',
            keyLoc: 'treasury',
            hasKey: false,
            gateLocked: true,
            success: true,
            log: 'Hero moves into Hallway.',
            status: 'IN_TRANSIT'
          },
          {
            action: 'unlock-door(gate)',
            heroLoc: 'hallway',
            ghostLoc: 'gate',
            keyLoc: 'treasury',
            hasKey: false,
            gateLocked: true,
            success: false,
            shockwave: true,
            log: 'REJECTION: Concrete engine blocked action! Precondition (has-key hero k1) is false.',
            status: 'ACTION_REJECTED'
          }
        ],
        // Repaired Model: Patched via CEG-OMR. Gathers key before approaching gate!
        repairedPlan: [
          { action: 'move(entrance -> hallway)', heroLoc: 'hallway', keyLoc: 'treasury', hasKey: false, gateLocked: true, success: true, log: 'Hero enters Hallway.' },
          { action: 'move(hallway -> treasury)', heroLoc: 'treasury', keyLoc: 'treasury', hasKey: false, gateLocked: true, success: true, log: 'Hero steps into Treasury chamber.' },
          { action: 'pickup-key(bronze_key)', heroLoc: 'treasury', keyLoc: 'inventory', hasKey: true, gateLocked: true, success: true, log: 'Item acquired: Bronze Key equipped in inventory.' },
          { action: 'move(treasury -> hallway)', heroLoc: 'hallway', keyLoc: 'inventory', hasKey: true, gateLocked: true, success: true, log: 'Hero returns to Hallway with key in hand.' },
          { action: 'unlock-door(gate)', heroLoc: 'hallway', keyLoc: 'inventory', hasKey: true, gateLocked: false, success: true, log: 'Runic lock disengaged. Gate raised!' },
          { action: 'move(hallway -> gate)', heroLoc: 'gate', keyLoc: 'inventory', hasKey: true, gateLocked: false, success: true, log: 'Hero passes freely through open gateway.' },
          { action: 'move(gate -> exit)', heroLoc: 'exit', keyLoc: 'inventory', hasKey: true, gateLocked: false, success: true, log: 'GOAL ACHIEVED: Agent entered dimensional exit portal. Win rate: 100%.' },
        ]
      },

      pitch_black: {
        name: 'Pitch Black',
        subtitle: 'Epistemic Visibility & Hidden Pitfalls',
        gridW: 3,
        gridH: 2,
        tileSize: 96,
        offsetX: 175,
        offsetY: 100,
        rooms: {
          r00: { x: 0, y: 0, label: 'Start (Lit)', type: 'floor' },
          r01: { x: 1, y: 0, label: 'Abyss Pit',   type: 'hazard_dark' },
          r02: { x: 2, y: 0, label: 'Exit Portal', type: 'exit_goal' },
          r10: { x: 0, y: 1, label: 'South West',  type: 'floor' },
          r11: { x: 1, y: 1, label: 'Light Switch',type: 'floor' },
          r12: { x: 2, y: 1, label: 'South East',  type: 'floor' },
        },
        initialState: {
          heroLoc: 'r00',
          rejection: false,
        },
        flawedPlan: [
          {
            action: 'move(r00 -> r01)',
            heroLoc: 'r01',
            ghostLoc: 'r01',
            success: false,
            shockwave: true,
            log: 'HAZARD FATALITY: Agent stepped into unlit abyss pit! Precondition (is-lit r01) was omitted.',
            status: 'HAZARD_ELIMINATION'
          }
        ],
        repairedPlan: [
          { action: 'move(r00 -> r10)', heroLoc: 'r10', success: true, log: 'Agent routes safely through south hallway.' },
          { action: 'move(r10 -> r11)', heroLoc: 'r11', success: true, log: 'Agent advances along illuminated corridor.' },
          { action: 'move(r11 -> r12)', heroLoc: 'r12', success: true, log: 'Agent maneuvers past pitfall hazard zone.' },
          { action: 'move(r12 -> r02)', heroLoc: 'r02', success: true, log: 'GOAL ACHIEVED: Safe arrival at Exit Portal without hazard exposure.' },
        ]
      },

      sokoban: {
        name: 'Sokoban Puzzle',
        subtitle: 'Irreversible Dead-End & Safety Envelope Shield',
        gridW: 4,
        gridH: 2,
        tileSize: 84,
        offsetX: 150,
        offsetY: 110,
        rooms: {
          c00: { x: 0, y: 0, label: 'Hero Start', type: 'floor' },
          c01: { x: 1, y: 0, label: 'Cargo Box',  type: 'floor' },
          c02: { x: 2, y: 0, label: 'Target Pad', type: 'target' },
          c03: { x: 3, y: 0, label: 'Corner Pit', type: 'deadlock' },
          c10: { x: 0, y: 1, label: 'Detour A',   type: 'floor' },
          c11: { x: 1, y: 1, label: 'Detour B',   type: 'floor' },
          c12: { x: 2, y: 1, label: 'Detour C',   type: 'floor' },
          c13: { x: 3, y: 1, label: 'Wall Trap',  type: 'deadlock' },
        },
        initialState: {
          heroLoc: 'c00',
          boxLoc: 'c01',
          targetLoc: 'c02',
          rejection: false,
        },
        flawedPlan: [
          {
            action: 'push(box, c01 -> c03)',
            heroLoc: 'c01',
            boxLoc: 'c03',
            success: false,
            shockwave: true,
            log: 'SHIELD INTERCEPTION: Action push(c03) is IRREVERSIBLE! Virtual shield blocked execution (K_env = 0).',
            status: 'SAFETY_SHIELD_INTERCEPT'
          }
        ],
        repairedPlan: [
          { action: 'push(box, c01 -> c02)', heroLoc: 'c01', boxLoc: 'c02', success: true, log: 'GOAL ACHIEVED: Box pushed directly into Target receptacle!' }
        ]
      }
    };
  }

  initControls() {
    const levelSelect = document.getElementById('gameLevelSelect');
    if (levelSelect) {
      levelSelect.addEventListener('change', (e) => {
        this.currentLevel = e.target.value;
        this.resetGame();
      });
    }

    const modelSelect = document.getElementById('gameModelSelect');
    if (modelSelect) {
      modelSelect.addEventListener('change', (e) => {
        this.modelMode = e.target.value;
        this.resetGame();
      });
    }

    const playBtn = document.getElementById('gamePlayBtn');
    const stepBtn = document.getElementById('gameStepBtn');
    const resetBtn = document.getElementById('gameResetBtn');

    if (playBtn) {
      playBtn.addEventListener('click', () => {
        if (this.isPlaying) {
          this.pause();
          this.updatePlayButton(false);
        } else {
          this.play();
          this.updatePlayButton(true);
        }
      });
    }

    if (stepBtn) {
      stepBtn.addEventListener('click', () => {
        this.pause();
        this.updatePlayButton(false);
        this.stepForward();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.pause();
        this.updatePlayButton(false);
        this.resetGame();
      });
    }
  }

  updatePlayButton(isPlaying) {
    const playBtn = document.getElementById('gamePlayBtn');
    if (!playBtn) return;
    if (isPlaying) {
      playBtn.innerHTML = `
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        <span>Pause</span>
      `;
    } else {
      playBtn.innerHTML = `
        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        <span>Auto Play</span>
      `;
    }
  }

  resetPositions() {
    const lvl = this.levels[this.currentLevel];
    const initialLoc = lvl.rooms[lvl.initialState.heroLoc];
    if (initialLoc) {
      const cx = lvl.offsetX + initialLoc.x * lvl.tileSize + lvl.tileSize / 2;
      const cy = lvl.offsetY + initialLoc.y * lvl.tileSize + lvl.tileSize / 2;
      this.agentPos = { x: cx, y: cy };
      this.targetPos = { x: cx, y: cy };
      this.ghostPos = { x: cx, y: cy };
      this.targetGhostPos = { x: cx, y: cy };
    }
    this.rejectionPulse = 0;
  }

  resetGame() {
    this.currentStep = 0;
    this.resetPositions();
    this.updateLog('System initialized. Environment reset to initial state.');
    this.updateTelemetryHUD();
  }

  play() {
    this.isPlaying = true;
    this.playTimer = setInterval(() => {
      const activePlan = this.getActivePlan();
      if (this.currentStep < activePlan.length) {
        this.stepForward();
      } else {
        this.pause();
        this.updatePlayButton(false);
      }
    }, 1100);
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

  getCurrentState() {
    const lvl = this.levels[this.currentLevel];
    const plan = this.getActivePlan();
    if (this.currentStep === 0) {
      return lvl.initialState;
    }
    return plan[Math.min(this.currentStep - 1, plan.length - 1)];
  }

  stepForward() {
    const activePlan = this.getActivePlan();
    if (this.currentStep < activePlan.length) {
      const stepData = activePlan[this.currentStep];
      this.currentStep++;

      const lvl = this.levels[this.currentLevel];
      const targetRoom = lvl.rooms[stepData.heroLoc];
      if (targetRoom) {
        this.targetPos = {
          x: lvl.offsetX + targetRoom.x * lvl.tileSize + lvl.tileSize / 2,
          y: lvl.offsetY + targetRoom.y * lvl.tileSize + lvl.tileSize / 2
        };
      }

      if (stepData.ghostLoc && lvl.rooms[stepData.ghostLoc]) {
        const gr = lvl.rooms[stepData.ghostLoc];
        this.targetGhostPos = {
          x: lvl.offsetX + gr.x * lvl.tileSize + lvl.tileSize / 2,
          y: lvl.offsetY + gr.y * lvl.tileSize + lvl.tileSize / 2
        };
      }

      if (stepData.shockwave) {
        this.rejectionPulse = 45; // Triggers animated shockwave rings
      }

      this.updateLog(`[STEP ${this.currentStep}/${activePlan.length}] ${stepData.action} -> ${stepData.log}`);
      this.updateTelemetryHUD(stepData);
    }
  }

  updateTelemetryHUD(stepData = null) {
    const logBox = document.getElementById('mentalPlanBox');
    if (!logBox) return;

    if (this.currentLevel === 'dungeon_escape') {
      if (this.modelMode === 'flawed') {
        logBox.innerHTML = `
          <div class="space-y-1">
            <div class="text-xs text-slate-400 font-mono">1. move(entrance -> hallway)</div>
            <div class="text-xs text-rose-400 font-mono font-bold">2. unlock-door(gate) [OMITTED PRECONDITION]</div>
            <div class="text-xs text-slate-400 font-mono">3. move(hallway -> exit)</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400">
            <span class="text-rose-400 font-semibold font-mono">DIAGNOSTIC:</span> Mental model omitted <code class="text-rose-300 font-mono">(has-key ?p ?k)</code>. Heuristic A* planner hallucinated a 3-step sequence break.
          </div>
        `;
      } else {
        logBox.innerHTML = `
          <div class="space-y-1">
            <div class="text-xs text-slate-400 font-mono">1. move(entrance -> hallway)</div>
            <div class="text-xs text-amber-300 font-mono">2. move(hallway -> treasury)</div>
            <div class="text-xs text-amber-300 font-mono">3. pickup-key(bronze_key)</div>
            <div class="text-xs text-slate-400 font-mono">4. move(treasury -> hallway)</div>
            <div class="text-xs text-emerald-400 font-mono font-semibold">5. unlock-door(gate) [KEY VERIFIED]</div>
            <div class="text-xs text-emerald-400 font-mono">6. move(gate -> exit)</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-emerald-400">
            <span class="font-semibold font-mono">REPAIRED:</span> CEG-OMR precondition-delete coherence restored. Legal plan execution achieves 100% PESR.
          </div>
        `;
      }
    }
  }

  updateLog(msg) {
    const logBox = document.getElementById('gameConsoleLog');
    if (!logBox) return;

    const line = document.createElement('div');
    line.className = 'py-0.5 border-b border-slate-900/60 font-mono text-[11px]';

    if (msg.includes('REJECTION') || msg.includes('FATALITY') || msg.includes('blocked')) {
      line.className += ' text-rose-400 font-medium';
    } else if (msg.includes('GOAL ACHIEVED') || msg.includes('REPAIRED') || msg.includes('disengaged')) {
      line.className += ' text-emerald-400 font-medium';
    } else if (msg.includes('equipped') || msg.includes('Bronze Key')) {
      line.className += ' text-amber-300';
    } else {
      line.className += ' text-slate-400';
    }

    line.textContent = msg;
    logBox.appendChild(line);
    logBox.scrollTop = logBox.scrollHeight;
  }

  startAnimationLoop() {
    const loop = (timestamp) => {
      this.animTime = timestamp * 0.003;

      // Smooth Position Lerp for Hero
      const lerpFactor = 0.18;
      this.agentPos.x += (this.targetPos.x - this.agentPos.x) * lerpFactor;
      this.agentPos.y += (this.targetPos.y - this.agentPos.y) * lerpFactor;

      // Lerp for Ghost Hero
      this.ghostPos.x += (this.targetGhostPos.x - this.ghostPos.x) * lerpFactor;
      this.ghostPos.y += (this.targetGhostPos.y - this.ghostPos.y) * lerpFactor;

      if (this.rejectionPulse > 0) {
        this.rejectionPulse--;
      }

      this.render();
      this.animFrameId = requestAnimationFrame(loop);
    };
    this.animFrameId = requestAnimationFrame(loop);
  }

  render() {
    this.ctx.clearRect(0, 0, this.width, this.height);

    // Deep Canvas Base
    this.ctx.fillStyle = '#010204';
    this.ctx.fillRect(0, 0, this.width, this.height);

    // Subtle Grid Blueprint Pattern
    this.drawBlueprintGrid();

    if (this.currentLevel === 'dungeon_escape') {
      this.renderDungeonEscape();
    } else if (this.currentLevel === 'pitch_black') {
      this.renderPitchBlack();
    } else if (this.currentLevel === 'sokoban') {
      this.renderSokoban();
    }

    // Top HUD Status Overlay
    this.renderCanvasHUD();
  }

  drawBlueprintGrid() {
    this.ctx.strokeStyle = 'rgba(35, 37, 42, 0.4)';
    this.ctx.lineWidth = 1;
    const step = 20;
    this.ctx.beginPath();
    for (let x = 0; x < this.width; x += step) {
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, this.height);
    }
    for (let y = 0; y < this.height; y += step) {
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(this.width, y);
    }
    this.ctx.stroke();
  }

  renderDungeonEscape() {
    const lvl = this.levels.dungeon_escape;
    const state = this.getCurrentState();
    const { tileSize, offsetX, offsetY } = lvl;

    // 1. Draw Connecting Hallway Corridors
    this.ctx.strokeStyle = '#1e293b';
    this.ctx.lineWidth = 10;
    this.ctx.lineCap = 'round';
    this.drawCorridor(0, 1, 1, 1, tileSize, offsetX, offsetY); // Entrance - Hallway
    this.drawCorridor(1, 1, 1, 0, tileSize, offsetX, offsetY); // Hallway - Treasury
    this.drawCorridor(1, 1, 2, 1, tileSize, offsetX, offsetY); // Hallway - Gate
    this.drawCorridor(2, 1, 3, 1, tileSize, offsetX, offsetY); // Gate - Exit

    // Inner corridor highlight line
    this.ctx.strokeStyle = '#334155';
    this.ctx.lineWidth = 2;
    this.drawCorridor(0, 1, 1, 1, tileSize, offsetX, offsetY);
    this.drawCorridor(1, 1, 1, 0, tileSize, offsetX, offsetY);
    this.drawCorridor(1, 1, 2, 1, tileSize, offsetX, offsetY);
    this.drawCorridor(2, 1, 3, 1, tileSize, offsetX, offsetY);

    // 2. Draw Hallucinated Ghost Trajectory if in Flawed Mode
    if (this.modelMode === 'flawed') {
      this.drawGhostTrajectory([
        { x: offsetX + 0 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
        { x: offsetX + 1 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
        { x: offsetX + 2 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
        { x: offsetX + 3 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
      ]);
    }

    // 3. Draw Room Chambers
    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      // Base Flagstone Tile
      this.drawFlagstoneTile(rx, ry, tileSize - 10, r.label);

      // Room Specific Game Objects
      if (roomId === 'treasury') {
        const isPickedUp = state.hasKey;
        this.drawVectorKey(rx + (tileSize - 10) / 2, ry + (tileSize - 10) / 2 - 2, isPickedUp);
      } else if (roomId === 'gate') {
        const isLocked = state.gateLocked;
        const isBlocked = this.rejectionPulse > 0;
        this.drawVectorGate(rx + (tileSize - 10) / 2, ry + (tileSize - 10) / 2 - 2, isLocked, isBlocked);
      } else if (roomId === 'exit') {
        this.drawVectorPortal(rx + (tileSize - 10) / 2, ry + (tileSize - 10) / 2 - 2);
      }
    }

    // 4. Draw Ghost Hero (Mental Shortcut Projection)
    if (this.modelMode === 'flawed' && this.currentStep > 0) {
      this.drawVectorGhostHero(this.ghostPos.x, this.ghostPos.y);
    }

    // 5. Draw Concrete Hero Agent
    this.drawVectorHero(this.agentPos.x, this.agentPos.y, state.hasKey);

    // 6. Draw Barrier Shockwave Pulse if Action was Rejected
    if (this.rejectionPulse > 0) {
      const gateRoom = lvl.rooms.gate;
      const gx = offsetX + gateRoom.x * tileSize + (tileSize - 10) / 2;
      const gy = offsetY + gateRoom.y * tileSize + (tileSize - 10) / 2;
      this.drawShockwaveRings(gx, gy, 45 - this.rejectionPulse);
    }
  }

  renderPitchBlack() {
    const lvl = this.levels.pitch_black;
    const state = this.getCurrentState();
    const { tileSize, offsetX, offsetY } = lvl;

    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      if (r.type === 'hazard_dark') {
        this.drawVectorHazardPit(rx, ry, tileSize - 12);
      } else if (r.type === 'exit_goal') {
        this.drawFlagstoneTile(rx, ry, tileSize - 12, r.label);
        this.drawVectorPortal(rx + (tileSize - 12) / 2, ry + (tileSize - 12) / 2);
      } else {
        this.drawFlagstoneTile(rx, ry, tileSize - 12, r.label);
        // Small ambient illuminated sensor dot
        this.ctx.beginPath();
        this.ctx.arc(rx + (tileSize - 12) / 2, ry + (tileSize - 12) / 2 - 4, 4, 0, Math.PI * 2);
        this.ctx.fillStyle = '#38bdf8';
        this.ctx.shadowColor = '#38bdf8';
        this.ctx.shadowBlur = 8;
        this.ctx.fill();
        this.ctx.shadowBlur = 0;
      }
    }

    // Draw Hero
    this.drawVectorHero(this.agentPos.x, this.agentPos.y, false);

    if (this.rejectionPulse > 0) {
      this.drawShockwaveRings(this.agentPos.x, this.agentPos.y, 45 - this.rejectionPulse);
    }
  }

  renderSokoban() {
    const lvl = this.levels.sokoban;
    const state = this.getCurrentState();
    const { tileSize, offsetX, offsetY } = lvl;

    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      if (r.type === 'target') {
        this.drawVectorTarget(rx, ry, tileSize - 10);
      } else if (r.type === 'deadlock') {
        this.drawVectorDeadlockCorner(rx, ry, tileSize - 10);
      } else {
        this.drawFlagstoneTile(rx, ry, tileSize - 10, r.label);
      }
    }

    // Draw Cargo Box
    const boxRoom = lvl.rooms[state.boxLoc || 'c01'];
    if (boxRoom) {
      const bx = offsetX + boxRoom.x * tileSize + (tileSize - 10) / 2;
      const by = offsetY + boxRoom.y * tileSize + (tileSize - 10) / 2;
      this.drawVectorCrate(bx, by);
    }

    // Draw Hero
    this.drawVectorHero(this.agentPos.x, this.agentPos.y, false);

    if (this.rejectionPulse > 0) {
      this.drawShockwaveRings(this.agentPos.x, this.agentPos.y, 45 - this.rejectionPulse);
    }
  }

  /* --------------------------------------------------------------------------
     PROCEDURAL VECTOR GRAPHICS PRIMITIVES (ZERO EMOJIS)
     -------------------------------------------------------------------------- */

  drawFlagstoneTile(x, y, size, label) {
    // Outer Border & Stone Base
    this.ctx.fillStyle = '#0f141f';
    this.ctx.strokeStyle = '#232a38';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.roundRect(x, y, size, size, 6);
    this.ctx.fill();
    this.ctx.stroke();

    // Subtle stone floor beveling line
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    this.ctx.beginPath();
    this.ctx.moveTo(x + 4, y + 4);
    this.ctx.lineTo(x + size - 4, y + 4);
    this.ctx.stroke();

    // Label at bottom
    if (label) {
      this.ctx.fillStyle = '#64748b';
      this.ctx.font = '500 10px Inter, sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText(label, x + size / 2, y + size - 8);
    }
  }

  drawVectorHero(cx, cy, hasKey) {
    this.ctx.save();
    this.ctx.translate(cx, cy);

    // Directional orientation ring
    this.ctx.strokeStyle = 'rgba(94, 106, 210, 0.3)';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 22, 0, Math.PI * 2);
    this.ctx.stroke();

    // Metallic Chassis
    this.ctx.fillStyle = '#111827';
    this.ctx.strokeStyle = '#5e6ad2';
    this.ctx.lineWidth = 2.5;
    this.ctx.shadowColor = 'rgba(94, 106, 210, 0.5)';
    this.ctx.shadowBlur = 10;
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 16, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.shadowBlur = 0;

    // Glowing Optical Sensor Visor
    this.ctx.fillStyle = '#38bdf8';
    this.ctx.beginPath();
    this.ctx.roundRect(-8, -4, 16, 8, 4);
    this.ctx.fill();

    // Center lens dot
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 2, 0, Math.PI * 2);
    this.ctx.fill();

    // Direction Pointer
    this.ctx.fillStyle = '#828fff';
    this.ctx.beginPath();
    this.ctx.moveTo(0, -18);
    this.ctx.lineTo(4, -12);
    this.ctx.lineTo(-4, -12);
    this.ctx.closePath();
    this.ctx.fill();

    // If key acquired: Draw equipped inventory badge
    if (hasKey) {
      this.ctx.fillStyle = '#f59e0b';
      this.ctx.shadowColor = '#f59e0b';
      this.ctx.shadowBlur = 8;
      this.ctx.beginPath();
      this.ctx.arc(12, -12, 5, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.shadowBlur = 0;
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.lineWidth = 1;
      this.ctx.stroke();
    }

    this.ctx.restore();
  }

  drawVectorGhostHero(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);

    // Phantom Glitch Aura
    this.ctx.strokeStyle = 'rgba(244, 63, 94, 0.5)';
    this.ctx.lineWidth = 1.5;
    this.ctx.setLineDash([3, 3]);
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 20, 0, Math.PI * 2);
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    // Translucent Ghost Chassis
    this.ctx.fillStyle = 'rgba(225, 29, 72, 0.35)';
    this.ctx.strokeStyle = '#fda4af';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 15, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.stroke();

    // Flawed Visor
    this.ctx.fillStyle = '#f43f5e';
    this.ctx.beginPath();
    this.ctx.roundRect(-6, -3, 12, 6, 3);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawGhostTrajectory(points) {
    if (points.length < 2) return;
    this.ctx.save();
    this.ctx.strokeStyle = 'rgba(244, 63, 94, 0.4)';
    this.ctx.lineWidth = 2;
    this.ctx.setLineDash([5, 5]);
    this.ctx.beginPath();
    this.ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
      this.ctx.lineTo(points[i].x, points[i].y);
    }
    this.ctx.stroke();
    this.ctx.setLineDash([]);
    this.ctx.restore();
  }

  drawVectorKey(cx, cy, isPickedUp) {
    if (isPickedUp) {
      // Empty pedestal indicator
      this.ctx.strokeStyle = 'rgba(245, 158, 11, 0.2)';
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.arc(cx, cy, 14, 0, Math.PI * 2);
      this.ctx.stroke();
      return;
    }

    this.ctx.save();
    this.ctx.translate(cx, cy);

    // Golden Halo
    const pulse = Math.sin(this.animTime * 3) * 3;
    this.ctx.fillStyle = 'rgba(245, 158, 11, 0.15)';
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 16 + pulse, 0, Math.PI * 2);
    this.ctx.fill();

    // Key Bow (Ring)
    this.ctx.strokeStyle = '#f59e0b';
    this.ctx.lineWidth = 3;
    this.ctx.beginPath();
    this.ctx.arc(-6, 0, 6, 0, Math.PI * 2);
    this.ctx.stroke();

    // Key Shaft
    this.ctx.beginPath();
    this.ctx.moveTo(0, 0);
    this.ctx.lineTo(10, 0);
    // Teeth
    this.ctx.lineTo(10, 4);
    this.ctx.moveTo(7, 0);
    this.ctx.lineTo(7, 3);
    this.ctx.stroke();

    // Gilded Sparkle
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(-6, 0, 1.5, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawVectorGate(cx, cy, isLocked, isBlocked) {
    this.ctx.save();
    this.ctx.translate(cx, cy);

    // Stone Archway Frame
    this.ctx.fillStyle = '#0b0f19';
    this.ctx.strokeStyle = isLocked ? '#475569' : '#10b981';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.roundRect(-20, -22, 40, 44, 4);
    this.ctx.fill();
    this.ctx.stroke();

    if (isLocked) {
      // Heavy Portcullis Vertical Bars
      this.ctx.strokeStyle = '#64748b';
      this.ctx.lineWidth = 2;
      for (let x = -12; x <= 12; x += 8) {
        this.ctx.beginPath();
        this.ctx.moveTo(x, -18);
        this.ctx.lineTo(x, 18);
        this.ctx.stroke();
      }

      // Center Runic Lock Plate
      this.ctx.fillStyle = isBlocked ? '#f43f5e' : '#1e293b';
      this.ctx.strokeStyle = isBlocked ? '#ffffff' : '#f43f5e';
      this.ctx.lineWidth = 1.5;
      this.ctx.beginPath();
      this.ctx.arc(0, 0, 9, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.stroke();

      // Padlock Shackle
      this.ctx.strokeStyle = '#ffffff';
      this.ctx.lineWidth = 1.5;
      this.ctx.beginPath();
      this.ctx.arc(0, -2, 4, Math.PI, 0);
      this.ctx.rect(-3, -2, 6, 5);
      this.ctx.stroke();
    } else {
      // Gate Unlocked & Raised: Open passage aura
      this.ctx.fillStyle = 'rgba(16, 185, 129, 0.2)';
      this.ctx.beginPath();
      this.ctx.roundRect(-16, -18, 32, 36, 4);
      this.ctx.fill();

      // Green upward open chevrons
      this.ctx.strokeStyle = '#10b981';
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.moveTo(-6, 4);
      this.ctx.lineTo(0, -2);
      this.ctx.lineTo(6, 4);
      this.ctx.moveTo(-6, -2);
      this.ctx.lineTo(0, -8);
      this.ctx.lineTo(6, -2);
      this.ctx.stroke();
    }

    this.ctx.restore();
  }

  drawVectorPortal(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);

    const rotation = this.animTime;

    // Cosmic Swirling Rings
    this.ctx.strokeStyle = 'rgba(139, 92, 246, 0.4)';
    this.ctx.lineWidth = 2;
    this.ctx.setLineDash([6, 4]);
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 18, rotation, rotation + Math.PI * 2);
    this.ctx.stroke();

    this.ctx.strokeStyle = 'rgba(167, 139, 250, 0.7)';
    this.ctx.setLineDash([4, 2]);
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 12, -rotation * 1.5, -rotation * 1.5 + Math.PI * 2);
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    // Core Singularity
    this.ctx.fillStyle = '#581c87';
    this.ctx.shadowColor = '#a855f7';
    this.ctx.shadowBlur = 12;
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 7, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;

    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 2.5, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawVectorHazardPit(x, y, size) {
    this.ctx.fillStyle = '#050508';
    this.ctx.strokeStyle = '#ef4444';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.roundRect(x, y, size, size, 6);
    this.ctx.fill();
    this.ctx.stroke();

    // Spikes
    this.ctx.fillStyle = '#27272a';
    this.ctx.strokeStyle = '#71717a';
    this.ctx.lineWidth = 1;
    const spikeW = size / 4;
    for (let i = 0; i < 4; i++) {
      this.ctx.beginPath();
      this.ctx.moveTo(x + i * spikeW, y + size);
      this.ctx.lineTo(x + (i + 0.5) * spikeW, y + size / 2);
      this.ctx.lineTo(x + (i + 1) * spikeW, y + size);
      this.ctx.closePath();
      this.ctx.fill();
      this.ctx.stroke();
    }

    // Hazard text
    this.ctx.fillStyle = '#ef4444';
    this.ctx.font = '600 9px Inter, sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('HAZARD PIT', x + size / 2, y + 16);
  }

  drawVectorTarget(x, y, size) {
    this.drawFlagstoneTile(x, y, size, 'Target Pad');
    this.ctx.save();
    this.ctx.translate(x + size / 2, y + size / 2 - 4);

    this.ctx.strokeStyle = '#10b981';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 14, 0, Math.PI * 2);
    this.ctx.stroke();

    this.ctx.fillStyle = '#059669';
    this.ctx.beginPath();
    this.ctx.arc(0, 0, 7, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.restore();
  }

  drawVectorDeadlockCorner(x, y, size) {
    this.ctx.fillStyle = '#18181b';
    this.ctx.strokeStyle = '#ef4444';
    this.ctx.lineWidth = 1.5;
    this.ctx.setLineDash([4, 4]);
    this.ctx.beginPath();
    this.ctx.roundRect(x, y, size, size, 6);
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.setLineDash([]);

    this.ctx.fillStyle = '#f87171';
    this.ctx.font = '600 9px Inter, sans-serif';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('DEAD-END', x + size / 2, y + size / 2);
  }

  drawVectorCrate(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);

    this.ctx.fillStyle = '#78350f';
    this.ctx.strokeStyle = '#d97706';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.roundRect(-16, -16, 32, 32, 4);
    this.ctx.fill();
    this.ctx.stroke();

    // Cross braces
    this.ctx.strokeStyle = '#92400e';
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();
    this.ctx.moveTo(-14, -14);
    this.ctx.lineTo(14, 14);
    this.ctx.moveTo(14, -14);
    this.ctx.lineTo(-14, 14);
    this.ctx.stroke();

    this.ctx.restore();
  }

  drawShockwaveRings(cx, cy, progress) {
    const maxRadius = 40;
    const currentR = (progress / 45) * maxRadius;
    const alpha = Math.max(0, 1 - progress / 45);

    this.ctx.strokeStyle = `rgba(244, 63, 94, ${alpha})`;
    this.ctx.lineWidth = 3;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, currentR, 0, Math.PI * 2);
    this.ctx.stroke();

    this.ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.7})`;
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.arc(cx, cy, currentR * 0.6, 0, Math.PI * 2);
    this.ctx.stroke();
  }

  drawCorridor(x1, y1, x2, y2, size, ox, oy) {
    const cx1 = ox + x1 * size + (size - 10) / 2;
    const cy1 = oy + y1 * size + (size - 10) / 2;
    const cx2 = ox + x2 * size + (size - 10) / 2;
    const cy2 = oy + y2 * size + (size - 10) / 2;

    this.ctx.beginPath();
    this.ctx.moveTo(cx1, cy1);
    this.ctx.lineTo(cx2, cy2);
    this.ctx.stroke();
  }

  renderCanvasHUD() {
    const isFlawed = this.modelMode === 'flawed';
    this.ctx.save();

    // Pill badge in top left
    this.ctx.fillStyle = isFlawed ? 'rgba(244, 63, 94, 0.1)' : 'rgba(16, 185, 129, 0.1)';
    this.ctx.strokeStyle = isFlawed ? 'rgba(244, 63, 94, 0.4)' : 'rgba(16, 185, 129, 0.4)';
    this.ctx.lineWidth = 1;
    this.ctx.beginPath();
    this.ctx.roundRect(14, 14, 280, 28, 6);
    this.ctx.fill();
    this.ctx.stroke();

    // Dot indicator
    this.ctx.fillStyle = isFlawed ? '#f43f5e' : '#10b981';
    this.ctx.beginPath();
    this.ctx.arc(26, 28, 4, 0, Math.PI * 2);
    this.ctx.fill();

    // Typography Label
    this.ctx.fillStyle = isFlawed ? '#fda4af' : '#6ee7b7';
    this.ctx.font = '600 11px Inter, sans-serif';
    this.ctx.textAlign = 'left';
    const text = isFlawed 
      ? 'FLAWED MODEL: Sequence-Break Exploit' 
      : 'CEG-OMR REPAIRED: Verified Policy';
    this.ctx.fillText(text, 38, 32);

    this.ctx.restore();
  }
}

window.GameAIVisualizer = GameAIVisualizer;
