#include "replay.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REPLAY_MAGIC "MGR1"
#define REPLAY_VERSION 1
#define REPLAY_MAX_EVENTS 65536
#define REPLAY_BUILD_MAX 64

/* flags bit layout — matches keys the sim actually reads */
#define RF_MOUSE_DOWN (1u << 0)
#define RF_SHIELD     (1u << 1)
#define RF_KEY_W      (1u << 2)
#define RF_KEY_A      (1u << 3)
#define RF_KEY_S      (1u << 4)
#define RF_KEY_D      (1u << 5)
#define RF_KEY_UP     (1u << 6)
#define RF_KEY_DOWN   (1u << 7)
#define RF_KEY_LEFT   (1u << 8)
#define RF_KEY_RIGHT  (1u << 9)
#define RF_KEY_SPACE  (1u << 10)
#define RF_KEY_K      (1u << 11)

typedef struct {
  int16_t move_x, move_y;
  int16_t aim_x, aim_y;
  int16_t mouse_x, mouse_y;
  uint16_t flags;
} replay_snap_t;

typedef struct {
  uint32_t tick;
  replay_snap_t snap;
} replay_event_t;

static char g_build_id[REPLAY_BUILD_MAX] = "dev";
static replay_mode_t g_mode = REPLAY_IDLE;
static uint32_t g_seed;
static uint32_t g_score;
static unsigned g_ticks;
static replay_snap_t g_last;
static int g_have_last;
static replay_event_t *g_events;
static int g_n_events;
static int g_cap_events;
static int g_play_idx;
static replay_snap_t g_play_snap;

static uint8_t *g_blob;
static size_t g_blob_len;

static int16_t qaxis(float v) {
  if (v > 1.f) v = 1.f;
  if (v < -1.f) v = -1.f;
  return (int16_t)(v * 32767.f);
}

static float deqaxis(int16_t v) { return (float)v / 32767.f; }

static void snap_from_game(game_t *g, replay_snap_t *s) {
  s->move_x = qaxis(g->pad_move_x);
  s->move_y = qaxis(g->pad_move_y);
  s->aim_x = qaxis(g->pad_aim_x);
  s->aim_y = qaxis(g->pad_aim_y);
  s->mouse_x = (int16_t)g->mouse_x;
  s->mouse_y = (int16_t)g->mouse_y;
  uint16_t f = 0;
  if (g->mouse_down) f |= RF_MOUSE_DOWN;
  if (g->pad_shield) f |= RF_SHIELD;
  if (g->keys[26]) f |= RF_KEY_W;
  if (g->keys[4]) f |= RF_KEY_A;
  if (g->keys[22]) f |= RF_KEY_S;
  if (g->keys[7]) f |= RF_KEY_D;
  if (g->keys[82]) f |= RF_KEY_UP;
  if (g->keys[81]) f |= RF_KEY_DOWN;
  if (g->keys[80]) f |= RF_KEY_LEFT;
  if (g->keys[79]) f |= RF_KEY_RIGHT;
  if (g->keys[44]) f |= RF_KEY_SPACE;
  if (g->keys[14]) f |= RF_KEY_K;
  s->flags = f;
}

static void snap_to_game(game_t *g, const replay_snap_t *s) {
  g->pad_move_x = deqaxis(s->move_x);
  g->pad_move_y = deqaxis(s->move_y);
  g->pad_aim_x = deqaxis(s->aim_x);
  g->pad_aim_y = deqaxis(s->aim_y);
  g->mouse_x = (int)s->mouse_x;
  g->mouse_y = (int)s->mouse_y;
  g->mouse_down = (s->flags & RF_MOUSE_DOWN) ? 1 : 0;
  g->pad_shield = (s->flags & RF_SHIELD) ? 1 : 0;
  g->keys[26] = (s->flags & RF_KEY_W) ? 1 : 0;
  g->keys[4] = (s->flags & RF_KEY_A) ? 1 : 0;
  g->keys[22] = (s->flags & RF_KEY_S) ? 1 : 0;
  g->keys[7] = (s->flags & RF_KEY_D) ? 1 : 0;
  g->keys[82] = (s->flags & RF_KEY_UP) ? 1 : 0;
  g->keys[81] = (s->flags & RF_KEY_DOWN) ? 1 : 0;
  g->keys[80] = (s->flags & RF_KEY_LEFT) ? 1 : 0;
  g->keys[79] = (s->flags & RF_KEY_RIGHT) ? 1 : 0;
  g->keys[44] = (s->flags & RF_KEY_SPACE) ? 1 : 0;
  g->keys[14] = (s->flags & RF_KEY_K) ? 1 : 0;
}

static int snap_eq(const replay_snap_t *a, const replay_snap_t *b) {
  return a->move_x == b->move_x && a->move_y == b->move_y && a->aim_x == b->aim_x &&
         a->aim_y == b->aim_y && a->mouse_x == b->mouse_x && a->mouse_y == b->mouse_y &&
         a->flags == b->flags;
}

