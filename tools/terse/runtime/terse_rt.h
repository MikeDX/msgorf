/* Host runtime ABI for TERSE experiments (SDL/WASM later). */
#ifndef TERSE_RT_H
#define TERSE_RT_H
#include <stdint.h>
#include <stddef.h>

typedef struct {
  uint16_t w, h;
  uint8_t *pix;   /* 0..3 */
  uint16_t *own;  /* owner id per pixel; 0 = empty */
} terse_frame_t;

void terse_frame_init(terse_frame_t *f, uint16_t w, uint16_t h);
void terse_frame_clear(terse_frame_t *f);
/* returns number of overlay collisions while blitting non-zero pixels */
int terse_blit_pattern(terse_frame_t *f, const char **rows, int rh, int rw,
                       int x, int y, uint16_t owner);
void terse_frame_free(terse_frame_t *f);

#endif
