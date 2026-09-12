/*
 * Pattern decode/blit validator — NOT Ms. Gorf gameplay.
 *
 * Faithful: pixel bytes from XC.PATTERNS (or source pack matching disk art),
 *           write-overlay collision count (Jamie's write-cycle model).
 * Not faithful / lab-only: window size guess, display palette, keyboard,
 *           any motion or layout. Dual-stick / missions / HUD are absent
 *           because XC.LOGIC is missing (see docs/findings/).
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

/* Lab greyscale for digits 0–3 — not claimed cabinet colors */
static const uint8_t PAL[4][3] = {
    {0, 0, 0},
    {85, 85, 85},
    {170, 170, 170},
    {255, 255, 255},
};

typedef struct {
  const char *name;
  const uint8_t *pix;
  int w, h;
  int owned; /* 1 if pix needs xc_pattern_free */
  xc_pattern_t xc;
} slot_t;

#define MAX_SLOTS 24

static void blit_atlas(terse_frame_t *fr, slot_t *slots, int n) {
  int x = 4, y = 4, row_h = 0;
  for (int i = 0; i < n; i++) {
    if (x + slots[i].w + 4 > fr->w) {
      x = 4;
      y += row_h + 4;
      row_h = 0;
    }
    if (y + slots[i].h > fr->h) break;
    terse_blit_u8(fr, slots[i].pix, slots[i].w, slots[i].h, x, y,
                  (uint16_t)(i + 1));
    x += slots[i].w + 4;
    if (slots[i].h > row_h) row_h = slots[i].h;
  }
}

