/* Portable xorshift32 — same stream on native and WASM (unlike libc rand). */
#ifndef RNG_H
#define RNG_H

#include <stdint.h>

void rng_seed(uint32_t seed);
uint32_t rng_u32(void);
int rng_int(int n);          /* 0 .. n-1, n>0 */
float rng_frand(void);       /* [0, 1) */
uint32_t rng_fresh_seed(void); /* wall-ish entropy for a new credit */

#endif
