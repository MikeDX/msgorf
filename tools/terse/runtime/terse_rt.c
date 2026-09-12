#include "terse_rt.h"
#include <stdlib.h>
#include <string.h>

void terse_frame_init(terse_frame_t *f, uint16_t w, uint16_t h) {
  f->w = w; f->h = h;
  f->pix = calloc((size_t)w * h, 1);
  f->own = calloc((size_t)w * h, sizeof(uint16_t));
}

void terse_frame_clear(terse_frame_t *f) {
  memset(f->pix, 0, (size_t)f->w * f->h);
  memset(f->own, 0, (size_t)f->w * f->h * sizeof(uint16_t));
}

void terse_frame_free(terse_frame_t *f) {
  free(f->pix); free(f->own);
  f->pix = NULL; f->own = NULL;
}

int terse_blit_pattern(terse_frame_t *f, const char **rows, int rh, int rw,
                       int x, int y, uint16_t owner) {
  int hits = 0;
  for (int j = 0; j < rh; j++) {
    int yy = y + j;
    if (yy < 0 || yy >= f->h) continue;
    const char *row = rows[j];
    for (int i = 0; i < rw; i++) {
      char ch = row[i];
      if (ch < '1' || ch > '3') continue;
      int xx = x + i;
      if (xx < 0 || xx >= f->w) continue;
      size_t idx = (size_t)yy * f->w + (size_t)xx;
      if (f->own[idx] && f->own[idx] != owner) hits++;
      f->pix[idx] = (uint8_t)(ch - '0');
      f->own[idx] = owner;
    }
  }
  return hits;
}
