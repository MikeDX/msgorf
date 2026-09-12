/*!
 * GUESS: video-derived Ms. Gorf sketch — not XC.LOGIC / not compiled game.
 * Disk patterns from play/assets.js; font + bullets + motion estimated from footage.
 *
 * Playfield: 320×204 — Astrocade commercial hi-res (landscape). Footage is horizontal.
 * See docs/findings/display.md (Ms. Gorf late board still unproven; Gorf cabinet was portrait).
 */
(function () {
  // Landscape Astrocade hi-res (gameplay video is horizontal)
  const W = 320;
  const H = 204;
  const SCALE = 3;

  const canvas = document.getElementById("c");
  const ctx = canvas.getContext("2d");
  canvas.width = W * SCALE;
  canvas.height = H * SCALE;
  ctx.imageSmoothingEnabled = false;

  const assets = window.MSGORF_ASSETS;
  if (!assets) {
    document.body.insertAdjacentHTML(
      "beforeend",
      "<p class='err'>Missing play/assets.js — run <code>python3 tools/export_play_assets.py</code></p>"
    );
    return;
  }

  const FONT = window.MSGORF_FONT_GUESS;
  const YELLOW = FONT?.color || [240, 200, 32];

  /** @type {Record<string, HTMLCanvasElement>} */
  const sprites = {};

  function patternToCanvas(p) {
    const c = document.createElement("canvas");
    c.width = p.w;
    c.height = p.h;
    const g = c.getContext("2d");
    const img = g.createImageData(p.w, p.h);
    const pal = p.palette_rgb || assets.palette_rgb;
    for (let y = 0; y < p.h; y++) {
      const row = p.rows[y];
      for (let x = 0; x < p.w; x++) {
        const d = Number(row[x] || "0");
        const [r, gv, b] = pal[d];
        const i = (y * p.w + x) * 4;
        img.data[i] = r;
        img.data[i + 1] = gv;
        img.data[i + 2] = b;
        img.data[i + 3] = d === 0 ? 0 : 255;
      }
    }
    g.putImageData(img, 0, 0);
    return c;
  }

  for (const [name, p] of Object.entries(assets.patterns)) {
    if (p.rows) sprites[name] = patternToCanvas(p);
  }

  // CLONE cycle from footage: 1 → 2 → 3 → 2(hflip)
  const CLONE_CYCLE = [
    { name: "CLN0", flip: false },
    { name: "CLN32", flip: false },
    { name: "CLN64", flip: false },
    { name: "CLN32", flip: true },
  ];

  const keys = Object.create(null);
  addEventListener("keydown", (e) => {
    keys[e.key.toLowerCase()] = true;
    if ([" ", "arrowup", "arrowdown", "arrowleft", "arrowright"].includes(e.key.toLowerCase()))
      e.preventDefault();
  });
  addEventListener("keyup", (e) => {
    keys[e.key.toLowerCase()] = false;
  });

  const mouse = { x: W / 2, y: H / 2, down: false };
  canvas.addEventListener("mousemove", (e) => {
    const r = canvas.getBoundingClientRect();
    mouse.x = ((e.clientX - r.left) / r.width) * W;
    mouse.y = ((e.clientY - r.top) / r.height) * H;
  });
  canvas.addEventListener("mousedown", () => {
    mouse.down = true;
  });
  canvas.addEventListener("mouseup", () => {
    mouse.down = false;
  });

  function drawGlyph(ch, x, y, px) {
    const g = FONT?.glyphs?.[ch];
    if (!g) return;
    const [cw, chh] = FONT.cell;
    const [r, gv, b] = YELLOW;
    for (let row = 0; row < chh; row++) {
      const bits = g[row] || "";
      for (let col = 0; col < cw; col++) {
        if (bits[col] === "1") {
          ctx.fillStyle = `rgb(${r},${gv},${b})`;
          ctx.fillRect(x + col * px, y + row * px, px, px);
        }
      }
    }
  }

  function drawText(str, x, y, px = 1) {
    const [cw] = FONT.cell;
    let cx = x;
    for (const ch of str) {
      drawGlyph(ch, cx, y, px);
      cx += (cw + 1) * px;
    }
    return cx;
  }

  function blit(name, x, y, opts) {
    const s = sprites[name];
    if (!s) return;
    const flip = opts && opts.flip;
    ctx.save();
    ctx.translate(x, y);
    if (flip) ctx.scale(-1, 1);
    // Ship / most sprites: never rotate — always “up” as stored on disk
    ctx.drawImage(s, -s.width / 2, -s.height / 2);
    ctx.restore();
  }

  // --- game state (GUESS rules) ---
  let mode = "select"; // select | intro | play | dead
  let score = 0;
  let shipsLeft = 3; // SBi / SBASE count
  let t = 0;
  let fireCd = 0;
  let spawnCd = 0;
  const player = { x: W * 0.35, y: H * 0.55, visible: false };
  /** @type {{x:number,y:number,vx:number,vy:number,life:number}[]} */
  let bullets = [];
  /** @type {{x:number,y:number,vx:number,vy:number,kind:string,hp:number,r:number}[]} */
  let foes = [];
  /** @type {{x:number,y:number,kind:string,hp:number}[]} */
  let fx = [];
  let clone = { x: W * 0.62, y: H * 0.42, frame: 0, visible: false };

  /** Level-start galaxy: 15 perimeter shells × 16 yellow stars. Intro only. */
  const galaxy = {
    phase: "in", // in | bang | out | done
    age: 0,
    /** How many shells are currently drawn (0..15). In: grow; out: shrink from outside. */
    shellsShown: 0,
    /** During out: how many outer shells have been peeled away. */
    shellsPeeled: 0,
  };
  const GALAXY_CX = W * 0.5;
  const GALAXY_CY = H * 0.52;
  const GALAXY_ARMS = 16;
  const GALAXY_SHELLS = 15;
  const GALAXY_R1 = 5; // innermost shell
  const GALAXY_SHELL_GAP = 3.5; // pixels between perimeter shells
  const GALAXY_R0 = GALAXY_R1 + (GALAXY_SHELLS - 1) * GALAXY_SHELL_GAP; // ~54 — compact near centre
  /** Clockwise-on-screen twist per shell (canvas Y-down; negative = CCW on CRT). */
  const GALAXY_SHELL_TWIST = -((Math.PI * 2) / GALAXY_ARMS / 3); // ~−7.5°
  const GALAXY_SHELL_DT = 0.075; // seconds per shell appear/remove
  const GALAXY_BANG_DUR = 0.55;

  const GORF_R = 7;
  const GORF_SPEED = 38;

  function randVel() {
    const a = Math.random() * Math.PI * 2;
    const s = GORF_SPEED * (0.75 + Math.random() * 0.5);
    return { vx: Math.cos(a) * s, vy: Math.sin(a) * s };
  }

  function spawnGorf(x, y) {
    const v = randVel();
    foes.push({
      x: x ?? W * 0.5 + (Math.random() - 0.5) * 80,
      y: y ?? H * 0.35 + (Math.random() - 0.5) * 60,
      vx: v.vx,
      vy: v.vy,
      kind: "GORF-PAT",
      hp: 1,
      r: GORF_R,
    });
  }

  function beginPlayfield() {
    player.visible = true;
    player.x = W * 0.28;
    player.y = H * 0.55;
    clone.visible = true;
    clone.x = W * 0.62;
    clone.y = H * 0.45;
    clone.frame = 0;
    spawnCd = 1.5;
    foes = [];
    for (let i = 0; i < 4; i++) spawnGorf();
    mode = "play";
  }

  function resetPlay() {
    score = 0;
    shipsLeft = 3;
    bullets = [];
    foes = [];
    fx = [];
    player.visible = false;
    clone.visible = false;
    galaxy.phase = "in";
    galaxy.age = 0;
    galaxy.shellsShown = 0;
    galaxy.shellsPeeled = 0;
    mode = "intro";
  }

  function spawnBurst(x, y) {
    fx.push({ x, y, kind: "_BANG", hp: 0.45 });
  }

  addEventListener("keydown", (e) => {
    if (mode === "select") {
      if (e.key === "1" || e.key === "2") resetPlay();
    } else if (mode === "dead" && (e.key === "Enter" || e.key === "1")) {
      mode = "select";
    }
  });

  function shellRadius(shellIndex) {
    // shell 0 = outermost, shell 14 = innermost; fixed ~3.5px gaps
    return GALAXY_R0 - shellIndex * GALAXY_SHELL_GAP;
  }

  /**
   * Draw discrete perimeter shells.
   * firstShell..lastShell inclusive; 0 = outer.
   */
  function drawGalaxyShells(firstShell, lastShell) {
    const [yr, yg, yb] = YELLOW;
    ctx.fillStyle = `rgb(${yr},${yg},${yb})`;
    for (let s = firstShell; s <= lastShell; s++) {
      if (s < 0 || s >= GALAXY_SHELLS) continue;
      const r = shellRadius(s);
      // each closer shell is rotated slightly anti-clockwise vs the previous
      const rot = s * GALAXY_SHELL_TWIST;
      for (let arm = 0; arm < GALAXY_ARMS; arm++) {
        const a = rot + (arm / GALAXY_ARMS) * Math.PI * 2;
        const x = GALAXY_CX + Math.cos(a) * r;
        const y = GALAXY_CY + Math.sin(a) * r;
        ctx.fillRect(x | 0, y | 0, 1, 1);
      }
    }
  }

  /**
   * Intro: shells appear outer→inner (15×16), bang at centre, then peel
   * outer→inner one perimeter at a time. GUESS from footage.
   */
  function drawGalaxy() {
    if (galaxy.phase === "done") return;

    let first = 0;
    let last = -1;
    if (galaxy.phase === "in") {
      // shellsShown = how many complete shells (1..15)
      last = galaxy.shellsShown - 1;
    } else if (galaxy.phase === "bang") {
      first = 0;
      last = GALAXY_SHELLS - 1;
    } else if (galaxy.phase === "out") {
      // peel outer shells: start drawing after shellsPeeled
      first = galaxy.shellsPeeled;
      last = GALAXY_SHELLS - 1;
    }

    if (last >= first) drawGalaxyShells(first, last);

    if (galaxy.phase === "bang") {
      const bangName = galaxy.age < GALAXY_BANG_DUR * 0.5 ? "FBEXP5" : "FBEXP6";
      blit(bangName, GALAXY_CX, GALAXY_CY);
    }
  }

  function updateIntro(dt) {
    t += dt;
    galaxy.age += dt;

    if (galaxy.phase === "in") {
      const want = Math.min(
        GALAXY_SHELLS,
        1 + Math.floor(galaxy.age / GALAXY_SHELL_DT)
      );
      galaxy.shellsShown = want;
      if (galaxy.shellsShown >= GALAXY_SHELLS && galaxy.age >= GALAXY_SHELLS * GALAXY_SHELL_DT) {
        galaxy.phase = "bang";
        galaxy.age = 0;
      }
    } else if (galaxy.phase === "bang") {
      if (galaxy.age >= GALAXY_BANG_DUR) {
        galaxy.phase = "out";
        galaxy.age = 0;
        galaxy.shellsPeeled = 0;
      }
    } else if (galaxy.phase === "out") {
      galaxy.shellsPeeled = Math.min(
        GALAXY_SHELLS,
        Math.floor(galaxy.age / GALAXY_SHELL_DT)
      );
      if (galaxy.shellsPeeled >= GALAXY_SHELLS) {
        galaxy.phase = "done";
        beginPlayfield();
      }
    }
  }

  function drawSelect() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    drawText("$8000", 8, 8, 1);
    // boxed 1 / 2 stand-ins on select (video); in-play uses P1Ui pattern
    const [cw, chh] = FONT.cell;
    ctx.strokeStyle = `rgb(${YELLOW[0]},${YELLOW[1]},${YELLOW[2]})`;
    ctx.strokeRect(8 + 6 * 6, 6, cw + 4, chh + 4);
    drawGlyph("1", 8 + 6 * 6 + 2, 8, 1);
    ctx.strokeRect(W - 8 - 6 * 6 - cw - 4, 6, cw + 4, chh + 4);
    drawGlyph("2", W - 8 - 6 * 6 - cw - 2, 8, 1);
    drawText("$4500", W - 8 - 5 * 6, 8, 1);
    const msg1 = "SELECT 1 OR 2";
    const msg2 = "PLAYER GAME";
    const px = 2;
    const w1 = msg1.length * (cw + 1) * px;
    const w2 = msg2.length * (cw + 1) * px;
    drawText(msg1, (W - w1) / 2, H * 0.4, px);
    drawText(msg2, (W - w2) / 2, H * 0.4 + 22, px);
    ctx.fillStyle = "#666";
    ctx.font = "10px monospace";
    ctx.fillText("GUESS — 1 / 2 to start", 8, H - 8);
  }

  function bounceWalls(e) {
    const margin = 4;
    const top = 22; // below HUD
    if (e.x - e.r < margin) {
      e.x = margin + e.r;
      e.vx = Math.abs(e.vx);
    } else if (e.x + e.r > W - margin) {
      e.x = W - margin - e.r;
      e.vx = -Math.abs(e.vx);
    }
    if (e.y - e.r < top) {
      e.y = top + e.r;
      e.vy = Math.abs(e.vy);
    } else if (e.y + e.r > H - margin) {
      e.y = H - margin - e.r;
      e.vy = -Math.abs(e.vy);
    }
  }

  function bouncePair(a, b) {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.hypot(dx, dy) || 1;
    const minD = a.r + b.r;
    if (dist >= minD) return;
    // separate
    const overlap = (minD - dist) / 2;
    const nx = dx / dist;
    const ny = dy / dist;
    a.x -= nx * overlap;
    a.y -= ny * overlap;
    b.x += nx * overlap;
    b.y += ny * overlap;
    // elastic swap along normal
    const avn = a.vx * nx + a.vy * ny;
    const bvn = b.vx * nx + b.vy * ny;
    a.vx += (bvn - avn) * nx;
    a.vy += (bvn - avn) * ny;
    b.vx += (avn - bvn) * nx;
    b.vy += (avn - bvn) * ny;
  }

  function updatePlay(dt) {
    t += dt;
    if (!player.visible) return;

    const speed = 70;
    let dx = 0,
      dy = 0;
    if (keys["a"] || keys["arrowleft"]) dx -= 1;
    if (keys["d"] || keys["arrowright"]) dx += 1;
    if (keys["w"] || keys["arrowup"]) dy -= 1;
    if (keys["s"] || keys["arrowdown"]) dy += 1;
    if (dx || dy) {
      const n = Math.hypot(dx, dy) || 1;
      player.x += (dx / n) * speed * dt;
      player.y += (dy / n) * speed * dt;
    }
    player.x = Math.max(12, Math.min(W - 12, player.x));
    player.y = Math.max(28, Math.min(H - 12, player.y));

    // Aim stick (mouse) — ship art stays upright
    const aim = Math.atan2(mouse.y - player.y, mouse.x - player.x);

    fireCd -= dt;
    if ((mouse.down || keys[" "] || keys["k"]) && fireCd <= 0) {
      fireCd = 0.12;
      const sp = 160;
      bullets.push({
        x: player.x,
        y: player.y,
        vx: Math.cos(aim) * sp,
        vy: Math.sin(aim) * sp,
        life: 0.9,
      });
    }

    bullets = bullets.filter((b) => {
      b.x += b.vx * dt;
      b.y += b.vy * dt;
      b.life -= dt;
      return b.life > 0 && b.x > -10 && b.x < W + 10 && b.y > -10 && b.y < H + 10;
    });

    // Clone machine: animate + drift; not destroyable; spawns gorfs
    if (clone.visible) {
      clone.frame = (clone.frame + dt * 2.4) % CLONE_CYCLE.length;
      clone.x += Math.sin(t * 0.55) * 10 * dt;
      clone.y += Math.cos(t * 0.4) * 8 * dt;
      clone.x = Math.max(40, Math.min(W - 40, clone.x));
      clone.y = Math.max(50, Math.min(H - 50, clone.y));

      spawnCd -= dt;
      if (spawnCd <= 0) {
        spawnCd = 2.2 + Math.random() * 1.5;
        spawnGorf(clone.x + (Math.random() - 0.5) * 20, clone.y + (Math.random() - 0.5) * 20);
      }
    }

    for (const f of foes) {
      f.x += f.vx * dt;
      f.y += f.vy * dt;
      bounceWalls(f);
    }
    for (let i = 0; i < foes.length; i++) {
      for (let j = i + 1; j < foes.length; j++) bouncePair(foes[i], foes[j]);
    }

    for (const b of bullets) {
      for (const f of foes) {
        if (f.hp <= 0) continue;
        if (Math.hypot(b.x - f.x, b.y - f.y) < f.r + 3) {
          f.hp = 0;
          b.life = 0;
          score += 1000;
          spawnBurst(f.x, f.y);
        }
      }
    }
    foes = foes.filter((f) => f.hp > 0);

    for (const e of fx) e.hp -= dt;
    fx = fx.filter((e) => e.hp > 0);

    for (const f of foes) {
      if (Math.hypot(f.x - player.x, f.y - player.y) < f.r + 8) {
        shipsLeft -= 1;
        spawnBurst(player.x, player.y);
        player.x = W * 0.3;
        player.y = H * 0.55;
        if (shipsLeft <= 0) mode = "dead";
        break;
      }
    }
  }

  function drawHud() {
    let x = 4;
    x = drawText("$" + String(score), x, 4, 1);
    x += 4;
    if (Math.floor(t * 4) % 2 === 0) {
      blit("P1UP", x + 4, 10);
    }
    x += 12;
    for (let i = 0; i < shipsLeft; i++) {
      blit("SBASE", x + 6 + i * 10, 10);
    }
  }

  function drawIntro() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    drawGalaxy();
    drawHud();
  }

  function drawPlay() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    // no galaxy during play — intro-only

    if (clone.visible) {
      const ci = Math.floor(clone.frame) % CLONE_CYCLE.length;
      const cf = CLONE_CYCLE[ci];
      blit(cf.name, clone.x, clone.y, { flip: cf.flip });
    }

    for (const f of foes) blit(f.kind, f.x, f.y);
    for (const e of fx) blit(e.hp > 0.22 ? "FBEXP5" : "FBEXP6", e.x, e.y);

    if (player.visible) blit("PLY1-P", player.x, player.y);

    ctx.strokeStyle = "rgb(240,220,180)";
    ctx.lineWidth = 1;
    for (const b of bullets) {
      const len = 5;
      const ang = Math.atan2(b.vy, b.vx);
      ctx.beginPath();
      ctx.moveTo(b.x - Math.cos(ang) * len, b.y - Math.sin(ang) * len);
      ctx.lineTo(b.x + Math.cos(ang) * len, b.y + Math.sin(ang) * len);
      ctx.stroke();
    }

    drawHud();
  }

  function drawDead() {
    drawPlay();
    ctx.fillStyle = "rgba(0,0,0,0.55)";
    ctx.fillRect(0, 0, W, H);
    drawText("GAME OVER", W / 2 - 40, H / 2 - 8, 2);
    ctx.fillStyle = "#aaa";
    ctx.font = "10px monospace";
    ctx.fillText("Enter / 1 — select", W / 2 - 48, H / 2 + 20);
  }

  let last = performance.now();
  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    ctx.setTransform(SCALE, 0, 0, SCALE, 0, 0);
    if (mode === "select") drawSelect();
    else if (mode === "intro") {
      updateIntro(dt);
      drawIntro();
    } else if (mode === "play") {
      updatePlay(dt);
      drawPlay();
    } else drawDead();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