static int ensure_cap(int need) {
  if (need <= g_cap_events) return 1;
  int ncap = g_cap_events ? g_cap_events * 2 : 256;
  while (ncap < need) ncap *= 2;
  if (ncap > REPLAY_MAX_EVENTS) ncap = REPLAY_MAX_EVENTS;
  if (need > ncap) return 0;
  replay_event_t *p = (replay_event_t *)realloc(g_events, (size_t)ncap * sizeof *p);
  if (!p) return 0;
  g_events = p;
  g_cap_events = ncap;
  return 1;
}

static void free_blob(void) {
  free(g_blob);
  g_blob = NULL;
  g_blob_len = 0;
}

static void w8(uint8_t **p, uint8_t v) { *(*p)++ = v; }
static void w16(uint8_t **p, uint16_t v) {
  *(*p)++ = (uint8_t)(v & 0xff);
  *(*p)++ = (uint8_t)((v >> 8) & 0xff);
}
static void w32(uint8_t **p, uint32_t v) {
  *(*p)++ = (uint8_t)(v & 0xff);
  *(*p)++ = (uint8_t)((v >> 8) & 0xff);
  *(*p)++ = (uint8_t)((v >> 16) & 0xff);
  *(*p)++ = (uint8_t)((v >> 24) & 0xff);
}

static int r8(const uint8_t **p, const uint8_t *end, uint8_t *o) {
  if (*p >= end) return 0;
  *o = *(*p)++;
  return 1;
}
static int r16(const uint8_t **p, const uint8_t *end, uint16_t *o) {
  if (*p + 2 > end) return 0;
  *o = (uint16_t)(*p)[0] | ((uint16_t)(*p)[1] << 8);
  *p += 2;
  return 1;
}
static int r32(const uint8_t **p, const uint8_t *end, uint32_t *o) {
  if (*p + 4 > end) return 0;
  *o = (uint32_t)(*p)[0] | ((uint32_t)(*p)[1] << 8) | ((uint32_t)(*p)[2] << 16) |
       ((uint32_t)(*p)[3] << 24);
  *p += 4;
  return 1;
}

static void write_snap(uint8_t **p, const replay_snap_t *s) {
  w16(p, (uint16_t)s->move_x);
  w16(p, (uint16_t)s->move_y);
  w16(p, (uint16_t)s->aim_x);
  w16(p, (uint16_t)s->aim_y);
  w16(p, (uint16_t)s->mouse_x);
  w16(p, (uint16_t)s->mouse_y);
  w16(p, s->flags);
}

static int read_snap(const uint8_t **p, const uint8_t *end, replay_snap_t *s) {
  uint16_t u;
  if (!r16(p, end, &u)) return 0;
  s->move_x = (int16_t)u;
  if (!r16(p, end, &u)) return 0;
  s->move_y = (int16_t)u;
  if (!r16(p, end, &u)) return 0;
  s->aim_x = (int16_t)u;
  if (!r16(p, end, &u)) return 0;
  s->aim_y = (int16_t)u;
  if (!r16(p, end, &u)) return 0;
  s->mouse_x = (int16_t)u;
  if (!r16(p, end, &u)) return 0;
  s->mouse_y = (int16_t)u;
  if (!r16(p, end, &u)) return 0;
  s->flags = u;
  return 1;
}

void replay_set_build_id(const char *id) {
  if (!id || !id[0]) id = "dev";
  snprintf(g_build_id, sizeof g_build_id, "%s", id);
}

const char *replay_build_id(void) { return g_build_id; }

void replay_reset(void) {
  g_mode = REPLAY_IDLE;
  g_seed = 0;
  g_score = 0;
  g_ticks = 0;
  g_have_last = 0;
  g_n_events = 0;
  g_play_idx = 0;
  memset(&g_last, 0, sizeof g_last);
  memset(&g_play_snap, 0, sizeof g_play_snap);
  free_blob();
}

void replay_cancel(void) { replay_reset(); }

void replay_begin_record(uint32_t seed) {
  free_blob();
  g_mode = REPLAY_RECORDING;
  g_seed = seed;
  g_score = 0;
  g_ticks = 0;
  g_have_last = 0;
  g_n_events = 0;
  g_play_idx = 0;
  memset(&g_last, 0, sizeof g_last);
}

void replay_begin_play(void) {
  g_mode = REPLAY_PLAYING;
  g_play_idx = 0;
  g_ticks = 0;
  memset(&g_play_snap, 0, sizeof g_play_snap);
  if (g_n_events > 0 && g_events[0].tick == 0)
    g_play_snap = g_events[0].snap;
}

static int push_event(uint32_t tick, const replay_snap_t *s) {
  if (!ensure_cap(g_n_events + 1)) return 0;
  g_events[g_n_events].tick = tick;
  g_events[g_n_events].snap = *s;
  g_n_events++;
  return 1;
}

