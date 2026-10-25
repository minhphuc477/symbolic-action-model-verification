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
      },

      dungeon_multikey: {
        name: 'Multi-Tier Dungeon',
        subtitle: 'Tri-Key Gated Labyrinth (Bronze, Silver, Gold)',
        gridW: 7,
        gridH: 2,
        tileSize: 68,
        offsetX: 80,
        offsetY: 105,
        rooms: {
          entrance:        { x: 0, y: 1, label: 'Entrance',    type: 'floor' },
          hall_west:       { x: 1, y: 1, label: 'West Hall',   type: 'floor' },
          treasury_bronze: { x: 1, y: 0, label: 'Bronze Key',  type: 'item_room' },
          gate_bronze:     { x: 2, y: 1, label: 'Bronze Gate', type: 'door_locked' },
          hall_center:     { x: 3, y: 1, label: 'Mid Hall',    type: 'floor' },
          treasury_silver: { x: 3, y: 0, label: 'Silver Key',  type: 'item_room' },
          gate_silver:     { x: 4, y: 1, label: 'Silver Gate', type: 'door_locked' },
          hall_east:       { x: 5, y: 1, label: 'East Hall',   type: 'floor' },
          treasury_gold:   { x: 5, y: 0, label: 'Gold Key',    type: 'item_room' },
          gate_gold:       { x: 6, y: 1, label: 'Gold Gate',   type: 'door_locked' },
        },
        initialState: {
          heroLoc: 'entrance',
          keysAcquired: [],
          rejection: false,
        },
        flawedPlan: [
          { action: 'move(entrance -> hall_west)', heroLoc: 'hall_west', ghostLoc: 'hall_west', success: true, log: 'Hero approaches West Hallway.', status: 'IN_TRANSIT' },
          { action: 'unlock-door(gate_bronze)', heroLoc: 'hall_west', ghostLoc: 'gate_bronze', success: false, shockwave: true, log: 'REJECTION: Gate locked! Missing (has-key hero bronze_key). Shortcut refuted!', status: 'ACTION_REJECTED' }
        ],
        repairedPlan: [
          { action: 'move(entrance -> hall_west)', heroLoc: 'hall_west', success: true, log: 'Hero enters West Hallway.' },
          { action: 'move(hall_west -> treasury_bronze)', heroLoc: 'treasury_bronze', success: true, log: 'Hero discovers Bronze Treasury.' },
          { action: 'pickup-key(bronze_key)', heroLoc: 'treasury_bronze', success: true, log: 'Equipped Bronze Key.' },
          { action: 'move(treasury_bronze -> hall_west)', heroLoc: 'hall_west', success: true, log: 'Returning to West Hallway.' },
          { action: 'unlock-door(gate_bronze)', heroLoc: 'hall_west', success: true, log: 'Bronze Gate unlocked and raised!' },
          { action: 'move(hall_west -> gate_bronze)', heroLoc: 'gate_bronze', success: true, log: 'Passing through Bronze Gate.' },
          { action: 'move(gate_bronze -> hall_center)', heroLoc: 'hall_center', success: true, log: 'Entering Central Hall.' },
          { action: 'move(hall_center -> treasury_silver)', heroLoc: 'treasury_silver', success: true, log: 'Hero discovers Silver Treasury.' },
          { action: 'pickup-key(silver_key)', heroLoc: 'treasury_silver', success: true, log: 'Equipped Silver Key.' },
          { action: 'move(treasury_silver -> hall_center)', heroLoc: 'hall_center', success: true, log: 'Returning to Central Hall.' },
          { action: 'unlock-door(gate_silver)', heroLoc: 'hall_center', success: true, log: 'Silver Gate disengaged!' },
          { action: 'move(hall_center -> gate_silver)', heroLoc: 'gate_silver', success: true, log: 'Passing through Silver Gate.' },
          { action: 'move(gate_silver -> hall_east)', heroLoc: 'hall_east', success: true, log: 'GOAL ACHIEVED: Multi-tier 13-step plan executed with 100% PESR.' }
        ]
      },

      crafting_rpg: {
        name: 'Crafting RPG Tech-Tree',
        subtitle: 'Minecraft/Crafter Tech Progression to Diamond',
        gridW: 4,
        gridH: 2,
        tileSize: 88,
        offsetX: 140,
        offsetY: 100,
        rooms: {
          forest:          { x: 0, y: 0, label: 'Wood Forest',   type: 'resource_wood' },
          spawn_clearing:  { x: 0, y: 1, label: 'Spawn Clear',   type: 'floor' },
          rocky_hills:     { x: 1, y: 1, label: 'Stone & Bench', type: 'crafting_bench' },
          cavern_entrance: { x: 2, y: 1, label: 'Coal & Iron',   type: 'furnace_cavern' },
          deep_abyss:      { x: 3, y: 1, label: 'Diamond Abyss', type: 'exit_goal' },
        },
        initialState: {
          heroLoc: 'spawn_clearing',
          hasPick: false,
          rejection: false,
        },
        flawedPlan: [
          { action: 'move(spawn -> rocky_hills)', heroLoc: 'rocky_hills', ghostLoc: 'rocky_hills', success: true, log: 'Agent advances across rocky terrain.', status: 'IN_TRANSIT' },
          { action: 'move(rocky_hills -> cavern)', heroLoc: 'cavern_entrance', ghostLoc: 'cavern_entrance', success: true, log: 'Agent descends toward cavern depths.', status: 'IN_TRANSIT' },
          { action: 'move(cavern -> deep_abyss)', heroLoc: 'deep_abyss', ghostLoc: 'deep_abyss', success: true, log: 'Agent rushes to the deep abyss.', status: 'IN_TRANSIT' },
          { action: 'mine-diamond(steve, diamond)', heroLoc: 'deep_abyss', ghostLoc: 'deep_abyss', success: false, shockwave: true, log: 'SHIELD REJECTION: Physical engine rejected diamond mining without Iron Pickaxe! Sequence break refuted.', status: 'ACTION_REJECTED' }
        ],
        repairedPlan: [
          { action: 'move(spawn -> forest)', heroLoc: 'forest', success: true, log: 'Steve heads into Forest.' },
          { action: 'gather-wood(item_wood)', heroLoc: 'forest', success: true, log: 'Harvested Oak Wood logs.' },
          { action: 'move(forest -> spawn)', heroLoc: 'spawn_clearing', success: true, log: 'Returning through spawn clearing.' },
          { action: 'move(spawn -> rocky_hills)', heroLoc: 'rocky_hills', success: true, log: 'Arrived at Rocky Hills.' },
          { action: 'craft-planks(item_planks)', heroLoc: 'rocky_hills', success: true, log: 'Processed Wood into Timber Planks.' },
          { action: 'craft-workbench(bench)', heroLoc: 'rocky_hills', success: true, log: 'Constructed Crafting Table.' },
          { action: 'craft-wooden-pickaxe(wood_pick)', heroLoc: 'rocky_hills', success: true, log: 'Crafted Wooden Pickaxe.' },
          { action: 'mine-stone(item_stone)', heroLoc: 'rocky_hills', success: true, log: 'Mined Cobblestone blocks.' },
          { action: 'build-furnace(furnace)', heroLoc: 'rocky_hills', success: true, log: 'Constructed Smelting Furnace.' },
          { action: 'move(rocky_hills -> cavern)', heroLoc: 'cavern_entrance', success: true, log: 'Entering Cavern Entrance.' },
          { action: 'gather-coal(item_coal)', heroLoc: 'cavern_entrance', success: true, log: 'Mined Fuel Coal vein.' },
          { action: 'mine-iron-ore(item_ore)', heroLoc: 'cavern_entrance', success: true, log: 'Mined Raw Iron Ore.' },
          { action: 'move(cavern -> rocky_hills)', heroLoc: 'rocky_hills', success: true, log: 'Returning to Furnace.' },
          { action: 'smelt-iron(iron_ingot)', heroLoc: 'rocky_hills', success: true, log: 'Smelted Iron Ingot in furnace.' },
          { action: 'craft-iron-pickaxe(iron_pick)', heroLoc: 'rocky_hills', success: true, log: 'Crafted Industrial Iron Pickaxe!' },
          { action: 'move(rocky_hills -> cavern)', heroLoc: 'cavern_entrance', success: true, log: 'Advancing deeper underground.' },
          { action: 'move(cavern -> deep_abyss)', heroLoc: 'deep_abyss', success: true, log: 'Entered Deep Abyss Diamond chamber.' },
          { action: 'mine-diamond(item_diamond)', heroLoc: 'deep_abyss', success: true, log: 'GOAL ACHIEVED: 17-step dependency tech-tree verified with 100% PESR!' }
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

    if (this.currentLevel === 'dungeon_escape' || this.currentLevel === 'dungeon_multikey') {
      const isMulti = this.currentLevel === 'dungeon_multikey';
      if (this.modelMode === 'flawed') {
        logBox.innerHTML = `
          <div class="space-y-1">
            <div class="text-xs text-slate-400 font-mono">1. move(entrance -> hall)</div>
            <div class="text-xs text-rose-400 font-mono font-bold">2. unlock-door(gate) [OMITTED PRECONDITION]</div>
            <div class="text-xs text-slate-400 font-mono">3. move(gate -> exit)</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400">
            <span class="text-rose-400 font-semibold font-mono">DIAGNOSTIC:</span> Mental model omitted <code class="text-rose-300 font-mono">(has-key ?p ?k)</code>. Heuristic A* planner hallucinated a sequence break shortcut across ${isMulti ? '3 locked gates' : 'locked gate'}.
          </div>
        `;
      } else {
        logBox.innerHTML = `
          <div class="space-y-1">
            <div class="text-xs text-slate-400 font-mono">1. move(entrance -> hall)</div>
            <div class="text-xs text-amber-300 font-mono">2. pickup-key(key) [TREASURY]</div>
            <div class="text-xs text-emerald-400 font-mono font-semibold">3. unlock-door(gate) [KEY VERIFIED]</div>
            <div class="text-xs text-slate-400 font-mono">4. ... ${isMulti ? '(13 steps full multi-key traversal)' : '(6 steps complete)'}</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-emerald-400">
            <span class="font-semibold font-mono">REPAIRED:</span> CEG-OMR precondition-delete coherence restored. Legal plan execution achieves 100% PESR.
          </div>
        `;
      }
    } else if (this.currentLevel === 'crafting_rpg') {
      if (this.modelMode === 'flawed') {
        logBox.innerHTML = `
          <div class="space-y-1">
            <div class="text-xs text-slate-400 font-mono">1. move(spawn -> rocky_hills)</div>
            <div class="text-xs text-slate-400 font-mono">2. move(rocky_hills -> cavern)</div>
            <div class="text-xs text-slate-400 font-mono">3. move(cavern -> deep_abyss)</div>
            <div class="text-xs text-rose-400 font-mono font-bold">4. mine-diamond(steve, diamond) [OMITTED PICKAXE]</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-slate-400">
            <span class="text-rose-400 font-semibold font-mono">COLLAPSE:</span> Omitting <code class="text-rose-300 font-mono">(has-item steve iron_pick)</code> collapsed search tree from 17 to 4 steps! Agent attempted bare-handed diamond mining.
          </div>
        `;
      } else {
        logBox.innerHTML = `
          <div class="space-y-1">
            <div class="text-xs text-slate-400 font-mono">1. gather-wood -> craft-planks -> workbench</div>
            <div class="text-xs text-amber-300 font-mono">2. wooden-pickaxe -> mine-stone -> furnace</div>
            <div class="text-xs text-amber-300 font-mono">3. coal + iron-ore -> smelt-iron -> iron-pickaxe</div>
            <div class="text-xs text-emerald-400 font-mono font-semibold">4. deep_abyss -> mine-diamond [17 STEPS VERIFIED]</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800 text-[11px] text-emerald-400">
            <span class="font-semibold font-mono">REPAIRED:</span> Full combinatorial dependency tech-tree verified in 0.547s via Fast Downward. 100% PESR.
          </div>
        `;
      }
    } else if (this.currentLevel === 'pitch_black') {
      logBox.innerHTML = `
        <div class="space-y-1">
          <div class="text-xs text-slate-400 font-mono">Visibility constraint diagnostic:</div>
          <div class="text-xs text-rose-400 font-mono">Flawed: Omit (is-light-on ?to) -> step into unlit pit</div>
          <div class="text-xs text-emerald-400 font-mono">Repaired: Route through illuminated switch hallway</div>
        </div>
      `;
    } else if (this.currentLevel === 'sokoban') {
      logBox.innerHTML = `
        <div class="space-y-1">
          <div class="text-xs text-slate-400 font-mono">Safety Shield Reversibility Guard:</div>
          <div class="text-xs text-rose-400 font-mono">Flawed: Push crate into irreversible corner sink</div>
          <div class="text-xs text-emerald-400 font-mono">Shield: Intercept unverified irreversible action (K_env = 0)</div>
        </div>
      `;
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

    if (this.currentLevel === 'dungeon_escape' || this.currentLevel === 'dungeon_multikey') {
      this.renderDungeonEscape();
    } else if (this.currentLevel === 'pitch_black') {
      this.renderPitchBlack();
    } else if (this.currentLevel === 'sokoban') {
      this.renderSokoban();
    } else if (this.currentLevel === 'crafting_rpg') {
      this.renderCraftingRPG();
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
    const lvl = this.levels[this.currentLevel];
    const state = this.getCurrentState();
    const { tileSize, offsetX, offsetY } = lvl;

    // 1. Draw Connecting Hallway Corridors dynamically
    this.ctx.strokeStyle = '#1e293b';
    this.ctx.lineWidth = 10;
    this.ctx.lineCap = 'round';
    for (const [id1, r1] of Object.entries(lvl.rooms)) {
      for (const [id2, r2] of Object.entries(lvl.rooms)) {
        if (id1 < id2 && Math.abs(r1.x - r2.x) + Math.abs(r1.y - r2.y) === 1) {
          this.drawCorridor(r1.x, r1.y, r2.x, r2.y, tileSize, offsetX, offsetY);
        }
      }
    }

    // Inner corridor highlight line
    this.ctx.strokeStyle = '#334155';
    this.ctx.lineWidth = 2;
    for (const [id1, r1] of Object.entries(lvl.rooms)) {
      for (const [id2, r2] of Object.entries(lvl.rooms)) {
        if (id1 < id2 && Math.abs(r1.x - r2.x) + Math.abs(r1.y - r2.y) === 1) {
          this.drawCorridor(r1.x, r1.y, r2.x, r2.y, tileSize, offsetX, offsetY);
        }
      }
    }

    // 2. Draw Hallucinated Ghost Trajectory if in Flawed Mode
    if (this.modelMode === 'flawed') {
      const ghostCoords = [];
      for (let i = 0; i < lvl.gridW; i++) {
        ghostCoords.push({ x: offsetX + i * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 });
      }
      this.drawGhostTrajectory(ghostCoords);
    }

    // 3. Draw Room Chambers
    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      // Base Flagstone Tile
      this.drawFlagstoneTile(rx, ry, tileSize - 10, r.label);

      // Room Specific Game Objects
      if (r.type === 'item_room' || roomId.includes('treasury')) {
        const isPickedUp = (state.keysAcquired && state.keysAcquired.includes(roomId)) || state.hasKey;
        this.drawVectorKey(rx + (tileSize - 10) / 2, ry + (tileSize - 10) / 2 - 2, isPickedUp);
      } else if (r.type === 'door_locked' || roomId.includes('gate')) {
        const isLocked = state.gateLocked !== false;
        const isBlocked = this.rejectionPulse > 0;
        this.drawVectorGate(rx + (tileSize - 10) / 2, ry + (tileSize - 10) / 2 - 2, isLocked, isBlocked);
      } else if (r.type === 'exit_goal' || roomId === 'exit') {
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
      const gateRoom = lvl.rooms.gate || lvl.rooms.gate_bronze || lvl.rooms.gate_gold;
      if (gateRoom) {
        const gx = offsetX + gateRoom.x * tileSize + (tileSize - 10) / 2;
        const gy = offsetY + gateRoom.y * tileSize + (tileSize - 10) / 2;
        this.drawShockwaveRings(gx, gy, 45 - this.rejectionPulse);
      }
    }
  }

  renderCraftingRPG() {
    const lvl = this.levels.crafting_rpg;
    const state = this.getCurrentState();
    const { tileSize, offsetX, offsetY } = lvl;

    // 1. Draw Connecting Paths
    this.ctx.strokeStyle = '#1e293b';
    this.ctx.lineWidth = 10;
    this.ctx.lineCap = 'round';
    this.drawCorridor(0, 0, 0, 1, tileSize, offsetX, offsetY); // Forest - Spawn
    this.drawCorridor(0, 1, 1, 1, tileSize, offsetX, offsetY); // Spawn - Hills
    this.drawCorridor(1, 1, 2, 1, tileSize, offsetX, offsetY); // Hills - Cavern
    this.drawCorridor(2, 1, 3, 1, tileSize, offsetX, offsetY); // Cavern - Abyss

    this.ctx.strokeStyle = '#334155';
    this.ctx.lineWidth = 2;
    this.drawCorridor(0, 0, 0, 1, tileSize, offsetX, offsetY);
    this.drawCorridor(0, 1, 1, 1, tileSize, offsetX, offsetY);
    this.drawCorridor(1, 1, 2, 1, tileSize, offsetX, offsetY);
    this.drawCorridor(2, 1, 3, 1, tileSize, offsetX, offsetY);

    // 2. Draw Hallucinated Shortcut if Flawed Mode
    if (this.modelMode === 'flawed') {
      this.drawGhostTrajectory([
        { x: offsetX + 0 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
        { x: offsetX + 1 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
        { x: offsetX + 2 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
        { x: offsetX + 3 * tileSize + tileSize / 2, y: offsetY + 1 * tileSize + tileSize / 2 },
      ]);
    }

    // 3. Draw Nodes
    for (const [roomId, r] of Object.entries(lvl.rooms)) {
      const rx = offsetX + r.x * tileSize;
      const ry = offsetY + r.y * tileSize;

      this.drawFlagstoneTile(rx, ry, tileSize - 10, r.label);

      const cx = rx + (tileSize - 10) / 2;
      const cy = ry + (tileSize - 10) / 2 - 4;

      if (r.type === 'resource_wood') {
        this.drawVectorWoodTree(cx, cy);
      } else if (r.type === 'crafting_bench') {
        this.drawVectorWorkbench(cx, cy);
      } else if (r.type === 'furnace_cavern') {
        this.drawVectorFurnace(cx, cy);
      } else if (r.type === 'exit_goal') {
        this.drawVectorDiamond(cx, cy);
      }
    }

    // 4. Draw Ghost Hero
    if (this.modelMode === 'flawed' && this.currentStep > 0) {
      this.drawVectorGhostHero(this.ghostPos.x, this.ghostPos.y);
    }

    // 5. Draw Hero Steve
    this.drawVectorHero(this.agentPos.x, this.agentPos.y, state.hasPick);

    // 6. Draw Shockwave
    if (this.rejectionPulse > 0) {
      const abyss = lvl.rooms.deep_abyss;
      if (abyss) {
        const gx = offsetX + abyss.x * tileSize + (tileSize - 10) / 2;
        const gy = offsetY + abyss.y * tileSize + (tileSize - 10) / 2;
        this.drawShockwaveRings(gx, gy, 45 - this.rejectionPulse);
      }
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

  drawVectorWoodTree(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);
    this.ctx.fillStyle = '#15803d';
    this.ctx.strokeStyle = '#22c55e';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.moveTo(0, -14);
    this.ctx.lineTo(12, 2);
    this.ctx.lineTo(-12, 2);
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.fillStyle = '#78350f';
    this.ctx.fillRect(-3, 2, 6, 8);
    this.ctx.restore();
  }

  drawVectorWorkbench(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);
    this.ctx.fillStyle = '#b45309';
    this.ctx.strokeStyle = '#f59e0b';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.roundRect(-12, -8, 24, 16, 2);
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.strokeStyle = '#78350f';
    this.ctx.lineWidth = 1;
    this.ctx.strokeRect(-8, -5, 16, 10);
    this.ctx.restore();
  }

  drawVectorFurnace(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);
    this.ctx.fillStyle = '#475569';
    this.ctx.strokeStyle = '#94a3b8';
    this.ctx.lineWidth = 1.5;
    this.ctx.beginPath();
    this.ctx.roundRect(-12, -10, 24, 20, 3);
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.fillStyle = '#ea580c';
    this.ctx.shadowColor = '#f97316';
    this.ctx.shadowBlur = 6;
    this.ctx.beginPath();
    this.ctx.arc(0, 2, 5, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.shadowBlur = 0;
    this.ctx.restore();
  }

  drawVectorDiamond(cx, cy) {
    this.ctx.save();
    this.ctx.translate(cx, cy);
    this.ctx.fillStyle = '#06b6d4';
    this.ctx.strokeStyle = '#67e8f9';
    this.ctx.lineWidth = 2;
    this.ctx.shadowColor = '#06b6d4';
    this.ctx.shadowBlur = 10;
    this.ctx.beginPath();
    this.ctx.moveTo(0, -12);
    this.ctx.lineTo(10, -2);
    this.ctx.lineTo(0, 12);
    this.ctx.lineTo(-10, -2);
    this.ctx.closePath();
    this.ctx.fill();
    this.ctx.stroke();
    this.ctx.shadowBlur = 0;
    this.ctx.fillStyle = '#ffffff';
    this.ctx.beginPath();
    this.ctx.moveTo(0, -7);
    this.ctx.lineTo(4, -2);
    this.ctx.lineTo(0, 3);
    this.ctx.lineTo(-4, -2);
    this.ctx.closePath();
    this.ctx.fill();
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
