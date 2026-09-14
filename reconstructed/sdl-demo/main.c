/* GUESS SDL host — simulate & paint only on 320×204, then integer-scale to window.
 * Never present fractional buffer→window mapping (that looks like “scaled pixel” motion). */
#include "game.h"
#include "replay.h"
#include "sound.h"

#include <SDL.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef VIEW_SCALE
#define VIEW_SCALE 3
#endif

/* Arcade-style fixed tick. Sim + present aim for 60Hz so SHLD mines flash 1:1. */
#define SIM_HZ 60
#define SIM_DT (1.f / (float)SIM_HZ)

#define PAD_DEADZONE 0.18f

static uint8_t fb[FB_W * FB_H * 3];
static game_t game;
static int running = 1;
static SDL_GameController *pad;

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

typedef struct {
  SDL_Window *win;
  SDL_Renderer *ren;
  SDL_Texture *tex;
  Uint64 last;
  Uint64 frame_start;
  int scale; /* integer pixels of window per buffer pixel */
  SDL_Rect dst; /* letterboxed dest in window pixels */
} host_t;

static host_t H;

/* Largest integer scale that fits; centre with black bars. */
static void layout_present(void) {
  int ww, wh;
  SDL_GetWindowSize(H.win, &ww, &wh);
  if (ww < 1) ww = 1;
  if (wh < 1) wh = 1;
  int sx = ww / FB_W;
  int sy = wh / FB_H;
  int s = sx < sy ? sx : sy;
  if (s < 1) s = 1;
  H.scale = s;
  H.dst.w = FB_W * s;
  H.dst.h = FB_H * s;
  H.dst.x = (ww - H.dst.w) / 2;
  H.dst.y = (wh - H.dst.h) / 2;
}

/* Window coords → integer 320×204 playfield (outside dest = clamp). */
static void map_mouse(int wx, int wy, int *ox, int *oy) {
  layout_present();
  int lx = wx - H.dst.x;
  int ly = wy - H.dst.y;
  if (H.scale < 1) H.scale = 1;
  *ox = lx / H.scale;
  *oy = ly / H.scale;
  if (*ox < 0) *ox = 0;
  if (*oy < 0) *oy = 0;
  if (*ox >= FB_W) *ox = FB_W - 1;
  if (*oy >= FB_H) *oy = FB_H - 1;
}

static float pad_axis(SDL_GameController *c, SDL_GameControllerAxis axis) {
  float v = (float)SDL_GameControllerGetAxis(c, axis) / 32767.f;
  if (v > 1.f) v = 1.f;
  if (v < -1.f) v = -1.f;
  float a = fabsf(v);
  if (a < PAD_DEADZONE) return 0.f;
  float s = (a - PAD_DEADZONE) / (1.f - PAD_DEADZONE);
  return (v < 0.f) ? -s : s;
}

static void open_pad_index(int index) {
  if (pad) return;
  if (!SDL_IsGameController(index)) return;
  pad = SDL_GameControllerOpen(index);
  if (pad) {
    const char *name = SDL_GameControllerName(pad);
    fprintf(stderr, "gamepad: %s\n", name ? name : "(unknown)");
  }
}

static void close_pad(void) {
  if (!pad) return;
  SDL_GameControllerClose(pad);
  pad = NULL;
  game_pad_move(&game, 0.f, 0.f);
  game_pad_aim(&game, 0.f, 0.f);
  game_pad_fire(&game, 0);
  game_pad_shield(&game, 0);
}

static void poll_gamepad(void) {
  if (!pad || replay_playing()) return;
  /* Left stick = move; right stick = aim (game fires from aim past deadzone). */
  game_pad_move(&game, pad_axis(pad, SDL_CONTROLLER_AXIS_LEFTX),
                pad_axis(pad, SDL_CONTROLLER_AXIS_LEFTY));
  float ax = pad_axis(pad, SDL_CONTROLLER_AXIS_RIGHTX);
  float ay = pad_axis(pad, SDL_CONTROLLER_AXIS_RIGHTY);
  game_pad_aim(&game, ax, ay);
  /* L/R triggers = shield drop only (game ignores outside placement window). */
  int shield = SDL_GameControllerGetAxis(pad, SDL_CONTROLLER_AXIS_TRIGGERLEFT) > 12000 ||
               SDL_GameControllerGetAxis(pad, SDL_CONTROLLER_AXIS_TRIGGERRIGHT) > 12000;
  game_pad_shield(&game, shield);
}

