#ifndef XC_MAP_H
#define XC_MAP_H
#include <stdint.h>
#include <stddef.h>

uint8_t *xc_load_64k(const char *path); /* malloc'd 65536 or NULL */

typedef struct {
  uint16_t w, h;
  uint8_t *pix; /* malloc'd 0..3, length w*h */
} xc_pattern_t;

/* Decode ATBL slot as simple 7-byte-header pattern; 0 on success */
int xc_decode_simple(const uint8_t *mem, int atbl_index, xc_pattern_t *out);
void xc_pattern_free(xc_pattern_t *p);

/* Known ANIM-MAP indices */
enum {
  XC_ATBL_PLY1 = 1,
  XC_ATBL_GORF = 9,
  XC_ATBL_LAZON = 10
};

#endif
