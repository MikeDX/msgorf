/*
 * Pattern animator — NOT Ms. Gorf gameplay.
 *
 * One sequence at a time, centred in a fixed cell (max frame w×h) so
 * CLONE / SMINE size changes do not jump the layout.
 * Left/Right = prev/next sequence · Space = pause · Esc = quit
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
#define SCALE 3

typedef struct {
  const char *label;
  int count;
  const terse_asset_t *const *frames; /* NULL => single */
  const terse_asset_t *single;
  int cell_w, cell_h;
} seq_t;

#define MAX_SEQ 48

static void seq_bounds(seq_t *s) {
  int mw = 1, mh = 1;
  if (s->frames) {
    for (int i = 0; i < s->count; i++) {
      if (s->frames[i]->w > mw) mw = s->frames[i]->w;
      if (s->frames[i]->h > mh) mh = s->frames[i]->h;
    }
  } else if (s->single) {
    mw = s->single->w;
    mh = s->single->h;
  }
  s->cell_w = mw;
  s->cell_h = mh;
}

static const terse_asset_t *seq_frame(const seq_t *s, int fi) {
  if (s->frames) return s->frames[fi % s->count];
  return s->single;
}

static void blit_centered(uint8_t *rgb, int fw, int fh, const terse_asset_t *a,
                          int cell_w, int cell_h, int ox, int oy) {
  int x0 = ox + (cell_w - a->w) / 2;
  int y0 = oy + (cell_h - a->h) / 2;
  for (int j = 0; j < a->h; j++) {
    for (int i = 0; i < a->w; i++) {
      uint8_t v = a->pix[j * a->w + i] & 3;
      if (!v) continue;
      int xx = x0 + i, yy = y0 + j;
      if (xx < 0 || yy < 0 || xx >= fw || yy >= fh) continue;
      size_t idx = ((size_t)yy * (size_t)fw + (size_t)xx) * 3;
      rgb[idx + 0] = a->pal[v][0];
      rgb[idx + 1] = a->pal[v][1];
      rgb[idx + 2] = a->pal[v][2];
    }
  }
}