#ifdef __EMSCRIPTEN__
/* JS twin-stick / Start / replay → game (Module._msgorf_*) */
EMSCRIPTEN_KEEPALIVE void msgorf_pad_move(float x, float y) {
  if (!replay_playing()) game_pad_move(&game, x, y);
}
EMSCRIPTEN_KEEPALIVE void msgorf_pad_aim(float x, float y) {
  if (!replay_playing()) game_pad_aim(&game, x, y);
}
EMSCRIPTEN_KEEPALIVE void msgorf_pad_fire(int down) {
  if (!replay_playing()) game_pad_fire(&game, down);
}
EMSCRIPTEN_KEEPALIVE void msgorf_pad_shield(int down) {
  if (!replay_playing()) game_pad_shield(&game, down);
}
EMSCRIPTEN_KEEPALIVE void msgorf_pad_start(int players) { game_pad_start(&game, players); }
EMSCRIPTEN_KEEPALIVE int msgorf_get_mode(void) { return game_get_mode(&game); }
EMSCRIPTEN_KEEPALIVE int msgorf_get_score(void) { return game_get_score(&game); }
EMSCRIPTEN_KEEPALIVE int msgorf_replay_mode(void) { return (int)replay_mode(); }
EMSCRIPTEN_KEEPALIVE int msgorf_replay_ready(void) { return replay_ready(); }
EMSCRIPTEN_KEEPALIVE int msgorf_replay_len(void) { return (int)replay_blob_len(); }
EMSCRIPTEN_KEEPALIVE const uint8_t *msgorf_replay_ptr(void) { return replay_blob(); }
EMSCRIPTEN_KEEPALIVE void msgorf_set_build_id(const char *id) { replay_set_build_id(id); }
EMSCRIPTEN_KEEPALIVE int msgorf_replay_play(const uint8_t *data, int len) {
  if (!data || len <= 0) return 0;
  return game_start_replay(&game, data, (size_t)len);
}
EMSCRIPTEN_KEEPALIVE void msgorf_replay_stop(void) { game_stop_replay(&game); }
/* Copy recording into a JS-owned buffer (ptr from Module._malloc). */
EMSCRIPTEN_KEEPALIVE int msgorf_replay_copy(uint8_t *dst, int max) {
  const uint8_t *src = replay_blob();
  size_t n = replay_blob_len();
  if (!src || !dst || max < (int)n) return -1;
  memcpy(dst, src, n);
  return (int)n;
}
#endif

static void frame(void) {
  H.frame_start = SDL_GetPerformanceCounter();

  SDL_Event e;
  while (SDL_PollEvent(&e)) {
    if (e.type == SDL_QUIT) running = 0;
    else if (e.type == SDL_KEYDOWN) {
      if (e.key.keysym.scancode == SDL_SCANCODE_ESCAPE) running = 0;
      game_keydown(&game, (int)e.key.keysym.scancode);
    } else if (e.type == SDL_KEYUP) {
      game_keyup(&game, (int)e.key.keysym.scancode);
    } else if (e.type == SDL_MOUSEMOTION) {
      if (!replay_playing()) {
        int mx, my;
        map_mouse(e.motion.x, e.motion.y, &mx, &my);
        game_mouse(&game, mx, my, -1);
      }
    } else if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT) {
      if (!replay_playing()) {
        int mx, my;
        map_mouse(e.button.x, e.button.y, &mx, &my);
        game_mouse(&game, mx, my, 1);
      }
    } else if (e.type == SDL_MOUSEBUTTONUP && e.button.button == SDL_BUTTON_LEFT) {
      if (!replay_playing()) {
        int mx, my;
        map_mouse(e.button.x, e.button.y, &mx, &my);
        game_mouse(&game, mx, my, 0);
      }
    } else if (e.type == SDL_CONTROLLERDEVICEADDED) {
      open_pad_index(e.cdevice.which);
    } else if (e.type == SDL_CONTROLLERDEVICEREMOVED) {
      if (pad && e.cdevice.which == SDL_JoystickInstanceID(SDL_GameControllerGetJoystick(pad)))
        close_pad();
    } else if (e.type == SDL_CONTROLLERBUTTONDOWN) {
      if (e.cbutton.button == SDL_CONTROLLER_BUTTON_START ||
          e.cbutton.button == SDL_CONTROLLER_BUTTON_A)
        game_pad_start(&game, 1); /* same as keyboard 1 / web Start */
    } else if (e.type == SDL_WINDOWEVENT &&
               (e.window.event == SDL_WINDOWEVENT_SIZE_CHANGED ||
                e.window.event == SDL_WINDOWEVENT_RESIZED)) {
      layout_present();
    }
  }

  poll_gamepad();
  /* Fixed 60Hz tick — one sim step per paced frame (mines flash every tick). */
  game_update(&game, SIM_DT);
  game_render(&game);

  layout_present();
  SDL_UpdateTexture(H.tex, NULL, fb, FB_W * 3);
  SDL_SetRenderDrawColor(H.ren, 0, 0, 0, 255);
  SDL_RenderClear(H.ren);
  /* Exact integer scale: each buffer pixel → scale×scale window pixels. */
  SDL_RenderCopy(H.ren, H.tex, NULL, &H.dst);
  SDL_RenderPresent(H.ren);