void replay_before_update(game_t *g, unsigned tick) {
  if (g_mode == REPLAY_RECORDING) {
    replay_snap_t s;
    snap_from_game(g, &s);
    if (!g_have_last || !snap_eq(&s, &g_last)) {
      push_event(tick, &s);
      g_last = s;
      g_have_last = 1;
    }
    g_ticks = tick + 1;
  } else if (g_mode == REPLAY_PLAYING) {
    while (g_play_idx < g_n_events && g_events[g_play_idx].tick <= tick) {
      g_play_snap = g_events[g_play_idx].snap;
      g_play_idx++;
    }
    snap_to_game(g, &g_play_snap);
    g_ticks = tick + 1;
  }
}

void replay_capture_from_game(game_t *g) {
  (void)g;
}

void replay_apply_to_game(game_t *g) {
  if (g_mode == REPLAY_PLAYING) snap_to_game(g, &g_play_snap);
}

void replay_end_record(uint32_t score, unsigned ticks) {
  if (g_mode != REPLAY_RECORDING) return;
  g_score = score;
  g_ticks = ticks;

  size_t bid_len = strlen(g_build_id);
  if (bid_len > 255) bid_len = 255;
  /* magic4 + ver1 + flags1 + bid_len1 + bid + seed4 + score4 + ticks4 + nevents4 + events */
  size_t need = 4 + 1 + 1 + 1 + bid_len + 4 + 4 + 4 + 4 + (size_t)g_n_events * (4 + 14);
  uint8_t *buf = (uint8_t *)malloc(need);
  if (!buf) {
    g_mode = REPLAY_IDLE;
    return;
  }
  uint8_t *p = buf;
  memcpy(p, REPLAY_MAGIC, 4);
  p += 4;
  w8(&p, REPLAY_VERSION);
  w8(&p, 0);
  w8(&p, (uint8_t)bid_len);
  memcpy(p, g_build_id, bid_len);
  p += bid_len;
  w32(&p, g_seed);
  w32(&p, g_score);
  w32(&p, (uint32_t)g_ticks);
  w32(&p, (uint32_t)g_n_events);
  for (int i = 0; i < g_n_events; i++) {
    w32(&p, g_events[i].tick);
    write_snap(&p, &g_events[i].snap);
  }
  free_blob();
  g_blob = buf;
  g_blob_len = (size_t)(p - buf);
  g_mode = REPLAY_READY;
}

replay_mode_t replay_mode(void) { return g_mode; }
uint32_t replay_seed(void) { return g_seed; }
uint32_t replay_score(void) { return g_score; }
unsigned replay_ticks(void) { return g_ticks; }
int replay_playing(void) { return g_mode == REPLAY_PLAYING; }
int replay_ready(void) { return g_mode == REPLAY_READY; }

const uint8_t *replay_blob(void) { return g_blob; }
size_t replay_blob_len(void) { return g_blob_len; }

int replay_load(const uint8_t *data, size_t len) {
  if (!data || len < 20) return 0;
  const uint8_t *p = data;
  const uint8_t *end = data + len;
  if (memcmp(p, REPLAY_MAGIC, 4) != 0) return 0;
  p += 4;
  uint8_t ver, flags, bid_len;
  if (!r8(&p, end, &ver) || !r8(&p, end, &flags) || !r8(&p, end, &bid_len)) return 0;
  if (ver != REPLAY_VERSION) return 0;
  if (p + bid_len > end) return 0;
  char bid[REPLAY_BUILD_MAX];
  if (bid_len >= sizeof bid) return 0;
  memcpy(bid, p, bid_len);
  bid[bid_len] = 0;
  p += bid_len;
  (void)flags;
  uint32_t seed, score, ticks, ne;
  if (!r32(&p, end, &seed) || !r32(&p, end, &score) || !r32(&p, end, &ticks) ||
      !r32(&p, end, &ne))
    return 0;
  if (ne > (uint32_t)REPLAY_MAX_EVENTS) return 0;
  if (!ensure_cap((int)ne)) return 0;
  for (uint32_t i = 0; i < ne; i++) {
    uint32_t tick;
    replay_snap_t s;
    if (!r32(&p, end, &tick) || !read_snap(&p, end, &s)) return 0;
    g_events[i].tick = tick;
    g_events[i].snap = s;
  }
  free_blob();
  g_blob = (uint8_t *)malloc(len);
  if (g_blob) {
    memcpy(g_blob, data, len);
    g_blob_len = len;
  }
  g_n_events = (int)ne;
  g_seed = seed;
  g_score = score;
  g_ticks = ticks;
  snprintf(g_build_id, sizeof g_build_id, "%s", bid[0] ? bid : "dev");
  replay_begin_play();
  return 1;
}
