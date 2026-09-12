/*
 * Pattern decode/blit validator — NOT Ms. Gorf gameplay.
 *
 * Shows authentic patterns with header-derived colours and cycles
 * multi-frame sequences from disk (CLONE / KAMI / SMINE / BANG).
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

static void blit_with_pal(terse_frame_t *fr, const terse_asset_t *a, int x, int y,
                          uint16_t owner) {
  terse_blit_u8(fr, a->pix, a->w, a->h, x, y, owner);
}

/* Composite atlas using each sprite's own palette into RGB (per-sprite bake). */
static void atlas_to_rgb(uint8_t *rgb, int fw, int fh,
                         const terse_asset_t *const *sprites, int n,
                         int anim_phase) {
  memset(rgb, 0, (size_t)fw * fh * 3);
  int x = 4, y = 4, row_h = 0;
  for (int i = 0; i < n; i++) {
    const terse_asset_t *a = sprites[i];
    /* If this asset is part of an anim group sharing a prefix slot, skip —
       we pass already-selected frames. */
    if (x + a->w + 4 > fw) {
      x = 4;
      y += row_h + 4;
      row_h = 0;
    }
    if (y + a->h > fh) break;
    for (int j = 0; j < a->h; j++) {
      for (int i2 = 0; i2 < a->w; i2++) {
        uint8_t v = a->pix[j * a->w + i2] & 3;
        if (!v) continue;
        int xx = x + i2, yy = y + j;
        if (xx < 0 || yy < 0 || xx >= fw || yy >= fh) continue;
        size_t idx = ((size_t)yy * (size_t)fw + (size_t)xx) * 3;
        rgb[idx + 0] = a->pal[v][0];
        rgb[idx + 1] = a->pal[v][1];
        rgb[idx + 2] = a->pal[v][2];
      }
    }
    x += a->w + 4;
    if (a->h > row_h) row_h = a->h;
  }
  (void)anim_phase;
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

  /* Build display list: one frame from each anim + leftover singles */
  const terse_asset_t *show[64];
  int nshow = 0;
  int anim_frame[16];
  memset(anim_frame, 0, sizeof anim_frame);

  for (int i = 0; i < TERSE_ANIM_COUNT && nshow < 64; i++) {
    show[nshow++] = terse_anims[i]->frames[0];
  }
  /* Add a few static notables not in anims */
  const char *statics[] = {"GORF-PAT", "PLY1-P", "LAZON", "SHLD-P", "TRION-P",
                           "DEB-P", "HK-P", "GB-P", "GRD-P", NULL};
  for (int s = 0; statics[s]; s++) {
    for (int i = 0; i < TERSE_ASSET_COUNT; i++) {
      if (!strcmp(terse_assets[i]->name, statics[s])) {
        int dup = 0;
        for (int j = 0; j < nshow; j++)
          if (show[j] == terse_assets[i]) dup = 1;
        if (!dup && nshow < 64) show[nshow++] = terse_assets[i];
        break;
      }
    }
  }

  uint8_t *xc_mem = NULL;
  if (use_xc && rom_path) {
    xc_mem = xc_load_64k(rom_path);
    if (xc_mem)
      printf("XC image loaded (atlas still uses source-pack frames+palettes)\n");
  }

  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }
  SDL_Window *win = SDL_CreateWindow(
      "Ms. Gorf pattern animator (not a game)", SDL_WINDOWPOS_CENTERED,
      SDL_WINDOWPOS_CENTERED, FRAME_W * SCALE, FRAME_H * SCALE, 0);
  SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
  SDL_Texture *tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_RGB24,
                                       SDL_TEXTUREACCESS_STREAMING, FRAME_W,
                                       FRAME_H);
  uint8_t *rgb = malloc((size_t)FRAME_W * FRAME_H * 3);
  terse_frame_t fr;
  terse_frame_init(&fr, FRAME_W, FRAME_H);

  printf("=== pattern animator (not Ms. Gorf) ===\n");
  printf("Colours: shared 0=black 1=yellow 2=blue 3=red (lab hypothesis)\n");
  printf("Anims: %d sequences · Esc quit", TERSE_ANIM_COUNT);
  if (probe) printf(" · --probe unused in atlas mode");
  printf("\n");

  int running = 1;
  Uint32 last = SDL_GetTicks();
  int phase = 0;

  while (running) {
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) running = 0;
      if (e.type == SDL_KEYDOWN && e.key.keysym.sym == SDLK_ESCAPE) running = 0;
    }

    Uint32 now = SDL_GetTicks();
    if (now - last > 120) {
      phase++;
      last = now;
      /* advance each animation slot */
      nshow = 0;
      for (int i = 0; i < TERSE_ANIM_COUNT && nshow < 64; i++) {
        const terse_anim_t *an = terse_anims[i];
        anim_frame[i] = (anim_frame[i] + 1) % an->count;
        show[nshow++] = an->frames[anim_frame[i]];
      }
      for (int s = 0; statics[s]; s++) {
        for (int i = 0; i < TERSE_ASSET_COUNT; i++) {
          if (!strcmp(terse_assets[i]->name, statics[s])) {
            int dup = 0;
            for (int j = 0; j < nshow; j++)
              if (show[j] == terse_assets[i]) dup = 1;
            if (!dup && nshow < 64) show[nshow++] = terse_assets[i];
            break;
          }
        }
      }
    }

    atlas_to_rgb(rgb, FRAME_W, FRAME_H, show, nshow, phase);
    SDL_UpdateTexture(tex, NULL, rgb, FRAME_W * 3);
    SDL_RenderClear(ren);
    SDL_RenderCopy(ren, tex, NULL, NULL);
    SDL_RenderPresent(ren);
    SDL_Delay(16);
  }

  free(xc_mem);
  free(rgb);
  terse_frame_free(&fr);
  SDL_DestroyTexture(tex);
  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  (void)blit_with_pal;
  (void)probe;
  return 0;
}
