/* SFX from work/video_refs/audio (copied into sfx/). */
#ifndef SOUND_H
#define SOUND_H

int sound_init(void);
void sound_quit(void);

void sound_play_title(void);   /* 1or2start — once on select */
void sound_stop_title(void);
void sound_play_startup(void); /* after start from title */
void sound_play_galaxy(void);
void sound_play_shoot(void);
void sound_play_playerdie(void);
void sound_play_clonedestroy(void); /* clear-burst / level end */

#endif
