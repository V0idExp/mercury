import sdl2
import sdl2.ext


window = sdl2.ext.Window('mercury', size=(800, 600))
window.show()

run = True
while run:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            run = False
            break

    window.refresh()

sdl2.ext.quit()
