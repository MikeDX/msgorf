/* GUESS: video-derived Ms. Gorf sketch — not XC.LOGIC.
 * Port of reconstructed/video-demo/demo.js onto a true 320×204 RGB buffer. */
#include "game.h"
#include "font_gen.h"
#include "assets_gen.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_FOES 64
#define MAX_BULLETS 48
#define MAX_FX 16
#define MAX_CLONE_JOBS 16
#define MAX_GALAXY_STARS 512

#define GORF_R 7
#define GORF_SPEED 38.f
#define BULLET_MUZZLE 12.f
#define CLONE_PROCESS_T 0.35f
#define CLONE_EXIT_SPEED 55.f
#define CLONE_COOL 0.75f

#define GALAXY_ARMS 16
#define GALAXY_SHELLS_IN 17
#define GALAXY_SHELLS_OVER 3
#define GALAXY_SHELL_GAP 3.5f
#define GALAXY_R1 5.f
#define GALAXY_STARS_PER_SEC (7.f * 30.f)
#define GALAXY_SHELL_PEEL_DT 0.07f

typedef struct {
  float x, y, vx, vy;
  float life;
} bullet_t;

typedef struct {
  float x, y, vx, vy;
  const char *kind; /* asset name with underscores */
  int hp;
  float r;
  float cool;
} foe_t;

typedef struct {
  float x, y, hp;
} fx_t;

typedef struct {
  float t;
  int exit_right; /* 0 left, 1 right */
  const char *kind;
} clone_job_t;

typedef struct {
  float x, y;
  int shell;
} gstar_t;

typedef struct {
  const char *name;
  int flip;
} clone_frame_t;

static const clone_frame_t CLONE_CYCLE[] = {
    {"CLN32", 1},
    {"CLN64", 0},
    {"CLN32", 0},
    {"CLN0", 0},
};

static game_t *G;
static float score;
static int ships_left;
static float t_accum;
static float fire_cd;
static float player_x, player_y;
static int player_vis;
static float clone_x, clone_y, clone_frame;
static float clone_home_x, clone_home_y;
static int clone_vis;

static bullet_t bullets[MAX_BULLETS];
static int n_bullets;
static foe_t foes[MAX_FOES];
static int n_foes;
static fx_t fx[MAX_FX];
static int n_fx;
static clone_job_t clone_jobs[MAX_CLONE_JOBS];
static int n_clone_jobs;

static gstar_t galaxy_stars[MAX_GALAXY_STARS];
static int n_galaxy_stars;
static int galaxy_phase; /* 0 in, 1 out, 2 done */
static float galaxy_age, galaxy_peel_age;
static int galaxy_stars_drawn, galaxy_shells_peeled;

static int pix(float v) {
  return (int)floorf(v);
}

static int name_eq(const char *a, const char *b) {
  /* Match GORF-PAT / GORF_PAT */
  for (;;) {
    char ca = *a, cb = *b;
    if (ca == '-') ca = '_';
    if (cb == '-') cb = '_';
    if (ca != cb) return 0;
    if (!ca) return 1;
    a++;
    b++;
  }
}

static const terse_asset_t *find_asset(const char *name) {
  for (int i = 0; i < TERSE_ASSET_COUNT; i++) {
    if (name_eq(terse_assets[i]->name, name)) return terse_assets[i];
  }
  return NULL;
}

static void fb_clear(uint8_t *rgb) {
  memset(rgb, 0, (size_t)FB_W * FB_H * 3);
}

static void put_px(uint8_t *rgb, int x, int y, uint8_t r, uint8_t g, uint8_t b) {
  if (x < 0 || y < 0 || x >= FB_W || y >= FB_H) return;
  size_t i = ((size_t)y * FB_W + (size_t)x) * 3;
  rgb[i] = r;
  rgb[i + 1] = g;
  rgb[i + 2] = b;
}

static void blit_asset(uint8_t *rgb, const terse_asset_t *a, int cx, int cy, int flip) {
  if (!a) return;
  int x0 = cx - a->w / 2;
  int y0 = cy - a->h / 2;
  for (int j = 0; j < a->h; j++) {
    for (int i = 0; i < a->w; i++) {
      int sx = flip ? (a->w - 1 - i) : i;
      uint8_t v = a->pix[j * a->w + sx] & 3;
      if (!v) continue;
      put_px(rgb, x0 + i, y0 + j, a->pal[v][0], a->pal[v][1], a->pal[v][2]);
    }
  }
}