int main(int argc, char **argv) {
  int use_xc = 0;
  int probe = 0;
  const char *rom_path = NULL;
  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--xc") && i + 1 < argc) {
      use_xc = 1;
      rom_path = argv[++i];
    } else if (!strcmp(argv[i], "--probe")) {
      probe = 1;
    }
  }

  slot_t slots[MAX_SLOTS];
  int nslots = 0;
  uint8_t *xc_mem = NULL;
  const char *pix_source = "source pack (assets.json / disk PATTERN art)";

  /* Prefer XC decode for every simple ATBL slot we can read */
  if (use_xc && rom_path) {
    xc_mem = xc_load_64k(rom_path);
    if (!xc_mem) {
      fprintf(stderr, "failed to load %s\n", rom_path);
    } else {
      static const int indices[] = {1, 2, 3, 4, 5, 9, 10, 13, 14, 15, 16, 17, 18, 19};
      static const char *names[] = {
          "PLY1-P", "PLY2-P", "SBASE",  "P1UP",   "P2UP",   "GORF-PAT", "LAZON",
          "SHLD-P", "MITE-P", "TRION-P", "DEB-P",  "HK-P",   "GB-P",     "GRD-P"};
      for (size_t i = 0; i < sizeof indices / sizeof indices[0] && nslots < MAX_SLOTS;
           i++) {
        xc_pattern_t p;
        if (xc_decode_simple(xc_mem, indices[i], &p) != 0) continue;
        slots[nslots].name = names[i];
        slots[nslots].pix = p.pix;
        slots[nslots].w = p.w;
        slots[nslots].h = p.h;
        slots[nslots].owned = 1;
        slots[nslots].xc = p;
        nslots++;
      }
      if (nslots > 0) pix_source = "XC.PATTERNS decode @ ROMSTART (authentic object)";
    }
  }

  if (nslots == 0) {
    for (int i = 0; i < TERSE_ASSET_COUNT && nslots < MAX_SLOTS; i++) {
      const terse_asset_t *a = terse_assets[i];
      slots[nslots].name = a->name;
      slots[nslots].pix = a->pix;
      slots[nslots].w = a->w;
      slots[nslots].h = a->h;
      slots[nslots].owned = 0;
      nslots++;
    }
  }

  if (nslots == 0) {
    fprintf(stderr, "no patterns loaded\n");
    return 1;
  }

  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }

  SDL_Window *win = SDL_CreateWindow(
      "Ms. Gorf pattern validator (not a game)", SDL_WINDOWPOS_CENTERED,
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

  /* Probe mode: two authentic sprites; arrows move A over B for collision ABI */
  int ai = 0, bi = (nslots > 1) ? 1 : 0;
  for (int i = 0; i < nslots; i++) {
    if (!strcmp(slots[i].name, "PLY1-P")) ai = i;
    if (!strcmp(slots[i].name, "GORF-PAT")) bi = i;
  }
  int ax = FRAME_W / 2 - slots[ai].w / 2;
  int ay = FRAME_H - slots[ai].h - 16;
  int bx = 24, by = 48;
  int hits = 0;
  int running = 1;

  printf("=== pattern validator (not Ms. Gorf) ===\n");
  printf("Pixels: %s\n", pix_source);
  printf("Frame %dx%d = lab guess only (docs/findings/display.md)\n", FRAME_W,
         FRAME_H);
  printf("Palette: lab greyscale (cabinet colors unknown)\n");
  printf("Loaded %d pattern(s):", nslots);
  for (int i = 0; i < nslots; i++)
    printf(" %s(%dx%d)", slots[i].name, slots[i].w, slots[i].h);
  printf("\n");
  if (probe) {
    printf("PROBE: arrows move %s over %s; overlay hits counted (write-cycle model)\n",
           slots[ai].name, slots[bi].name);
    printf("       This motion is lab input — not source game logic.\n");
  } else {
    printf("Keys: Esc quit · --probe for overlay-collision ABI test\n");
  }
  printf("Missing: XC.LOGIC / missions / dual-stick (see professionalmagic.com/gorf notes)\n");

  while (running) {
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) running = 0;
      if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_ESCAPE) running = 0;
    }
    if (probe) {
      const Uint8 *k = SDL_GetKeyboardState(NULL);
      if (k[SDL_SCANCODE_LEFT] || k[SDL_SCANCODE_A]) ax--;
      if (k[SDL_SCANCODE_RIGHT] || k[SDL_SCANCODE_D]) ax++;
      if (k[SDL_SCANCODE_UP] || k[SDL_SCANCODE_W]) ay--;
      if (k[SDL_SCANCODE_DOWN] || k[SDL_SCANCODE_S]) ay++;
      if (ax < 0) ax = 0;
      if (ay < 0) ay = 0;
      if (ax > FRAME_W - slots[ai].w) ax = FRAME_W - slots[ai].w;
      if (ay > FRAME_H - slots[ai].h) ay = FRAME_H - slots[ai].h;
    }

    terse_frame_clear(&fr);
    if (probe) {
      terse_blit_u8(&fr, slots[bi].pix, slots[bi].w, slots[bi].h, bx, by, 2);
      hits += terse_blit_u8(&fr, slots[ai].pix, slots[ai].w, slots[ai].h, ax, ay,
                            1);
    } else {
      blit_atlas(&fr, slots, nslots);
    }

    terse_frame_to_rgb24(&fr, rgb, PAL);
    SDL_UpdateTexture(tex, NULL, rgb, FRAME_W * 3);
    SDL_RenderClear(ren);
    SDL_RenderCopy(ren, tex, NULL, NULL);
    SDL_RenderPresent(ren);

    char title[200];
    if (probe)
      snprintf(title, sizeof title, "probe hits=%d | %s", hits, pix_source);
    else
      snprintf(title, sizeof title, "atlas %d pats | %s", nslots, pix_source);
    SDL_SetWindowTitle(win, title);
    SDL_Delay(16);
  }

  for (int i = 0; i < nslots; i++) {
    if (slots[i].owned) xc_pattern_free(&slots[i].xc);
  }
  free(xc_mem);
  free(rgb);
  terse_frame_free(&fr);
  SDL_DestroyTexture(tex);
  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
