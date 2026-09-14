/* Headless replay verifier — print final score after simulating a .mgr1 blob.
 * Usage: msgorf_verify <replay.bin>
 * Exit 0 + score on stdout if the run reaches GAME OVER; non-zero on failure.
 */
#include "game.h"
#include "replay.h"

#include <stdio.h>
#include <stdlib.h>

#define SIM_DT (1.f / 60.f)
#define MAX_TICKS (60 * 60 * 30) /* 30 minutes of sim */

int main(int argc, char **argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: %s <replay.bin>\n", argv[0]);
    return 2;
  }

  FILE *f = fopen(argv[1], "rb");
  if (!f) {
    perror(argv[1]);
    return 2;
  }
  if (fseek(f, 0, SEEK_END) != 0) {
    fclose(f);
    return 2;
  }
  long sz = ftell(f);
  if (sz < 8 || sz > 512 * 1024) {
    fclose(f);
    fprintf(stderr, "bad size\n");
    return 2;
  }
  rewind(f);
  uint8_t *data = (uint8_t *)malloc((size_t)sz);
  if (!data || fread(data, 1, (size_t)sz, f) != (size_t)sz) {
    free(data);
    fclose(f);
    return 2;
  }
  fclose(f);

  static uint8_t fb[FB_W * FB_H * 3];
  game_t g;
  game_init(&g, fb);
  if (!game_start_replay(&g, data, (size_t)sz)) {
    fprintf(stderr, "load failed\n");
    free(data);
    return 3;
  }
  free(data);

  uint32_t claimed = replay_score();
  int ticks = 0;
  while (ticks < MAX_TICKS && game_get_mode(&g) != MODE_DEAD) {
    game_update(&g, SIM_DT);
    ticks++;
  }
  if (game_get_mode(&g) != MODE_DEAD) {
    fprintf(stderr, "did not reach game over (%d ticks)\n", ticks);
    return 4;
  }

  int score = game_get_score(&g);
  printf("%d\n", score);
  if ((uint32_t)score != claimed) {
    fprintf(stderr, "score mismatch: sim=%d claimed=%u\n", score, claimed);
    return 5;
  }
  return 0;
}
