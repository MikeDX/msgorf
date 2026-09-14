/* No-op audio for headless replay verification. */
#include "sound.h"

int sound_init(void) { return 0; }
void sound_quit(void) {}
void sound_play_title(void) {}
void sound_stop_title(void) {}
void sound_play_startup(void) {}
void sound_play_galaxy(void) {}
void sound_play_shoot(void) {}
void sound_play_playerdie(void) {}
void sound_play_clonedestroy(void) {}
void sound_play_lastship(void) {}
void sound_play_gameover(void) {}
