/* GUESS: video-derived Ms. Gorf sketch — not XC.LOGIC.
 * Integer 320×204 playfield. Pattern art from disk via assets_gen.
 *
 * Pipeline: float sim (sub-pixel) → floor onto buffer pixels → host integer-scales
 * that buffer to the window. Nothing is drawn or moved in window/scaled space.
 */
#ifndef GAME_H
#define GAME_H

#include <stdint.h>

#define FB_W 320
#define FB_H 204

typedef enum {
  MODE_SELECT = 0,
  MODE_INTRO,
  MODE_PLAY,
  MODE_DEAD
} game_mode_t;

typedef struct {
  uint8_t *rgb; /* FB_W*FB_H*3 */
  game_mode_t mode;
  int keys[512];
  int mouse_x, mouse_y, mouse_down;
  int start_players; /* 1 or 2 from select */
} game_t;

void game_init(game_t *g, uint8_t *rgb);
void game_keydown(game_t *g, int scancode);
void game_keyup(game_t *g, int scancode);
void game_mouse(game_t *g, int x, int y, int down);
void game_update(game_t *g, float dt);
void game_render(game_t *g);

#endif