static void blit_named(uint8_t *rgb, const char *name, int cx, int cy, int flip) {
  blit_asset(rgb, find_asset(name), cx, cy, flip);
}

static const uint8_t *glyph_rows(char ch) {
  for (size_t i = 0; i < FONT_GLYPH_COUNT; i++) {
    if (FONT_GLYPHS[i].ch == ch) return FONT_GLYPHS[i].rows;
  }
  return NULL;
}

static int draw_glyph(uint8_t *rgb, char ch, int x, int y, int px) {
  const uint8_t *rows = glyph_rows(ch);
  if (!rows) return FONT_CW * px;
  for (int row = 0; row < FONT_CH; row++) {
    uint8_t bits = rows[row];
    for (int col = 0; col < FONT_CW; col++) {
      if (bits & (1u << (FONT_CW - 1 - col))) {
        for (int dy = 0; dy < px; dy++)
          for (int dx = 0; dx < px; dx++)
            put_px(rgb, x + col * px + dx, y + row * px + dy, FONT_RGB[0], FONT_RGB[1],
                   FONT_RGB[2]);
      }
    }
  }
  return (FONT_CW + 1) * px;
}

static int draw_text(uint8_t *rgb, const char *str, int x, int y, int px) {
  int cx = x;
  for (; *str; str++) cx += draw_glyph(rgb, *str, cx, y, px);
  return cx;
}

static void draw_line(uint8_t *rgb, int x0, int y0, int x1, int y1, uint8_t r, uint8_t g,
                      uint8_t b) {
  int dx = abs(x1 - x0), sx = x0 < x1 ? 1 : -1;
  int dy = -abs(y1 - y0), sy = y0 < y1 ? 1 : -1;
  int err = dx + dy;
  for (;;) {
    put_px(rgb, x0, y0, r, g, b);
    if (x0 == x1 && y0 == y1) break;
    int e2 = 2 * err;
    if (e2 >= dy) {
      err += dy;
      x0 += sx;
    }
    if (e2 <= dx) {
      err += dx;
      y0 += sy;
    }
  }
}

static void build_galaxy(void) {
  const float cx = FB_W * 0.5f;
  const float cy = FB_H * 0.52f;
  const float r0 = GALAXY_R1 + (GALAXY_SHELLS_IN - 1) * GALAXY_SHELL_GAP;
  const float start = (float)(-M_PI / 2.0 - (M_PI * 2.0) / 12.0 * 2.0);
  const float arm_step = (float)(-(M_PI * 2.0) / GALAXY_ARMS);
  const float twist = arm_step / 3.f;
  n_galaxy_stars = 0;
  for (int s = 0; s < GALAXY_SHELLS_IN; s++) {
    float r = r0 - s * GALAXY_SHELL_GAP;
    float base = start + s * twist;
    for (int a = 0; a < GALAXY_ARMS; a++) {
      if (n_galaxy_stars >= MAX_GALAXY_STARS) return;
      float ang = base + a * arm_step;
      galaxy_stars[n_galaxy_stars].x = cx + cosf(ang) * r;
      galaxy_stars[n_galaxy_stars].y = cy + sinf(ang) * r;
      galaxy_stars[n_galaxy_stars].shell = s;
      n_galaxy_stars++;
    }
  }
  for (int s = 0; s < GALAXY_SHELLS_OVER; s++) {
    float r = -((s + 1) * GALAXY_SHELL_GAP);
    int shell = GALAXY_SHELLS_IN + s;
    float base = start + shell * twist;
    for (int a = 0; a < GALAXY_ARMS; a++) {
      if (n_galaxy_stars >= MAX_GALAXY_STARS) return;
      float ang = base + a * arm_step;
      galaxy_stars[n_galaxy_stars].x = cx + cosf(ang) * r;
      galaxy_stars[n_galaxy_stars].y = cy + sinf(ang) * r;
      galaxy_stars[n_galaxy_stars].shell = shell;
      n_galaxy_stars++;
    }
  }
}

static float frand(void) { return (float)(rand() % 10000) / 10000.f; }

static void rand_vel(float *vx, float *vy) {
  float a = frand() * (float)(M_PI * 2.0);
  float s = GORF_SPEED * (0.75f + frand() * 0.5f);
  *vx = cosf(a) * s;
  *vy = sinf(a) * s;
}

