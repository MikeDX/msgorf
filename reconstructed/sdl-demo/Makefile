# Ms. Gorf GUESS SDL demo — 320×204 pixel buffer + disk patterns.
# Native: make / make run
# Web:    make web   (EMSDK=/Users/mike/src/emsdk or source emsdk_env.sh)

ROOT      := ../..
RUNTIME   := $(ROOT)/tools/terse/runtime
PACK      := $(RUNTIME)/pack_assets.py
ASSETS_C  := $(RUNTIME)/assets_gen.c
ASSETS_H  := $(RUNTIME)/assets_gen.h
PLAY_JSON := $(ROOT)/play/assets.json
AUDIO_SRC := $(ROOT)/work/video_refs/audio
SFX_DIR   := sfx
SFX_STEMS := 1or2start startup galaxy p1shoot playerdie clonedestroy lastship
SFX_OGGS  := $(addsuffix .ogg,$(SFX_STEMS))

VIEW_SCALE ?= 3
DRAW_TILE_SNAP ?= 0
CFLAGS     ?= -O2 -Wall -Wextra -std=c11
INCLUDES   := -I. -I$(RUNTIME)
SRCS       := main.c game.c sound.c $(ASSETS_C)

# --- native ---
SDL_CFLAGS := $(shell sdl2-config --cflags 2>/dev/null)
SDL_LIBS   := $(shell sdl2-config --libs 2>/dev/null)
MIX_CFLAGS := $(shell pkg-config --cflags SDL2_mixer 2>/dev/null)
NATIVE_BIN := msgorf_sdl

# --- emscripten ---
EMSDK ?= $(HOME)/src/emsdk
ifdef EMSDK
  ifneq ($(wildcard $(EMSDK)/emsdk_env.sh),)
    EMCC := bash -lc 'source "$(EMSDK)/emsdk_env.sh" >/dev/null 2>&1 && emcc'
  endif
endif
EMCC ?= emcc
WEB_DIR := web
WEB_OUT := $(WEB_DIR)/index.html

.PHONY: all native run web deploy clean assets font sync-sfx stamp-web

all: native

assets: $(ASSETS_C)

SFX_FILES := $(addprefix $(SFX_DIR)/,$(SFX_OGGS))

sync-sfx: $(SFX_FILES)

$(SFX_DIR):
	mkdir -p $(SFX_DIR)

# Compact OGG for native + web preload (~100KB vs ~1.2MB WAV).
$(SFX_DIR)/%.ogg: $(AUDIO_SRC)/%.wav | $(SFX_DIR)
	ffmpeg -y -hide_banner -loglevel error -i $< -c:a vorbis -strict experimental -q:a 3 $@

$(ASSETS_C) $(ASSETS_H): $(PLAY_JSON) $(PACK)
	python3 $(PACK)

font_gen.h: ../video-demo/font_guess.json
	python3 gen_font.py

native: assets sync-sfx $(NATIVE_BIN)

$(NATIVE_BIN): main.c game.c sound.c sound.h game.h font_gen.h $(ASSETS_C) $(ASSETS_H) $(SFX_FILES)
	$(CC) $(CFLAGS) -DVIEW_SCALE=$(VIEW_SCALE) -DDRAW_TILE_SNAP=$(DRAW_TILE_SNAP) $(INCLUDES) $(SDL_CFLAGS) $(MIX_CFLAGS) \
	  -o $@ main.c game.c sound.c $(ASSETS_C) $(SDL_LIBS) -lSDL2_mixer -lm

run: native
	./$(NATIVE_BIN)

web: assets sync-sfx
	@mkdir -p $(WEB_DIR)
	@command -v emcc >/dev/null 2>&1 || { \
	  echo "emcc not on PATH — sourcing $(EMSDK)/emsdk_env.sh"; \
	  . "$(EMSDK)/emsdk_env.sh"; \
	}
	bash -lc 'source "$(EMSDK)/emsdk_env.sh" >/dev/null && \
	  emcc -O1 -Wall -std=c11 -DVIEW_SCALE=$(VIEW_SCALE) -DDRAW_TILE_SNAP=$(DRAW_TILE_SNAP) $(INCLUDES) \
	    main.c game.c sound.c $(ASSETS_C) \
	    -sUSE_SDL=2 -sUSE_SDL_MIXER=2 -sSDL2_MIXER_FORMATS='\''["ogg"]'\'' \
	    -sALLOW_MEMORY_GROWTH=1 -sMINIFY_HTML=0 \
	    --preload-file $(SFX_DIR)@/sfx \
	    -sEXPORTED_FUNCTIONS=_main,_msgorf_pad_move,_msgorf_pad_aim,_msgorf_pad_fire,_msgorf_pad_start,_msgorf_get_mode \
	    -sEXPORTED_RUNTIME_METHODS=ccall,cwrap \
	    --shell-file shell.html \
	    -o $(WEB_OUT)'
	@$(MAKE) stamp-web
	@echo "Open $(WEB_OUT) via a local HTTP server (file:// may block WASM)."
	@du -h $(WEB_DIR)/index.data 2>/dev/null || true

# Bust browser caches: unique ?v= on index.js / .wasm / .data each build.
stamp-web:
	@bid=$$(git -C "$(ROOT)" rev-parse --short HEAD 2>/dev/null || echo nogit); \
	 bid="$$bid-$$(date +%s)"; \
	 python3 stamp_web.py $(WEB_DIR)/index.html "$$bid"

# Optional: DEPLOY_HOST=mike@192.168.68.105 DEPLOY_PATH=~/msgorf
DEPLOY_HOST ?= mike@192.168.68.105
DEPLOY_PATH ?= ~/msgorf

deploy: web
	rsync -avz --delete \
	  --exclude docker-compose.yml --exclude nginx \
	  $(WEB_DIR)/ $(DEPLOY_HOST):$(DEPLOY_PATH)/
	rsync -avz deploy/nginx-default.conf $(DEPLOY_HOST):$(DEPLOY_PATH)/nginx/default.conf
	ssh $(DEPLOY_HOST) 'chmod 755 $(DEPLOY_PATH); docker exec msgorf nginx -s reload 2>/dev/null || true'
	@echo "Deployed with cache-busting; nginx reloaded."

clean:
	rm -f $(NATIVE_BIN)
	rm -rf $(WEB_DIR)
