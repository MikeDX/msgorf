# Ms. Gorf TERSE host runtime (SDL2)
CC ?= cc
SDL_CFLAGS := $(shell sdl2-config --cflags)
SDL_LIBS := $(shell sdl2-config --libs)
CFLAGS ?= -O2 -Wall -Wextra -std=c11 $(SDL_CFLAGS)
ROOT := $(abspath ../../..)
ROM := $(ROOT)/out/msgorf_patterns_at_4000.bin
ASSETS_JSON := $(ROOT)/play/assets.json

OBJS := terse_rt.o assets_gen.o xc_map.o sdl_main.o
BIN := terse_harness

.PHONY: all run clean assets

all: assets $(BIN)

assets:
	python3 pack_assets.py

assets_gen.c assets_gen.h: pack_assets.py
	python3 pack_assets.py

$(BIN): $(OBJS)
	$(CC) -o $@ $(OBJS) $(SDL_LIBS)

%.o: %.c terse_rt.h assets_gen.h xc_map.h
	$(CC) $(CFLAGS) -c -o $@ $<

sdl_main.o: sdl_main.c assets_gen.h
	$(CC) $(CFLAGS) -c -o $@ $<

run: $(BIN)
	./$(BIN) --xc "$(ROM)"

clean:
	rm -f $(OBJS) $(BIN) assets_gen.c assets_gen.h