static void spawn_gorf(float x, float y, float vx, float vy, const char *kind, float cool) {
  if (n_foes >= MAX_FOES) return;
  foe_t *f = &foes[n_foes++];
  f->x = x;
  f->y = y;
  f->vx = vx;
  f->vy = vy;
  f->kind = kind ? kind : "GORF_PAT";
  f->hp = 1;
  f->r = GORF_R;
  f->cool = cool;
}

/* Keep gorfs moving after wall/pair bounce (elastic swaps can kill speed). */
static void keep_gorf_speed(foe_t *e) {
  float sp = hypotf(e->vx, e->vy);
  float lo = GORF_SPEED * 0.7f;
  float hi = GORF_SPEED * 1.35f;
  if (sp < 8.f) {
    rand_vel(&e->vx, &e->vy);
    return;
  }
  if (sp < lo) {
    float s = lo / sp;
    e->vx *= s;
    e->vy *= s;
  } else if (sp > hi) {
    float s = hi / sp;
    e->vx *= s;
    e->vy *= s;
  }
}

static void spawn_gorf_at_edge(int side) {
  const float margin = 18.f;
  float x, y, vx, vy;
  side = side % 4;
  if (side == 0) {
    x = margin + frand() * (FB_W - margin * 2);
    y = margin + 22 + frand() * 20;
  } else if (side == 1) {
    x = margin + frand() * (FB_W - margin * 2);
    y = FB_H - margin - frand() * 24;
  } else if (side == 2) {
    x = margin + frand() * 24;
    y = margin + 28 + frand() * (FB_H - margin * 2 - 28);
  } else {
    x = FB_W - margin - frand() * 24;
    y = margin + 28 + frand() * (FB_H - margin * 2 - 28);
  }
  rand_vel(&vx, &vy);
  spawn_gorf(x, y, vx, vy, "GORF_PAT", 0);
}

static void spawn_burst(float x, float y) {
  if (n_fx >= MAX_FX) return;
  fx[n_fx].x = x;
  fx[n_fx].y = y;
  fx[n_fx].hp = 0.45f;
  n_fx++;
}

static void reveal_player_and_clone(void) {
  player_vis = 1;
  player_x = FB_W * 0.5f;
  player_y = FB_H * 0.5f;
  clone_vis = 1;
  /* GUESS: continuous Lissajous drift around a home near centre (footage). */
  clone_home_x = FB_W * 0.5f + 20.f;
  clone_home_y = FB_H * 0.5f - 6.f;
  clone_x = clone_home_x;
  clone_y = clone_home_y;
  clone_frame = 0;
}

static void begin_level(game_t *g) {
  (void)g;
  score = 0;
  ships_left = 3;
  n_bullets = n_foes = n_fx = n_clone_jobs = 0;
  player_vis = 0;
  clone_vis = 0;
  fire_cd = 0;
  t_accum = 0;
  for (int i = 0; i < 4; i++) spawn_gorf_at_edge(i);
  galaxy_phase = 0;
  galaxy_age = 0;
  galaxy_peel_age = 0;
  galaxy_stars_drawn = 0;
  galaxy_shells_peeled = 0;
  G->mode = MODE_INTRO;
}

