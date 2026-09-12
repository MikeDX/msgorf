/* GUESS SDL host — 320×204 integer buffer, nearest-neighbour present.
 * Native: SDL2. Web: emscripten + USE_SDL=2. */
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

static void map_mouse(SDL_Window *win, int wx, int wy, int *ox, int *oy) {
  int ww, wh;
  SDL_GetWindowSize(win, &ww, &wh);
  if (ww < 1) ww = 1;
  if (wh < 1) wh = 1;
  *ox = (int)((float)wx / (float)ww * FB_W);
  *oy = (int)((float)wy / (float)wh * FB_H);
  if (*ox < 0) *ox = 0;
  if (*oy < 0) *oy = 0;
  if (*ox >= FB_W) *ox = FB_W - 1;
  if (*oy >= FB_H) *oy = FB_H - 1;
}

typedef struct {
  SDL_Window *win;
  SDL_Renderer *ren;
  SDL_Texture *tex;
  Uint64 last;
} host_t;

static host_t H;

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
      map_mouse(H.win, e.motion.x, e.motion.y, &mx, &my);
      game_mouse(&game, mx, my, -1);
    } else if (e.type == SDL_MOUSEBUTTONDOWN && e.button.button == SDL_BUTTON_LEFT) {
      int mx, my;
      map_mouse(H.win, e.button.x, e.button.y, &mx, &my);
      game_mouse(&game, mx, my, 1);
    } else if (e.type == SDL_MOUSEBUTTONUP && e.button.button == SDL_BUTTON_LEFT) {
      int mx, my;
      map_mouse(H.win, e.button.x, e.button.y, &mx, &my);
      game_mouse(&game, mx, my, 0);
    }
  }

  game_update(&game, dt);
  game_render(&game);

  SDL_UpdateTexture(H.tex, NULL, fb, FB_W * 3);
  SDL_SetRenderDrawColor(H.ren, 0, 0, 0, 255);
  SDL_RenderClear(H.ren);
  SDL_RenderCopy(H.ren, H.tex, NULL, NULL);
  SDL_RenderPresent(H.ren);
}

int main(int argc, char **argv) {
  (void)argc;
  (void)argv;

  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
  if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }

  H.win = SDL_CreateWindow(
      "Ms. Gorf (GUESS SDL) — 320x204", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
      FB_W * VIEW_SCALE, FB_H * VIEW_SCALE, SDL_WINDOW_SHOWN | SDL_WINDOW_RESIZABLE);
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
  SDL_RenderSetLogicalSize(H.ren, FB_W, FB_H);
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");

  H.tex = SDL_CreateTexture(H.ren, SDL_PIXELFORMAT_RGB24, SDL_TEXTUREACCESS_STREAMING, FB_W, FB_H);
  if (!H.tex) {
    fprintf(stderr, "texture: %s\n", SDL_GetError());
    return 1;
  }

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
