"""
Generate crisp, publication-grade SVG assets for Game AI visualizer:
- UI Icons (Linear/Vercel style, 24x24 viewBox, stroke-width=2, stroke-linecap=round)
- Game Sprites (Hero, Ghost Hero, Key, Gate Locked/Unlocked, Hazard Pit, Exit Portal, Sokoban Box, Sokoban Target)
"""
import os

ICONS_DIR = "ui_ux/assets/icons"
SPRITES_DIR = "ui_ux/assets/sprites"
os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(SPRITES_DIR, exist_ok=True)

icons = {
    "play.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>''',
    "pause.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>''',
    "step.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 4 15 12 5 20 5 4" fill="currentColor"/><line x1="19" y1="5" x2="19" y2="19"/></svg>''',
    "reset.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>''',
    "shield.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>''',
    "shield-check.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>''',
    "warning.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>''',
    "terminal.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>''',
    "cpu.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>''',
    "gamepad.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/><line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/><rect x="2" y="6" width="20" height="12" rx="6"/></svg>''',
    "activity.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>''',
    "crosshair.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>''',
    "radar.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/><line x1="12" y1="12" x2="19" y2="5"/></svg>''',
    "key.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/></svg>''',
    "lock.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>''',
    "unlock.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></svg>''',
    "portal.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 9 9"/><path d="M12 7a5 5 0 0 1 5 5"/><circle cx="12" cy="12" r="2" fill="currentColor"/></svg>''',
}

for name, content in icons.items():
    with open(os.path.join(ICONS_DIR, name), "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(icons)} icons in {ICONS_DIR}")

# Sprites & Tiles
TILES_DIR = "ui_ux/assets/tiles"
os.makedirs(TILES_DIR, exist_ok=True)

sprites = {
    "hero.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Outer Aura -->
  <circle cx="32" cy="32" r="28" fill="#3b82f6" fill-opacity="0.15" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="3 3"/>
  <!-- Main Chassis -->
  <circle cx="32" cy="32" r="20" fill="#1e293b" stroke="#60a5fa" stroke-width="2.5"/>
  <!-- Visor / Sensor Core -->
  <rect x="22" y="24" width="20" height="10" rx="5" fill="#38bdf8"/>
  <circle cx="32" cy="29" r="2" fill="#ffffff"/>
  <!-- Directional Indicator Arrow -->
  <path d="M32 14 L36 20 L28 20 Z" fill="#60a5fa"/>
  <!-- Power Core Indicator -->
  <circle cx="32" cy="42" r="3" fill="#10b981"/>
</svg>''',

    "ghost_hero.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Phantom Glitch Aura -->
  <circle cx="32" cy="32" r="28" fill="#f43f5e" fill-opacity="0.12" stroke="#f43f5e" stroke-width="1.5" stroke-dasharray="4 4"/>
  <!-- Ghost Body (Translucent) -->
  <circle cx="32" cy="32" r="20" fill="#881337" fill-opacity="0.4" stroke="#fb7185" stroke-width="2" stroke-dasharray="6 2"/>
  <!-- Flawed Visor -->
  <rect x="22" y="24" width="20" height="10" rx="5" fill="#f43f5e" fill-opacity="0.6"/>
  <!-- Glitch Marker (Question Mark / Broken Wire) -->
  <path d="M30 38 Q32 35 34 38 Q36 41 32 44" stroke="#fda4af" stroke-width="2" stroke-linecap="round"/>
</svg>''',

    "key.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Golden Radiance Glow -->
  <circle cx="24" cy="40" r="18" fill="#fbbf24" fill-opacity="0.15"/>
  <!-- Key Bow (Ring) -->
  <circle cx="24" cy="40" r="12" stroke="#f59e0b" stroke-width="4" fill="#78350f" fill-opacity="0.4"/>
  <circle cx="24" cy="40" r="5" stroke="#fde68a" stroke-width="2"/>
  <!-- Key Blade (Shaft) -->
  <path d="M33 31 L54 10" stroke="#f59e0b" stroke-width="4" stroke-linecap="round"/>
  <!-- Key Teeth / Bit -->
  <path d="M47 17 L52 22 M52 12 L56 16" stroke="#fde68a" stroke-width="3.5" stroke-linecap="round"/>
  <!-- Highlight Glint -->
  <polygon points="24,24 26,20 28,24 24,24" fill="#ffffff"/>
</svg>''',

    "gate_locked.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Stone Gate Arch -->
  <rect x="6" y="6" width="52" height="52" rx="6" fill="#0f172a" stroke="#475569" stroke-width="3"/>
  <!-- Heavy Iron Portcullis Bars -->
  <line x1="16" y1="10" x2="16" y2="54" stroke="#64748b" stroke-width="3"/>
  <line x1="26" y1="10" x2="26" y2="54" stroke="#64748b" stroke-width="3"/>
  <line x1="38" y1="10" x2="38" y2="54" stroke="#64748b" stroke-width="3"/>
  <line x1="48" y1="10" x2="48" y2="54" stroke="#64748b" stroke-width="3"/>
  <line x1="10" y1="22" x2="54" y2="22" stroke="#64748b" stroke-width="2.5"/>
  <line x1="10" y1="40" x2="54" y2="40" stroke="#64748b" stroke-width="2.5"/>
  <!-- Red Energy Field / Lock Rune -->
  <circle cx="32" cy="32" r="14" fill="#881337" fill-opacity="0.8" stroke="#f43f5e" stroke-width="2.5"/>
  <rect x="26" y="29" width="12" height="9" rx="2" fill="#fecdd3"/>
  <path d="M28 29 V25 A4 4 0 0 1 36 25 V29" stroke="#fecdd3" stroke-width="2" fill="none"/>
</svg>''',

    "gate_open.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Open Archway -->
  <rect x="6" y="6" width="52" height="52" rx="6" fill="#064e3b" fill-opacity="0.3" stroke="#10b981" stroke-width="3"/>
  <!-- Raised Portcullis -->
  <rect x="12" y="8" width="40" height="14" fill="#334155" stroke="#64748b" stroke-width="2"/>
  <line x1="18" y1="8" x2="18" y2="22" stroke="#94a3b8" stroke-width="2"/>
  <line x1="27" y1="8" x2="27" y2="22" stroke="#94a3b8" stroke-width="2"/>
  <line x1="37" y1="8" x2="37" y2="22" stroke="#94a3b8" stroke-width="2"/>
  <line x1="46" y1="8" x2="46" y2="22" stroke="#94a3b8" stroke-width="2"/>
  <!-- Green Passage Aura -->
  <circle cx="32" cy="38" r="10" fill="#10b981" fill-opacity="0.3"/>
  <polyline points="26 38 32 32 38 38" stroke="#6ee7b7" stroke-width="2.5" stroke-linecap="round"/>
</svg>''',

    "portal.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Outer Cosmic Vortex -->
  <circle cx="32" cy="32" r="26" stroke="#8b5cf6" stroke-width="2.5" stroke-dasharray="6 3"/>
  <circle cx="32" cy="32" r="20" stroke="#a78bfa" stroke-width="2" stroke-dasharray="4 2"/>
  <!-- Core Horizon -->
  <circle cx="32" cy="32" r="14" fill="#4c1d95" stroke="#c4b5fd" stroke-width="3"/>
  <!-- Spiral Arms -->
  <path d="M32 18 C39 20 42 27 38 34 C34 40 26 39 24 33" stroke="#ddd6fe" stroke-width="2" stroke-linecap="round"/>
  <!-- Center Singularity -->
  <circle cx="32" cy="32" r="4" fill="#ffffff"/>
</svg>''',

    "hazard_pit.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Abyss Pit Base -->
  <rect x="6" y="6" width="52" height="52" rx="6" fill="#09090b" stroke="#ef4444" stroke-width="2" stroke-dasharray="6 3"/>
  <!-- Warning Stripes along edge -->
  <polygon points="6,6 16,6 6,16" fill="#ef4444" fill-opacity="0.4"/>
  <polygon points="58,58 48,58 58,48" fill="#ef4444" fill-opacity="0.4"/>
  <polygon points="6,58 6,48 16,58" fill="#ef4444" fill-opacity="0.4"/>
  <polygon points="58,6 58,16 48,6" fill="#ef4444" fill-opacity="0.4"/>
  <!-- Pit Spikes Depth -->
  <polygon points="18,48 24,24 30,48" fill="#18181b" stroke="#71717a" stroke-width="1.5"/>
  <polygon points="28,48 34,18 40,48" fill="#18181b" stroke="#71717a" stroke-width="1.5"/>
  <polygon points="38,48 44,26 50,48" fill="#18181b" stroke="#71717a" stroke-width="1.5"/>
</svg>''',

    "sokoban_box.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Heavy Wooden / Metallic Crate -->
  <rect x="8" y="8" width="48" height="48" rx="4" fill="#78350f" stroke="#b45309" stroke-width="3"/>
  <!-- Reinforcement Cross Planks -->
  <line x1="8" y1="8" x2="56" y2="56" stroke="#92400e" stroke-width="3"/>
  <line x1="56" y1="8" x2="8" y2="56" stroke="#92400e" stroke-width="3"/>
  <!-- Inner Border & Corner Brackets -->
  <rect x="12" y="12" width="40" height="40" stroke="#d97706" stroke-width="1.5"/>
  <!-- Metal Rivets -->
  <circle cx="12" cy="12" r="2.5" fill="#fcd34d"/>
  <circle cx="52" cy="12" r="2.5" fill="#fcd34d"/>
  <circle cx="12" cy="52" r="2.5" fill="#fcd34d"/>
  <circle cx="52" cy="52" r="2.5" fill="#fcd34d"/>
</svg>''',

    "sokoban_target.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <!-- Target Pad Floor Recess -->
  <rect x="8" y="8" width="48" height="48" rx="6" fill="#064e3b" fill-opacity="0.3" stroke="#059669" stroke-width="2"/>
  <!-- Concentric Target Reticle -->
  <circle cx="32" cy="32" r="16" stroke="#10b981" stroke-width="2" stroke-dasharray="4 2"/>
  <circle cx="32" cy="32" r="8" fill="#059669" stroke="#34d399" stroke-width="2"/>
  <circle cx="32" cy="32" r="3" fill="#ffffff"/>
</svg>''',
}