static void draw_cell_border(uint8_t *rgb, int fw, int fh, int ox, int oy,
                             int cw, int ch) {
  uint8_t c = 40;
  for (int x = ox; x < ox + cw && x < fw; x++) {
    if (oy >= 0 && oy < fh) {
      size_t i = ((size_t)oy * fw + x) * 3;
      rgb[i] = rgb[i + 1] = rgb[i + 2] = c;
    }
    int yb = oy + ch - 1;
    if (yb >= 0 && yb < fh) {
      size_t i = ((size_t)yb * fw + x) * 3;
      rgb[i] = rgb[i + 1] = rgb[i + 2] = c;
    }
  }
  for (int y = oy; y < oy + ch && y < fh; y++) {
    if (ox >= 0 && ox < fw) {
      size_t i = ((size_t)y * fw + ox) * 3;
      rgb[i] = rgb[i + 1] = rgb[i + 2] = c;
    }
    int xr = ox + cw - 1;
    if (xr >= 0 && xr < fw) {
      size_t i = ((size_t)y * fw + xr) * 3;
      rgb[i] = rgb[i + 1] = rgb[i + 2] = c;
    }
  }
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

  seq_t seqs[MAX_SEQ];
  int nseq = 0;
  for (int i = 0; i < TERSE_ANIM_COUNT && nseq < MAX_SEQ; i++) {
    seqs[nseq].label = terse_anims[i]->name;
    seqs[nseq].count = terse_anims[i]->count;
    seqs[nseq].frames = terse_anims[i]->frames;
    seqs[nseq].single = NULL;
    seq_bounds(&seqs[nseq]);
    nseq++;
  }
  const char *statics[] = {"GORF-PAT", "PLY1-P", "PLY2-P", "LAZON", "SHLD-P",
                           "TRION-P",  "DEB-P",  "HK-P",   "GB-P",  "GRD-P",
                           "SBASE",    "P1UP",   "P2UP",   NULL};
  for (int s = 0; statics[s] && nseq < MAX_SEQ; s++) {
    for (int i = 0; i < TERSE_ASSET_COUNT; i++) {
      if (strcmp(terse_assets[i]->name, statics[s])) continue;
      seqs[nseq].label = terse_assets[i]->name;
      seqs[nseq].count = 1;
      seqs[nseq].frames = NULL;
      seqs[nseq].single = terse_assets[i];
      seq_bounds(&seqs[nseq]);
      nseq++;
      break;
    }
  }

  uint8_t *xc_mem = NULL;
  if (use_xc && rom_path) {
    xc_mem = xc_load_64k(rom_path);
    if (xc_mem) printf("XC image loaded (display uses source pack)\n");
  }

  if (SDL_Init(SDL_INIT_VIDEO) != 0) {
    fprintf(stderr, "SDL_Init: %s\n", SDL_GetError());
    return 1;
  }
  SDL_Window *win = SDL_CreateWindow(
      "Ms. Gorf patterns", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
      FRAME_W * SCALE, FRAME_H * SCALE, 0);
  SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED);
  SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "0");
  SDL_Texture *tex = SDL_CreateTexture(ren, SDL_PIXELFORMAT_RGB24,
                                       SDL_TEXTUREACCESS_STREAMING, FRAME_W,
                                       FRAME_H);
  uint8_t *rgb = malloc((size_t)FRAME_W * FRAME_H * 3);

  printf("=== pattern animator (not Ms. Gorf) ===\n");
  printf("Left/Right  previous / next sequence\n");
  printf("Space       pause/resume animation\n");
  printf("[ / ]       slower / faster\n");
  printf("Esc         quit\n");
  printf("Palette: 0=black 1=yellow 2=blue 3=red\n");

  int sel = 0;
  int fi = 0;
  int paused = 0;
  int period_ms = 140;
  int running = 1;
  Uint32 last = SDL_GetTicks();

  while (running) {
    SDL_Event e;
    while (SDL_PollEvent(&e)) {
      if (e.type == SDL_QUIT) running = 0;
      if (e.type != SDL_KEYDOWN) continue;
      switch (e.key.keysym.sym) {
        case SDLK_ESCAPE:
          running = 0;
          break;
        case SDLK_LEFT:
        case SDLK_a:
          sel = (sel + nseq - 1) % nseq;
          fi = 0;
          break;
        case SDLK_RIGHT:
        case SDLK_d:
          sel = (sel + 1) % nseq;
          fi = 0;
          break;
        case SDLK_SPACE:
          paused = !paused;
          break;
        case SDLK_LEFTBRACKET:
          if (period_ms < 400) period_ms += 20;
          break;
        case SDLK_RIGHTBRACKET:
          if (period_ms > 40) period_ms -= 20;
          break;
        default:
          break;
      }
    }

    Uint32 now = SDL_GetTicks();
    if (!paused && seqs[sel].count > 1 && now - last >= (Uint32)period_ms) {
      fi = (fi + 1) % seqs[sel].count;
      last = now;
    }

    memset(rgb, 0, (size_t)FRAME_W * FRAME_H * 3);
    seq_t *s = &seqs[sel];
    const terse_asset_t *fr = seq_frame(s, fi);
    /* Centre the fixed cell in the framebuffer */
    int ox = (FRAME_W - s->cell_w) / 2;
    int oy = (FRAME_H - s->cell_h) / 2 - 8;
    if (ox < 4) ox = 4;
    if (oy < 4) oy = 4;
    draw_cell_border(rgb, FRAME_W, FRAME_H, ox - 1, oy - 1, s->cell_w + 2,
                     s->cell_h + 2);
    blit_centered(rgb, FRAME_W, FRAME_H, fr, s->cell_w, s->cell_h, ox, oy);

    /* Tiny filmstrip of all frames in this sequence along the bottom */
    int strip_y = FRAME_H - 40;
    int sx = 4;
    if (s->frames) {
      for (int i = 0; i < s->count; i++) {
        const terse_asset_t *f = s->frames[i];
        int cw = s->cell_w;
        /* scale strip cells down if needed */
        int max_strip = 36;
        int cell = cw > max_strip ? max_strip : cw;
        int ch = s->cell_h > 28 ? 28 : s->cell_h;
        if (sx + cell + 2 > FRAME_W) break;
        /* draw mini: nearest subsample via centred blit into small cell */
        int mx = sx, my = strip_y;
        if (i == fi) draw_cell_border(rgb, FRAME_W, FRAME_H, mx - 1, my - 1,
                                      cell + 2, ch + 2);
        /* simple 1:1 if fits, else skip pixels */
        int x0 = mx + (cell - f->w) / 2;
        int y0 = my + (ch - f->h) / 2;
        for (int j = 0; j < f->h; j++) {
          for (int ii = 0; ii < f->w; ii++) {
            uint8_t v = f->pix[j * f->w + ii] & 3;
            if (!v) continue;
            int xx = x0 + ii, yy = y0 + j;
            if (xx < mx || yy < my || xx >= mx + cell || yy >= my + ch) continue;
            if (xx >= FRAME_W || yy >= FRAME_H) continue;
            size_t idx = ((size_t)yy * FRAME_W + xx) * 3;
            rgb[idx] = f->pal[v][0];
            rgb[idx + 1] = f->pal[v][1];
            rgb[idx + 2] = f->pal[v][2];
          }
        }
        sx += cell + 4;
      }
    }

    char title[160];
    snprintf(title, sizeof title,
             "%s  frame %d/%d  cell %dx%d  %dms %s", s->label, fi + 1, s->count,
             s->cell_w, s->cell_h, period_ms, paused ? "[paused]" : "");
    SDL_SetWindowTitle(win, title);

    SDL_UpdateTexture(tex, NULL, rgb, FRAME_W * 3);
    SDL_RenderClear(ren);
    SDL_RenderCopy(ren, tex, NULL, NULL);
    SDL_RenderPresent(ren);
    SDL_Delay(16);
  }

  free(xc_mem);
  free(rgb);
  SDL_DestroyTexture(tex);
  SDL_DestroyRenderer(ren);
  SDL_DestroyWindow(win);
  SDL_Quit();
  return 0;
}
