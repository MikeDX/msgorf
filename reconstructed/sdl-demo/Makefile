# Ms. Gorf GUESS SDL demo — 320×204 pixel buffer + disk patterns.
# Native: make / make run
# Web:    make web   (EMSDK=/Users/mike/src/emsdk or source emsdk_env.sh)

ROOT      := ../..
RUNTIME   := $(ROOT)/tools/terse/runtime
PACK      := $(RUNTIME)/pack_assets.py
ASSETS_C  := $(RUNTIME)/assets_gen.c
ASSETS_H  := $(RUNTIME)/assets_gen.h
PLAY_JSON := $(ROOT)/play/assets.json

VIEW_SCALE ?= 3
CFLAGS     ?= -O2 -Wall -Wextra -std=c11
INCLUDES   := -I. -I$(RUNTIME)
SRCS       := main.c game.c $(ASSETS_C)

# --- native ---
SDL_CFLAGS := $(shell sdl2-config --cflags 2>/dev/null)
SDL_LIBS   := $(shell sdl2-config --libs 2>/dev/null)
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

.PHONY: all native run web deploy clean assets font

all: native

assets: $(ASSETS_C)

$(ASSETS_C) $(ASSETS_H): $(PLAY_JSON) $(PACK)
	python3 $(PACK)

font_gen.h: ../video-demo/font_guess.json
	python3 gen_font.py

native: assets $(NATIVE_BIN)

$(NATIVE_BIN): main.c game.c game.h font_gen.h $(ASSETS_C) $(ASSETS_H)
	$(CC) $(CFLAGS) -DVIEW_SCALE=$(VIEW_SCALE) $(INCLUDES) $(SDL_CFLAGS) \
	  -o $@ main.c game.c $(ASSETS_C) $(SDL_LIBS) -lm

run: native
	./$(NATIVE_BIN)

web: assets
	@mkdir -p $(WEB_DIR)
	@command -v emcc >/dev/null 2>&1 || { \
	  echo "emcc not on PATH — sourcing $(EMSDK)/emsdk_env.sh"; \
	  . "$(EMSDK)/emsdk_env.sh"; \
	}
	bash -lc 'source "$(EMSDK)/emsdk_env.sh" >/dev/null && \
	  emcc -O1 -Wall -std=c11 -DVIEW_SCALE=$(VIEW_SCALE) $(INCLUDES) \
	    main.c game.c $(ASSETS_C) \
	    -sUSE_SDL=2 -sALLOW_MEMORY_GROWTH=1 -sFORCE_FILESYSTEM=0 \
	    -sEXPORTED_FUNCTIONS=_main,_msgorf_pad_move,_msgorf_pad_aim,_msgorf_pad_fire,_msgorf_pad_start,_msgorf_get_mode \
	    -sEXPORTED_RUNTIME_METHODS=ccall,cwrap \
	    --shell-file shell.html \
	    -o $(WEB_OUT)'
	@echo "Open $(WEB_OUT) via a local HTTP server (file:// may block WASM)."

# Optional: DEPLOY_HOST=mike@192.168.68.105 DEPLOY_PATH=~/msgorf
DEPLOY_HOST ?= mike@192.168.68.105
DEPLOY_PATH ?= ~/msgorf

deploy: web
	rsync -avz --delete \
	  --exclude docker-compose.yml --exclude nginx \
	  $(WEB_DIR)/ $(DEPLOY_HOST):$(DEPLOY_PATH)/
	ssh $(DEPLOY_HOST) 'chmod 755 $(DEPLOY_PATH)'

clean:
	rm -f $(NATIVE_BIN)
	rm -rf $(WEB_DIR)
