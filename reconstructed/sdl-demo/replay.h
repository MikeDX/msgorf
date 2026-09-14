/* Tick-based sparse input recording / playback for deterministic replays. */
#ifndef REPLAY_H
#define REPLAY_H

#include "game.h"

#include <stddef.h>
#include <stdint.h>

typedef enum {
  REPLAY_IDLE = 0,
  REPLAY_RECORDING = 1,
  REPLAY_READY = 2,   /* finished run; blob available */
  REPLAY_PLAYING = 3
} replay_mode_t;

void replay_set_build_id(const char *id);
const char *replay_build_id(void);

void replay_reset(void);
void replay_begin_record(uint32_t seed);
void replay_begin_play(void); /* after successful load */
void replay_cancel(void);

/* Call once per sim tick, after live input poll, before game_update. */
void replay_before_update(game_t *g, unsigned tick);

/* Finalize recording (score + duration). */
void replay_end_record(uint32_t score, unsigned ticks);

replay_mode_t replay_mode(void);
uint32_t replay_seed(void);
uint32_t replay_score(void);
unsigned replay_ticks(void);
int replay_playing(void);
int replay_ready(void);

/* Encoded blob (valid while READY or after end_record). */
const uint8_t *replay_blob(void);
size_t replay_blob_len(void);

/* Load a blob; on success enters PLAYING prep (caller should begin_level). */
int replay_load(const uint8_t *data, size_t len);

/* Capture / apply helpers used by host */
void replay_capture_from_game(game_t *g);
void replay_apply_to_game(game_t *g);

#endif
