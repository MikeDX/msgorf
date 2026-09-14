#include "rng.h"

#include <stdint.h>
#include <time.h>

static uint32_t rng_state = 1u;

void rng_seed(uint32_t seed) {
  if (seed == 0u) seed = 1u;
  rng_state = seed;
}

uint32_t rng_u32(void) {
  uint32_t x = rng_state;
  x ^= x << 13;
  x ^= x >> 17;
  x ^= x << 5;
  rng_state = x;
  return x;
}

int rng_int(int n) {
  if (n <= 1) return 0;
  return (int)(rng_u32() % (uint32_t)n);
}

float rng_frand(void) { return (float)(rng_u32() % 10000u) / 10000.f; }

uint32_t rng_fresh_seed(void) {
  uint32_t t = (uint32_t)time(NULL);
  uint32_t mix = t ^ (t << 16) ^ (uint32_t)(uintptr_t)&rng_state;
  mix ^= rng_state;
  if (mix == 0u) mix = 0xA5A5A5A5u;
  return mix;
}