#ifndef __EMSCRIPTEN__
  /* Pace to 60Hz when vsync is off or display is faster than 60. */
  {
    Uint64 freq = SDL_GetPerformanceFrequency();
    Uint64 elapsed = SDL_GetPerformanceCounter() - H.frame_start;
    Uint64 budget = freq / (Uint64)SIM_HZ;
    if (elapsed < budget) {
      double remain_s = (double)(budget - elapsed) / (double)freq;
      if (remain_s > 0.001)
        SDL_Delay((Uint32)(remain_s * 1000.0));
      /* Busy-wait the last ~1ms for tighter cadence. */
      while (SDL_GetPerformanceCounter() - H.frame_start < budget) {
      }
    }
  }
#endif
  H.last = SDL_GetPerformanceCounter();
}

int main(int argc, char **argv) {
  (void)argc;
  (void)argv;

  /* Must be set before renderer/texture creation for nearest filtering. */
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
  SDL_SetHint(SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS, "1");
  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER | SDL_INIT_AUDIO | SDL_INIT_GAMECONTROLLER) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }
  if (sound_init() != 0) {
    fprintf(stderr, "sound_init failed (continuing without audio)\n");
  }

  H.win = SDL_CreateWindow(
      "Ms. Gorf (GUESS SDL) — 320x204 integer scale", SDL_WINDOWPOS_CENTERED,
      SDL_WINDOWPOS_CENTERED, FB_W * VIEW_SCALE, FB_H * VIEW_SCALE,
      SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);
  if (!H.win) {
    fprintf(stderr, "window: %s\n", SDL_GetError());
    return 1;
  }

  /* No vsync — we pace to a fixed 60Hz tick ourselves (120Hz panels would
   * otherwise double the mine flash rate). */
  H.ren = SDL_CreateRenderer(H.win, -1, SDL_RENDERER_ACCELERATED);
  if (!H.ren) H.ren = SDL_CreateRenderer(H.win, -1, 0);
  if (!H.ren) {
    fprintf(stderr, "renderer: %s\n", SDL_GetError());
    return 1;
  }
  /* No RenderSetLogicalSize — that allows non-integer scale into the window. */
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");

  H.tex = SDL_CreateTexture(H.ren, SDL_PIXELFORMAT_RGB24, SDL_TEXTUREACCESS_STREAMING, FB_W, FB_H);
  if (!H.tex) {
    fprintf(stderr, "texture: %s\n", SDL_GetError());
    return 1;
  }
#if SDL_VERSION_ATLEAST(2, 0, 12)
  SDL_SetTextureScaleMode(H.tex, SDL_ScaleModeNearest);
#endif

  for (int i = 0; i < SDL_NumJoysticks(); i++) open_pad_index(i);

  layout_present();
  game_init(&game, fb);
  H.last = SDL_GetPerformanceCounter();

#ifdef __EMSCRIPTEN__
  emscripten_set_main_loop(frame, SIM_HZ, 1);
#else
  while (running) frame();
#endif

  close_pad();
  SDL_DestroyTexture(H.tex);
  SDL_DestroyRenderer(H.ren);
  SDL_DestroyWindow(H.win);
  sound_quit();
  SDL_Quit();
  return 0;
}
