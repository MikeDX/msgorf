/*
 * Source-faithful pattern harness (not a game).
 * Authentic pixels from disk pack and/or XC.PATTERNS decode.
 * WASD moves ship; Gorf drifts; overlay collision counted.
 */
#include "terse_rt.h"
#include "assets_gen.h"
#include "xc_map.h"

#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef FRAME_W
#define FRAME_W 240
#endif
#ifndef FRAME_H
#define FRAME_H 352
#endif
#define SCALE 2

static const uint8_t PAL[4][3] = {
    {0, 0, 0},
    {40, 90, 220},
    {230, 50, 40},
    {245, 245, 245},
};

static const terse_asset_t *find_asset(const char *name) {
  for (int i = 0; i < TERSE_ASSET_COUNT; i++) {
    if (strcmp(terse_assets[i]->name, name) == 0) return terse_assets[i];
  }
  return NULL;
}

int main(int argc, char **argv) {
  int use_xc = 0;
  const char *rom_path = NULL;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--xc") && i + 1 < argc) {
      use_xc = 1;
      rom_path = argv[++i];
    }
  }

  const terse_asset_t *ship_src = find_asset("PLY1-P");
  const terse_asset_t *gorf_src = find_asset("GORF-PAT");
  if (!ship_src || !gorf_src) {
    fprintf(stderr, "missing packed assets\n");
    return 1;
  }

  const uint8_t *ship_pix = ship_src->pix;
  const uint8_t *gorf_pix = gorf_src->pix;
  int ship_w = ship_src->w, ship_h = ship_src->h;
  int gorf_w = gorf_src->w, gorf_h = gorf_src->h;
  const char *pix_source = "source pack (assets.json)";

  uint8_t *xc_mem = NULL;
  xc_pattern_t xc_ship = {0}, xc_gorf = {0};
  if (use_xc && rom_path) {
    xc_mem = xc_load_64k(rom_path);
    if (!xc_mem) {
      fprintf(stderr, "failed to load XC image %s (using source pack)\n", rom_path);
    } else if (xc_decode_simple(xc_mem, XC_ATBL_PLY1, &xc_ship) == 0 &&
               xc_decode_simple(xc_mem, XC_ATBL_GORF, &xc_gorf) == 0) {
      ship_pix = xc_ship.pix;
      ship_w = xc_ship.w;
      ship_h = xc_ship.h;
      gorf_pix = xc_gorf.pix;
      gorf_w = xc_gorf.w;
      gorf_h = xc_gorf.h;
      pix_source = "XC.PATTERNS decode @ ROMSTART";
      printf("XC decode OK: PLY1-P %dx%d @ ATBL[1], GORF-PAT %dx%d @ ATBL[9]\n",
             ship_w, ship_h, gorf_w, gorf_h);
    } else {
      fprintf(stderr, "XC decode failed; falling back to source pack\n");
    }
  }

  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }

  SDL_Window *win = SDL_CreateWindow(
      "Ms. Gorf TERSE harness (patterns only)", SDL_WINDOWPOS_CENTERED,
      SDL_WINDOWPOS_CENTERED, FRAME_W * SCALE, FRAME_H * SCALE, 0);
  if (!win) {
    fprintf(stderr, "window: %s\n", SDL_GetError());
    return 1;
  }
  SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
  SDL_Texture *tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_RGB24,
                                       SDL_TEXTUREACCESS_STREAMING, FRAME_W,
                                       FRAME_H);

  terse_frame_t fr;
  terse_frame_init(&fr, FRAME_W, FRAME_H);
  uint8_t *rgb = malloc((size_t)FRAME_W * FRAME_H * 3);

  float ship_x = (float)(FRAME_W / 2 - ship_w / 2);
  float ship_y = (float)(FRAME_H - ship_h - 24);
  float gorf_x = 40.0f, gorf_y = 60.0f, gorf_vx = 0.6f;
  int running = 1;
  int total_hits = 0;
  Uint32 last = SDL_GetTicks();

  printf("Controls: WASD move ship · Esc quit\n");
  printf("Pixels: %s\n", pix_source);
  printf("Frame %dx%d (harness default; see docs/findings/display.md)\n", FRAME_W,
         FRAME_H);

  while (running) {
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) running = 0;
      if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_ESCAPE) running = 0;
    }
    const Uint8 *k = SDL_GetKeyboardState(NULL);
    float sp = 1.8f;
    if (k[SDL_SCANCODE_A] || k[SDL_SCANCODE_LEFT]) ship_x -= sp;
    if (k[SDL_SCANCODE_D] || k[SDL_SCANCODE_RIGHT]) ship_x += sp;
    if (k[SDL_SCANCODE_W] || k[SDL_SCANCODE_UP]) ship_y -= sp;
    if (k[SDL_SCANCODE_S] || k[SDL_SCANCODE_DOWN]) ship_y += sp;
    if (ship_x < 0) ship_x = 0;
    if (ship_y < 0) ship_y = 0;
    if (ship_x > FRAME_W - ship_w) ship_x = (float)(FRAME_W - ship_w);
    if (ship_y > FRAME_H - ship_h) ship_y = (float)(FRAME_H - ship_h);

    gorf_x += gorf_vx;
    if (gorf_x < 8 || gorf_x > FRAME_W - gorf_w - 8) gorf_vx = -gorf_vx;
    gorf_y += 0.15f;
    if (gorf_y > FRAME_H / 2) gorf_y = 40.0f;

    terse_frame_clear(&fr);
    terse_blit_u8(&fr, gorf_pix, gorf_w, gorf_h, (int)gorf_x, (int)gorf_y, 2);
    int h2 = terse_blit_u8(&fr, ship_pix, ship_w, ship_h, (int)ship_x,
                           (int)ship_y, 1);
    if (h2 > 0) {
      total_hits += h2;
      ship_y += 4;
    }

    terse_frame_to_rgb24(&fr, rgb, PAL);
    SDL_UpdateTexture(tex, NULL, rgb, FRAME_W * 3);
    SDL_RenderClear(ren);
    SDL_RenderCopy(ren, tex, NULL, NULL);
    SDL_RenderPresent(ren);

    Uint32 now = SDL_GetTicks();
    if (now - last > 500) {
      char title[192];
      snprintf(title, sizeof title, "Ms. Gorf harness | hits=%d | %s", total_hits,
               pix_source);
      SDL_SetWindowTitle(win, title);
      last = now;
    }
    SDL_Delay(16);
  }

  xc_pattern_free(&xc_ship);
  xc_pattern_free(&xc_gorf);
  free(xc_mem);
  free(rgb);
  terse_frame_free(&fr);
  SDL_DestroyTexture(tex);
  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
