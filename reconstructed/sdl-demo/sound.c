#include "sound.h"

#include <SDL.h>
#include <SDL_mixer.h>
#include <stdio.h>

#ifdef __EMSCRIPTEN__
#define SFX_DIR "/sfx"
#else
#define SFX_DIR "sfx"
#endif

/* OGG Vorbis — ~10× smaller than PCM WAV for web preload. */
static Mix_Music *title;
static Mix_Chunk *startup;
static Mix_Chunk *galaxy;
static Mix_Chunk *shoot;
static Mix_Chunk *playerdie;
static Mix_Chunk *clonedestroy;
static Mix_Chunk *lastship;
static Mix_Chunk *gameover;
static int ready;

static Mix_Chunk *load_chunk(const char *name) {
  char path[256];
  snprintf(path, sizeof path, "%s/%s", SFX_DIR, name);
  /* Mix_LoadWAV loads any format SDL_mixer supports (including OGG). */
  Mix_Chunk *c = Mix_LoadWAV(path);
  if (!c) fprintf(stderr, "sound: %s: %s\n", path, Mix_GetError());
  return c;
}

int sound_init(void) {
  if (Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024) != 0) {
    fprintf(stderr, "Mix_OpenAudio: %s\n", Mix_GetError());
    return -1;
  }
  Mix_AllocateChannels(16);

  {
    char path[256];
    snprintf(path, sizeof path, "%s/1or2start.ogg", SFX_DIR);
    title = Mix_LoadMUS(path);
    if (!title) fprintf(stderr, "sound: %s: %s\n", path, Mix_GetError());
  }
  startup = load_chunk("startup.ogg");
  galaxy = load_chunk("galaxy.ogg");
  shoot = load_chunk("p1shoot.ogg");
  playerdie = load_chunk("playerdie.ogg");
  clonedestroy = load_chunk("clonedestroy.ogg");
  lastship = load_chunk("lastship.ogg");
  gameover = load_chunk("gameover.ogg");
  ready = 1;
  return 0;
}

void sound_quit(void) {
  if (!ready) return;
  Mix_HaltMusic();
  Mix_HaltChannel(-1);
  if (title) Mix_FreeMusic(title);
  if (startup) Mix_FreeChunk(startup);
  if (galaxy) Mix_FreeChunk(galaxy);
  if (shoot) Mix_FreeChunk(shoot);
  if (playerdie) Mix_FreeChunk(playerdie);
  if (clonedestroy) Mix_FreeChunk(clonedestroy);
  if (lastship) Mix_FreeChunk(lastship);
  if (gameover) Mix_FreeChunk(gameover);
  title = NULL;
  startup = galaxy = shoot = playerdie = clonedestroy = lastship = gameover = NULL;
  Mix_CloseAudio();
  ready = 0;
}

void sound_play_title(void) {
  if (!ready || !title) return;
  if (Mix_PlayingMusic()) Mix_HaltMusic();
  Mix_PlayMusic(title, 0); /* once — no loop */
}

void sound_stop_title(void) {
  if (!ready) return;
  Mix_HaltMusic();
}

void sound_play_startup(void) {
  if (!ready || !startup) return;
  Mix_PlayChannel(-1, startup, 0);
}

void sound_play_galaxy(void) {
  if (!ready || !galaxy) return;
  Mix_PlayChannel(-1, galaxy, 0);
}

void sound_play_shoot(void) {
  if (!ready || !shoot) return;
  Mix_PlayChannel(-1, shoot, 0);
}

void sound_play_playerdie(void) {
  if (!ready || !playerdie) return;
  Mix_PlayChannel(-1, playerdie, 0);
}

void sound_play_clonedestroy(void) {
  if (!ready || !clonedestroy) return;
  Mix_PlayChannel(-1, clonedestroy, 0);
}

void sound_play_lastship(void) {
  if (!ready || !lastship) return;
  Mix_PlayChannel(-1, lastship, 0);
}

void sound_play_gameover(void) {
  if (!ready || !gameover) return;
  Mix_PlayChannel(-1, gameover, 0);
}