for name, content in sprites.items():
    with open(os.path.join(SPRITES_DIR, name), "w", encoding="utf-8") as f:
        f.write(content)

tiles = {
    "flagstone.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" fill="#0f172a"/>
  <!-- Stone Tile 1 -->
  <rect x="2" y="2" width="28" height="28" rx="2" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <!-- Stone Tile 2 -->
  <rect x="34" y="2" width="28" height="28" rx="2" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <!-- Stone Tile 3 -->
  <rect x="2" y="34" width="28" height="28" rx="2" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <!-- Stone Tile 4 -->
  <rect x="34" y="34" width="28" height="28" rx="2" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <!-- Subtle Floor Mortar -->
  <path d="M0 32 H64 M32 0 V64" stroke="#090d16" stroke-width="2"/>
</svg>''',

    "wall_brick.svg": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" fill="#090d16"/>
  <!-- Masonry Brick Layout -->
  <rect x="2" y="2" width="60" height="18" rx="2" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
  <rect x="2" y="23" width="28" height="18" rx="2" fill="#334155" stroke="#475569" stroke-width="1.5"/>
  <rect x="34" y="23" width="28" height="18" rx="2" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
  <rect x="2" y="44" width="60" height="18" rx="2" fill="#1e293b" stroke="#475569" stroke-width="1.5"/>
</svg>''',
}

for name, content in tiles.items():
    with open(os.path.join(TILES_DIR, name), "w", encoding="utf-8") as f:
        f.write(content)

print(f"Generated {len(sprites)} sprites in {SPRITES_DIR} and {len(tiles)} tiles in {TILES_DIR}")
