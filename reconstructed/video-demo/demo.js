/*!
 * GUESS: video-derived Ms. Gorf sketch — not XC.LOGIC / not compiled game.
 * Disk patterns from play/assets.js; font + bullets + motion estimated from footage.
 */
(function () {
  const W = 320;
  const H = 240; // lab playfield (portrait cabinet was taller; landscape for remake readability)
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

  function drawText(str, x, y, px = 2) {
    const [cw] = FONT.cell;
    let cx = x;
    for (const ch of str) {
      drawGlyph(ch, cx, y, px);
      cx += (cw + 1) * px;
    }
  }

  function drawBoxedDigit(d, x, y, px = 2) {
    const [r, gv, b] = YELLOW;
    ctx.strokeStyle = `rgb(${r},${gv},${b})`;
    ctx.lineWidth = px;
    const [cw, chh] = FONT.cell;
    const bw = (cw + 2) * px;
    const bh = (chh + 2) * px;
    ctx.strokeRect(x + 0.5, y + 0.5, bw, bh);
    drawGlyph(String(d), x + px, y + px, px);
  }

  function drawLifeDiamond(x, y, s = 3) {
    ctx.fillStyle = "rgb(180,60,160)";
    ctx.beginPath();
    ctx.moveTo(x, y - s);
    ctx.lineTo(x + s, y);
    ctx.lineTo(x, y + s);
    ctx.lineTo(x - s, y);
    ctx.closePath();
    ctx.fill();
  }

  function blit(name, x, y, ang) {
    const s = sprites[name];
    if (!s) return;
    ctx.save();
    ctx.translate(x, y);
    if (ang) ctx.rotate(ang);
    ctx.drawImage(s, -s.width / 2, -s.height / 2);
    ctx.restore();
  }

  // --- game state (GUESS rules) ---
  let mode = "select"; // select | play | dead
  let score = 0;
  let lives = 3;
  let t = 0;
  let fireCd = 0;
  const player = { x: W * 0.35, y: H * 0.55, vx: 0, vy: 0 };
  /** @type {{x:number,y:number,vx:number,vy:number,life:number}[]} */
  let bullets = [];
  /** @type {{x:number,y:number,kind:string,phase:number,hp:number}[]} */
  let foes = [];
  let clone = { x: W * 0.65, y: H * 0.4, frame: 0, alive: true };
  let spiral = true;

  function resetPlay() {
    score = 0;
    lives = 3;
    player.x = W * 0.35;
    player.y = H * 0.55;
    bullets = [];
    foes = [];
    clone = { x: W * 0.62, y: H * 0.42, frame: 0, alive: true };
    for (let i = 0; i < 6; i++) {
      foes.push({
        x: W * 0.55 + Math.random() * W * 0.35,
        y: 30 + Math.random() * (H - 60),
        kind: "GORF-PAT",
        phase: Math.random() * Math.PI * 2,
        hp: 1,
      });
    }
    mode = "play";
  }

  function spawnBurst(x, y) {
    // visual only — FBEXP flash
    foes.push({ x, y, kind: "_BANG", phase: 0, hp: 8 });
  }

  addEventListener("keydown", (e) => {
    if (mode === "select") {
      if (e.key === "1" || e.key === "2") resetPlay();
    } else if (mode === "dead" && (e.key === "Enter" || e.key === "1")) {
      mode = "select";
    }
  });

  function drawSpiral(cx, cy) {
    ctx.fillStyle = "rgb(48,200,80)";
    for (let i = 0; i < 90; i++) {
      const a = i * 0.35 + t * 0.02;
      const r = 8 + i * 0.9;
      const x = cx + Math.cos(a) * r;
      const y = cy + Math.sin(a) * r * 0.85;
      ctx.fillRect(x, y, 1, 1);
    }
  }

  function drawSelect() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    drawText("$8000", 12, 10, 2);
    drawBoxedDigit(1, 68, 8, 2);
    drawBoxedDigit(2, W - 100, 8, 2);
    drawText("$4500", W - 72, 10, 2);
    const msg1 = "SELECT 1 OR 2";
    const msg2 = "PLAYER GAME";
    const [cw] = FONT.cell;
    const px = 3;
    const w1 = msg1.length * (cw + 1) * px;
    const w2 = msg2.length * (cw + 1) * px;
    drawText(msg1, (W - w1) / 2, H * 0.38, px);
    drawText(msg2, (W - w2) / 2, H * 0.38 + 28, px);
    ctx.fillStyle = "#666";
    ctx.font = "10px monospace";
    ctx.fillText("GUESS remake — press 1 or 2", 8, H - 10);
  }

  function updatePlay(dt) {
    t += dt;
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
    player.y = Math.max(20, Math.min(H - 12, player.y));

    const aimX = mouse.x - player.x;
    const aimY = mouse.y - player.y;
    const aim = Math.atan2(aimY, aimX);

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

    if (clone.alive) {
      clone.frame = (clone.frame + dt * 2.2) % 3;
      clone.x += Math.sin(t * 0.7) * 12 * dt;
      clone.y += Math.cos(t * 0.5) * 10 * dt;
    }

    for (const f of foes) {
      if (f.kind === "_BANG") {
        f.hp -= dt * 8;
        continue;
      }
      f.phase += dt;
      f.x += Math.sin(f.phase) * 18 * dt;
      f.y += Math.cos(f.phase * 0.8) * 14 * dt;
      f.x = Math.max(10, Math.min(W - 10, f.x));
      f.y = Math.max(24, Math.min(H - 10, f.y));
    }

    // collisions (AABB GUESS)
    for (const b of bullets) {
      for (const f of foes) {
        if (f.kind === "_BANG" || f.hp <= 0) continue;
        if (Math.hypot(b.x - f.x, b.y - f.y) < 10) {
          f.hp = 0;
          b.life = 0;
          score += 500;
          spawnBurst(f.x, f.y);
        }
      }
      if (clone.alive && Math.hypot(b.x - clone.x, b.y - clone.y) < 18) {
        b.life = 0;
        clone.alive = false;
        score += 2000;
        spawnBurst(clone.x, clone.y);
      }
    }
    foes = foes.filter((f) => f.hp > 0);
    if (foes.filter((f) => f.kind === "GORF-PAT").length < 4) {
      foes.push({
        x: W * 0.7 + Math.random() * 40,
        y: 40 + Math.random() * (H - 80),
        kind: "GORF-PAT",
        phase: Math.random() * 6,
        hp: 1,
      });
    }

    // touch damage
    for (const f of foes) {
      if (f.kind === "_BANG") continue;
      if (Math.hypot(f.x - player.x, f.y - player.y) < 12) {
        lives -= 1;
        player.x = W * 0.3;
        player.y = H * 0.55;
        if (lives <= 0) mode = "dead";
        break;
      }
    }
  }

  function drawPlay() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    if (spiral) drawSpiral(W * 0.55, H * 0.45);

    drawText("$" + String(score), 6, 4, 2);
    drawBoxedDigit(1, 6 + (String(score).length + 2) * 12, 2, 2);
    for (let i = 0; i < lives; i++) drawLifeDiamond(W - 14 - i * 12, 12, 4);

    const cloneNames = ["CLN0", "CLN32", "CLN64"];
    if (clone.alive) blit(cloneNames[Math.floor(clone.frame) % 3], clone.x, clone.y);

    for (const f of foes) {
      if (f.kind === "_BANG") {
        blit(f.hp > 4 ? "FBEXP5" : "FBEXP6", f.x, f.y);
      } else {
        blit(f.kind, f.x, f.y);
      }
    }

    const aim = Math.atan2(mouse.y - player.y, mouse.x - player.x);
    blit("PLY1-P", player.x, player.y, aim);

    // GUESS line bullets
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
  }

  function drawDead() {
    drawPlay();
    ctx.fillStyle = "rgba(0,0,0,0.55)";
    ctx.fillRect(0, 0, W, H);
    drawText("GAME OVER", W / 2 - 54, H / 2 - 10, 3);
    ctx.fillStyle = "#aaa";
    ctx.font = "10px monospace";
    ctx.fillText("Enter / 1 — select", W / 2 - 50, H / 2 + 24);
  }

  let last = performance.now();
  function frame(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    ctx.setTransform(SCALE, 0, 0, SCALE, 0, 0);
    if (mode === "select") drawSelect();
    else if (mode === "play") {
      updatePlay(dt);
      drawPlay();
    } else drawDead();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
