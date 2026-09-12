#include "xc_map.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define ROMSTART 0x4000

uint8_t *xc_load_64k(const char *path) {
  FILE *fp = fopen(path, "rb");
  if (!fp) return NULL;
  uint8_t *buf = malloc(65536);
  if (!buf) {
    fclose(fp);
    return NULL;
  }
  size_t n = fread(buf, 1, 65536, fp);
  fclose(fp);
  if (n != 65536) {
    free(buf);
    return NULL;
  }
  return buf;
}

void xc_pattern_free(xc_pattern_t *p) {
  free(p->pix);
  p->pix = NULL;
  p->w = p->h = 0;
}

int xc_decode_simple(const uint8_t *mem, int atbl_index, xc_pattern_t *out) {
  memset(out, 0, sizeof(*out));
  if (!mem || atbl_index < 0 || atbl_index > 63) return -1;
  uint16_t ptr = (uint16_t)mem[ROMSTART + atbl_index * 2] |
                 ((uint16_t)mem[ROMSTART + atbl_index * 2 + 1] << 8);
  if (ptr < ROMSTART || ptr > 0xFFF0) return -1;
  if (ptr >= 0x4200 && ptr < 0x4300) return -1; /* animation table */
  uint8_t bpr = mem[ptr + 2];
  uint8_t h = mem[ptr + 3];
  if (bpr == 0 || h == 0 || bpr > 64 || h > 64) return -1;
  uint16_t w = (uint16_t)bpr * 4;
  const uint8_t *data = mem + ptr + 7;
  uint8_t *pix = malloc((size_t)w * h);
  if (!pix) return -1;
  for (int row = 0; row < h; row++) {
    int col = 0;
    for (int b = 0; b < bpr; b++) {
      uint8_t byte = data[row * bpr + b];
      for (int shift = 6; shift >= 0 && col < w; shift -= 2) {
        pix[row * w + col] = (uint8_t)((byte >> shift) & 3);
        col++;
      }
    }
  }
  out->w = w;
  out->h = h;
  out->pix = pix;
  return 0;
}
