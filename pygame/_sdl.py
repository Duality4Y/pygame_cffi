
import cffi

ffi = cffi.FFI()

ffi.cdef("""

// constants

#define SDL_INIT_EVERYTHING ...
#define SDL_INIT_VIDEO ...

#define SDL_SWSURFACE ...
#define SDL_ANYFORMAT ...

// structs

typedef struct SDL_PixelFormat {
    uint8_t BitsPerPixel;
    uint32_t Rmask, Gmask, Bmask, Amask;
    ...;
} SDL_PixelFormat;

typedef struct SDL_Rect {
    int16_t x, y;
    uint16_t w, h;
} SDL_Rect;

typedef struct SDL_Surface {
    SDL_PixelFormat* format;
    int w, h;
    ...;
} SDL_Surface;

typedef struct SDL_VideoInfo {
    SDL_PixelFormat* vfmt;
    ...;
} SDL_VideoInfo;

typedef uint32_t Uint32;

// functions

int SDL_Init(uint32_t flags);
void SDL_Quit(void);
SDL_Surface *SDL_SetVideoMode(int width, int height, int bpp, uint32_t flags);
uint32_t SDL_WasInit(uint32_t flags);
char *SDL_GetError(void);

uint32_t SDL_MapRGBA(SDL_PixelFormat *fmt, uint8_t r, uint8_t g, uint8_t b, uint8_t a);

SDL_Surface* SDL_GetVideoSurface(void);
SDL_VideoInfo* SDL_GetVideoInfo(void);

int SDL_LockSurface(SDL_Surface*);
void SDL_UnlockSurface(SDL_Surface*);
int SDL_FillRect(SDL_Surface *dst, SDL_Rect *dsrect, uint32_t color);

SDL_Surface  *SDL_CreateRGBSurface(Uint32 flags, int width, int height,
       int depth, Uint32 Rmask, Uint32 Gmask, Uint32 Bmask, Uint32 Amask);

int SDL_BlitSurface(SDL_Surface *src,  SDL_Rect  *srcrect,  SDL_Surface
       *dst, SDL_Rect *dstrect);

int SDL_Flip(SDL_Surface*);

void SDL_PumpEvents(void);

void SDL_WM_GetCaption(char **title, char **icon);

void SDL_WM_SetCaption(const char *title, const char *icon);

""")

sdl = ffi.verify(libraries=['SDL'],
    include_dirs=['/usr/include/SDL'],
    source="#include <SDL.h>")

def LockSurface(c_surface):
    res = sdl.SDL_LockSurface(c_surface)
    if res == -1:
        raise RuntimeError("error locking surface")

def FillRect(dst, dstrect, color):
    from pygame.error import SDLError

    res = sdl.SDL_FillRect(dst, dstrect, color)
    if res == -1:
        raise SDLError.from_sdl_error()

def BlitSurface(src, srcrect, dst, dstrect):
    from pygame.error import SDLError

    res = sdl.SDL_BlitSurface(src, srcrect, dst, dstrect)
    if res < 0:
        raise SDLError.from_sdl_error()

class locked(object):
    def __init__(self, c_surface):
        self.c_surface = c_surface

    def __enter__(self):
        LockSurface(self.c_surface)

    def __exit__(self, *args):
        sdl.SDL_UnlockSurface(self.c_surface)