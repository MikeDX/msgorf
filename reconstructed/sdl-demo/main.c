/* GUESS SDL host — simulate & paint only on 320×204, then integer-scale to window.
 * Never present fractional buffer→window mapping (that looks like “scaled pixel” motion). */
#include "game.h"

#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>

#ifndef VIEW_SCALE
#define VIEW_SCALE 3
#endif

static uint8_t fb[FB_W * FB_H * 3];
static game_t game;
static int running = 1;

#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

typedef struct {
  SDL_Window *win;
  SDL_Renderer *ren;
  SDL_Texture *tex;
  Uint64 last;
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

#ifdef __EMSCRIPTEN__
#include <emscripten.h>

/* JS twin-stick / Start → game (Module._msgorf_*) */
EMSCRIPTEN_KEEPALIVE void msgorf_pad_move(float x, float y) { game_pad_move(&game, x, y); }
EMSCRIPTEN_KEEPALIVE void msgorf_pad_aim(float x, float y) { game_pad_aim(&game, x, y); }
EMSCRIPTEN_KEEPALIVE void msgorf_pad_fire(int down) { game_pad_fire(&game, down); }
EMSCRIPTEN_KEEPALIVE void msgorf_pad_start(int players) { game_pad_start(&game, players); }
EMSCRIPTEN_KEEPALIVE int msgorf_get_mode(void) { return game_get_mode(&game); }
#endif

static void frame(void) {
  Uint64 now = SDL_GetPerformanceCounter();
  float dt = (float)(now - H.last) / (float)SDL_GetPerformanceFrequency();
  H.last = now;

  SDL_Event e;
  while (SDL_PollEvent(&e)) {
    if (e.type == SDL_QUIT) running = 0;
    else if (e.type == SDL_KEYDOWN) {
      if (e.key.keysym.scancode == SDL_SCANCODE_ESCAPE) running = 0;
      game_keydown(&game, (int)e.key.keysym.scancode);
    } else if (e.type == SDL_KEYUP) {
      game_keyup(&game, (int)e.key.keysym.scancode);
    } else if (e.type == SDL_MOUSEMOTION) {
      int mx, my;
      map_mouse(e.motion.x, e.motion.y, &mx, &my);
      game_mouse(&game, mx, my, -1);
    } else if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT) {
      int mx, my;
      map_mouse(e.button.x, e.button.y, &mx, &my);
      game_mouse(&game, mx, my, 1);
    } else if (e.type == SDL_MOUSEBUTTONUP && e.button.button == SDL_BUTTON_LEFT) {
      int mx, my;
      map_mouse(e.button.x, e.button.y, &mx, &my);
      game_mouse(&game, mx, my, 0);
    } else if (e.type == SDL_WINDOWEVENT &&
               (e.window.event == SDL_WINDOWEVENT_SIZE_CHANGED ||
                e.window.event == SDL_WINDOWEVENT_RESIZED)) {
      layout_present();
    }
  }

  game_update(&game, dt);
  game_render(&game);

  layout_present();
  SDL_UpdateTexture(H.tex, NULL, fb, FB_W * 3);
  SDL_SetRenderDrawColor(H.ren, 0, 0, 0, 255);
  SDL_RenderClear(H.ren);
  /* Exact integer scale: each buffer pixel → scale×scale window pixels. */
  SDL_RenderCopy(H.ren, H.tex, NULL, &H.dst);
  SDL_RenderPresent(H.ren);
}

int main(int argc, char **argv) {
  (void)argc;
  (void)argv;

  /* Must be set before renderer/texture creation for nearest filtering. */
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }

  H.win = SDL_CreateWindow(
      "Ms. Gorf (GUESS SDL) — 320x204 integer scale", SDL_WINDOWPOS_CENTERED,
      SDL_WINDOWPOS_CENTERED, FB_W * VIEW_SCALE, FB_H * VIEW_SCALE,
      SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);
  if (!H.win) {
    fprintf(stderr, "window: %s\n", SDL_GetError());
    return 1;
  }

  H.ren = SDL_CreateRenderer(H.win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
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

  layout_present();
  game_init(&game, fb);
  H.last = SDL_GetPerformanceCounter();

#ifdef __EMSCRIPTEN__
  emscripten_set_main_loop(frame, 0, 1);
#else
  while (running) frame();
#endif

  SDL_DestroyTexture(H.tex);
  SDL_DestroyRenderer(H.ren);
  SDL_DestroyWindow(H.win);
  SDL_Quit();
  return 0;
}