static void draw_galaxy(uint8_t *rgb) {
  if (galaxy_phase == 2) return;
  int n = galaxy_stars_drawn;
  if (n > n_galaxy_stars) n = n_galaxy_stars;
  int total = GALAXY_SHELLS_IN + GALAXY_SHELLS_OVER;
  for (int i = 0; i < n; i++) {
    gstar_t *st = &galaxy_stars[i];
    if (galaxy_phase == 1 && st->shell < galaxy_shells_peeled) continue;
    if (st->shell >= total) continue;
    put_px(rgb, pix(st->x), pix(st->y), FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
  }
}

static void draw_hud(uint8_t *rgb) {
  char buf[32];
  snprintf(buf, sizeof buf, "$%d", (int)score);
  int x = draw_text(rgb, buf, 4, 4, 1);
  x += 4;
  if (((int)(t_accum * 4.f) % 2) == 0) blit_named(rgb, "P1UP", x + 4, 10, 0);
  x += 12;
  for (int i = 0; i < ships_left; i++) blit_named(rgb, "SBASE", x + 6 + i * 10, 10, 0);
}

static void draw_select(uint8_t *rgb) {
  fb_clear(rgb);
  draw_text(rgb, "$8000", 8, 8, 1);
  /* boxed 1 / 2 */
  int box_l = 8 + 6 * 6;
  for (int i = 0; i < FONT_CW + 4; i++) {
    put_px(rgb, box_l + i, 6, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
    put_px(rgb, box_l + i, 6 + FONT_CH + 3, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
  }
  for (int j = 0; j < FONT_CH + 4; j++) {
    put_px(rgb, box_l, 6 + j, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
    put_px(rgb, box_l + FONT_CW + 3, 6 + j, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
  }
  draw_glyph(rgb, '1', box_l + 2, 8, 1);

  int box_r = FB_W - 8 - 6 * 6 - FONT_CW - 4;
  for (int i = 0; i < FONT_CW + 4; i++) {
    put_px(rgb, box_r + i, 6, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
    put_px(rgb, box_r + i, 6 + FONT_CH + 3, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
  }
  for (int j = 0; j < FONT_CH + 4; j++) {
    put_px(rgb, box_r, 6 + j, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
    put_px(rgb, box_r + FONT_CW + 3, 6 + j, FONT_RGB[0], FONT_RGB[1], FONT_RGB[2]);
  }
  draw_glyph(rgb, '2', box_r + 2, 8, 1);
  draw_text(rgb, "$4500", FB_W - 8 - 5 * 6, 8, 1);

  const char *msg1 = "SELECT 1 OR 2";
  const char *msg2 = "PLAYER GAME";
  int px = 2;
  int w1 = (int)strlen(msg1) * (FONT_CW + 1) * px;
  int w2 = (int)strlen(msg2) * (FONT_CW + 1) * px;
  draw_text(rgb, msg1, (FB_W - w1) / 2, (int)(FB_H * 0.4f), px);
  draw_text(rgb, msg2, (FB_W - w2) / 2, (int)(FB_H * 0.4f) + 22, px);
}

static void bounce_walls(foe_t *e) {
  const float margin = 4.f;
  const float top = 22.f;
  if (e->x - e->r < margin) {
    e->x = margin + e->r;
    if (e->vx < 0) e->vx = -e->vx;
  } else if (e->x + e->r > FB_W - margin) {
    e->x = FB_W - margin - e->r;
    if (e->vx > 0) e->vx = -e->vx;
  }
  if (e->y - e->r < top) {
    e->y = top + e->r;
    if (e->vy < 0) e->vy = -e->vy;
  } else if (e->y + e->r > FB_H - margin) {
    e->y = FB_H - margin - e->r;
    if (e->vy > 0) e->vy = -e->vy;
  }
}

static void bounce_pair(foe_t *a, foe_t *b) {
  float dx = b->x - a->x;
  float dy = b->y - a->y;
  float dist = hypotf(dx, dy);
  float min_d = a->r + b->r;
  if (dist < 1e-3f) {
    /* stacked — shove apart so they don't lock */
    dist = 1.f;
    dx = 1.f;
    dy = 0.f;
  }
  if (dist >= min_d) return;
  float overlap = (min_d - dist) * 0.5f + 0.5f;
  float nx = dx / dist, ny = dy / dist;
  a->x -= nx * overlap;
  a->y -= ny * overlap;
  b->x += nx * overlap;
  b->y += ny * overlap;
  float avn = a->vx * nx + a->vy * ny;
  float bvn = b->vx * nx + b->vy * ny;
  /* only exchange if approaching — avoids sticky re-collision thrash */
  if (avn - bvn > 0.f) return;
  a->vx += (bvn - avn) * nx;
  a->vy += (bvn - avn) * ny;
  b->vx += (avn - bvn) * nx;
  b->vy += (avn - bvn) * ny;
}

static const clone_frame_t *current_clone_frame(void) {
  int i = ((int)clone_frame) % (int)(sizeof CLONE_CYCLE / sizeof CLONE_CYCLE[0]);
  if (i < 0) i = 0;
  return &CLONE_CYCLE[i];
}

typedef struct {
  float x0, x1, y0, y1;
  int exit_right;
} port_t;

static void clone_ports(port_t *left, port_t *right) {
  const clone_frame_t *cf = current_clone_frame();
  const terse_asset_t *a = find_asset(cf->name);
  int w = a ? a->w : 32;
  int h = a ? a->h : 32;
  float hw = w * 0.5f, hh = h * 0.5f;
  float pw = 5.f;
  float y0 = clone_y - hh * 0.35f;
  float y1 = clone_y + hh * 0.5f;
  left->x0 = clone_x - hw;
  left->x1 = clone_x - hw + pw;
  left->y0 = y0;
  left->y1 = y1;
  left->exit_right = 1;
  right->x0 = clone_x + hw - pw;
  right->x1 = clone_x + hw;
  right->y0 = y0;
  right->y1 = y1;
  right->exit_right = 0;
}

static int overlaps_port(const foe_t *f, const port_t *p) {
  return f->x + f->r > p->x0 && f->x - f->r < p->x1 && f->y + f->r > p->y0 &&
         f->y - f->r < p->y1;
}

static void emit_clones(int exit_right, const char *kind) {
  port_t L, R;
  clone_ports(&L, &R);
  port_t *port = exit_right ? &R : &L;
  float mid_x = (port->x0 + port->x1) * 0.5f;
  float mid_y = (port->y0 + port->y1) * 0.5f;
  float dir = exit_right ? 1.f : -1.f;
  float dys[2] = {-6.f, 6.f};
  for (int i = 0; i < 2; i++) {
    spawn_gorf(mid_x + dir * 8.f, mid_y + dys[i], dir * CLONE_EXIT_SPEED, dys[i] * 2.f, kind,
               CLONE_COOL);
  }
}

static void process_clone_machine(float dt) {
  if (!clone_vis) return;
  const int ncycle = (int)(sizeof CLONE_CYCLE / sizeof CLONE_CYCLE[0]);
  clone_frame = fmodf(clone_frame + dt * 2.4f, (float)ncycle);
  if (clone_frame < 0) clone_frame += ncycle;
  /* Continuous path (not integrated+truncated — that stuttered). */
  clone_x = clone_home_x + sinf(t_accum * 0.55f) * 28.f + sinf(t_accum * 0.19f) * 6.f;
  clone_y = clone_home_y + cosf(t_accum * 0.37f) * 20.f + sinf(t_accum * 0.23f + 1.1f) * 5.f;
  if (clone_x < 48.f) clone_x = 48.f;
  if (clone_x > FB_W - 48.f) clone_x = FB_W - 48.f;
  if (clone_y < 48.f) clone_y = 48.f;
  if (clone_y > FB_H - 40.f) clone_y = FB_H - 40.f;

  port_t L, R;
  clone_ports(&L, &R);
  for (int i = 0; i < n_foes; i++) {
    foe_t *f = &foes[i];
    if (f->hp <= 0 || f->cool > 0) continue;
    int hit = -1;
    if (overlaps_port(f, &L))
      hit = L.exit_right;
    else if (overlaps_port(f, &R))
      hit = R.exit_right;
    if (hit < 0) continue;
    f->hp = 0;
    if (n_clone_jobs < MAX_CLONE_JOBS) {
      clone_jobs[n_clone_jobs].t = CLONE_PROCESS_T;
      clone_jobs[n_clone_jobs].exit_right = hit;
      clone_jobs[n_clone_jobs].kind = f->kind;
      n_clone_jobs++;
    }
  }

  int w = 0;
  for (int i = 0; i < n_clone_jobs; i++) {
    clone_jobs[i].t -= dt;
    if (clone_jobs[i].t <= 0) {
      emit_clones(clone_jobs[i].exit_right, clone_jobs[i].kind);
    } else {
      clone_jobs[w++] = clone_jobs[i];
    }
  }
  n_clone_jobs = w;

  /* compact dead foes */
  w = 0;
  for (int i = 0; i < n_foes; i++)
    if (foes[i].hp > 0) foes[w++] = foes[i];
  n_foes = w;
}

static void update_intro(float dt) {
  t_accum += dt;
  galaxy_age += dt;
  if (galaxy_phase == 0) {
    galaxy_stars_drawn = (int)(galaxy_age * GALAXY_STARS_PER_SEC);
    if (galaxy_stars_drawn > n_galaxy_stars) galaxy_stars_drawn = n_galaxy_stars;
    if (galaxy_stars_drawn >= n_galaxy_stars) {
      galaxy_phase = 1;
      galaxy_peel_age = 0;
      galaxy_shells_peeled = 0;
    }
  } else if (galaxy_phase == 1) {
    galaxy_peel_age += dt;
    galaxy_shells_peeled = (int)(galaxy_peel_age / GALAXY_SHELL_PEEL_DT);
    int total = GALAXY_SHELLS_IN + GALAXY_SHELLS_OVER;
    if (galaxy_shells_peeled > total) galaxy_shells_peeled = total;
    if (galaxy_shells_peeled >= total) {
      galaxy_phase = 2;
      reveal_player_and_clone();
      G->mode = MODE_PLAY;
    }
  }
}

static int key_down(game_t *g, int sc) {
  if (sc < 0 || sc >= 512) return 0;
  return g->keys[sc];
}

static void update_play(game_t *g, float dt) {
  t_accum += dt;
  if (!player_vis) return;

  float speed = 70.f;
  float dx = 0, dy = 0;
  /* SDL scancodes: A=4 D=7 W=26 S=22 Left=80 Right=79 Up=82 Down=81 Space=44 */
  if (key_down(g, 4) || key_down(g, 80)) dx -= 1;
  if (key_down(g, 7) || key_down(g, 79)) dx += 1;
  if (key_down(g, 26) || key_down(g, 82)) dy -= 1;
  if (key_down(g, 22) || key_down(g, 81)) dy += 1;
  if (dx || dy) {
    float n = hypotf(dx, dy);
    if (n < 1e-3f) n = 1.f;
    player_x += (dx / n) * speed * dt;
    player_y += (dy / n) * speed * dt;
  }
  if (player_x < 12) player_x = 12;
  if (player_x > FB_W - 12) player_x = FB_W - 12;
  if (player_y < 28) player_y = 28;
  if (player_y > FB_H - 12) player_y = FB_H - 12;

  float aim = atan2f(g->mouse_y - player_y, g->mouse_x - player_x);
  fire_cd -= dt;
  int fire = g->mouse_down || key_down(g, 44) || key_down(g, 14); /* Space / K */
  if (fire && fire_cd <= 0 && n_bullets < MAX_BULLETS) {
    fire_cd = 0.12f;
    float sp = 160.f;
    float c = cosf(aim), s = sinf(aim);
    bullet_t *b = &bullets[n_bullets++];
    b->x = player_x + c * BULLET_MUZZLE;
    b->y = player_y + s * BULLET_MUZZLE;
    b->vx = c * sp;
    b->vy = s * sp;
    b->life = 0.9f;
  }

  int wb = 0;
  for (int i = 0; i < n_bullets; i++) {
    bullet_t *b = &bullets[i];
    b->x += b->vx * dt;
    b->y += b->vy * dt;
    b->life -= dt;
    if (b->life > 0 && b->x > -10 && b->x < FB_W + 10 && b->y > -10 && b->y < FB_H + 10)
      bullets[wb++] = *b;
  }
  n_bullets = wb;

  process_clone_machine(dt);

  for (int i = 0; i < n_foes; i++) {
    foe_t *f = &foes[i];
    if (f->cool > 0) f->cool -= dt;
    f->x += f->vx * dt;
    f->y += f->vy * dt;
    bounce_walls(f);
  }
  for (int i = 0; i < n_foes; i++)
    for (int j = i + 1; j < n_foes; j++) bounce_pair(&foes[i], &foes[j]);
  for (int i = 0; i < n_foes; i++) {
    bounce_walls(&foes[i]); /* re-clamp after pair shove */
    keep_gorf_speed(&foes[i]);
  }
  for (int bi = 0; bi < n_bullets; bi++) {
    bullet_t *b = &bullets[bi];
    for (int fi = 0; fi < n_foes; fi++) {
      foe_t *f = &foes[fi];
      if (f->hp <= 0) continue;
      if (hypotf(b->x - f->x, b->y - f->y) < f->r + 3) {
        f->hp = 0;
        b->life = 0;
        score += 1000;
        spawn_burst(f->x, f->y);
      }
    }
  }
  wb = 0;
  for (int i = 0; i < n_bullets; i++)
    if (bullets[i].life > 0) bullets[wb++] = bullets[i];
  n_bullets = wb;
  int wf = 0;
  for (int i = 0; i < n_foes; i++)
    if (foes[i].hp > 0) foes[wf++] = foes[i];
  n_foes = wf;

  for (int i = 0; i < n_fx; i++) fx[i].hp -= dt;
  wf = 0;
  for (int i = 0; i < n_fx; i++)
    if (fx[i].hp > 0) fx[wf++] = fx[i];
  n_fx = wf;

  for (int i = 0; i < n_foes; i++) {
    foe_t *f = &foes[i];
    if (hypotf(f->x - player_x, f->y - player_y) < f->r + 8) {
      ships_left -= 1;
      spawn_burst(player_x, player_y);
      player_x = FB_W * 0.5f;
      player_y = FB_H * 0.5f;
      if (ships_left <= 0) G->mode = MODE_DEAD;
      break;
    }
  }
}

static void draw_world(uint8_t *rgb, int with_galaxy) {
  fb_clear(rgb);
  for (int i = 0; i < n_foes; i++) blit_named(rgb, foes[i].kind, pix(foes[i].x), pix(foes[i].y), 0);
  if (with_galaxy) draw_galaxy(rgb);
  for (int i = 0; i < n_fx; i++)
    blit_named(rgb, fx[i].hp > 0.22f ? "FBEXP5" : "FBEXP6", pix(fx[i].x), pix(fx[i].y), 0);
  if (clone_vis) {
    const clone_frame_t *cf = current_clone_frame();
    blit_named(rgb, cf->name, pix(clone_x), pix(clone_y), cf->flip);
  }
  if (player_vis) blit_named(rgb, "PLY1_P", pix(player_x), pix(player_y), 0);
  for (int i = 0; i < n_bullets; i++) {
    bullet_t *b = &bullets[i];
    float ang = atan2f(b->vy, b->vx);
    float len = 5.f;
    int x0 = pix(b->x - cosf(ang) * len);
    int y0 = pix(b->y - sinf(ang) * len);
    int x1 = pix(b->x + cosf(ang) * len);
    int y1 = pix(b->y + sinf(ang) * len);
    draw_line(rgb, x0, y0, x1, y1, 240, 220, 180);
  }
  draw_hud(rgb);
}

void game_init(game_t *g, uint8_t *rgb) {
  memset(g, 0, sizeof *g);
  g->rgb = rgb;
  g->mode = MODE_SELECT;
  g->mouse_x = FB_W / 2;
  g->mouse_y = FB_H / 2;
  G = g;
  build_galaxy();
  srand(1);
}

void game_keydown(game_t *g, int scancode) {
  if (scancode >= 0 && scancode < 512) g->keys[scancode] = 1;
  if (g->mode == MODE_SELECT) {
    if (scancode == 30 || scancode == 31) { /* 1 / 2 */
      g->start_players = (scancode == 30) ? 1 : 2;
      begin_level(g);
    }
  } else if (g->mode == MODE_DEAD) {
    if (scancode == 40 || scancode == 30) /* Enter / 1 */ g->mode = MODE_SELECT;
  }
}

void game_keyup(game_t *g, int scancode) {
  if (scancode >= 0 && scancode < 512) g->keys[scancode] = 0;
}

void game_mouse(game_t *g, int x, int y, int down) {
  g->mouse_x = x;
  g->mouse_y = y;
  if (down >= 0) g->mouse_down = down;
}

void game_update(game_t *g, float dt) {
  if (dt > 0.05f) dt = 0.05f;
  if (g->mode == MODE_INTRO) update_intro(dt);
  else if (g->mode == MODE_PLAY) update_play(g, dt);
}

void game_render(game_t *g) {
  uint8_t *rgb = g->rgb;
  if (g->mode == MODE_SELECT) {
    draw_select(rgb);
  } else if (g->mode == MODE_INTRO) {
    draw_world(rgb, 1);
  } else if (g->mode == MODE_PLAY) {
    draw_world(rgb, 0);
  } else {
    draw_world(rgb, 0);
    /* dim overlay */
    for (int y = 0; y < FB_H; y++) {
      for (int x = 0; x < FB_W; x++) {
        size_t i = ((size_t)y * FB_W + x) * 3;
        rgb[i] = (uint8_t)(rgb[i] * 0.45f);
        rgb[i + 1] = (uint8_t)(rgb[i + 1] * 0.45f);
        rgb[i + 2] = (uint8_t)(rgb[i + 2] * 0.45f);
      }
    }
    const char *msg = "GAME OVER";
    int px = 2;
    int w = (int)strlen(msg) * (FONT_CW + 1) * px;
    draw_text(rgb, msg, (FB_W - w) / 2, FB_H / 2 - 8, px);
  }
}
