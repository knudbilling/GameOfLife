import queue
import threading

from collections import defaultdict
from time import time_ns
import pygame

BASE_CELL_SIZE = 100
ZOOM_FACTOR = 0.75

# NEW zoom level:
# zoom is in interval [1, ... [
# 0 = one cell is 100 pixels wide
# 1 = one cell is 75 pixels wide
# ie cell width in pixels = 100 * (0.75 ** zoom)


def queue_translator(event_queue, view_queue):
    done = False
    while not done:
        msg, attr = view_queue.get()  # blocking
        event = pygame.event.Event(pygame.USEREVENT, msg=msg, attr=attr)
        event_queue.post(event)
        if msg == "quit":
            done = True


class GolGridView(threading.Thread):

    def __init__(self, hub_queue: queue.Queue):
        threading.Thread.__init__(self)
        self.hub_queue = hub_queue

        self.queue = queue.Queue()
        self.center_x = self.center_y = 0

        self.new_zoom = 0

        self.window_size = (1000, 1000)
        self.color_bg = (50, 50, 50)
        self.color_alive = (255, 220, 70)
        self.sleep_time = 0
        self.top = -int(self.window_size[0]/2)
        self.left = -int(self.window_size[1]/2)

        self.gol = set()

        self.gol_center = [0, 0]

        self.screen = None

        self.start()

    def process_message(self):
        pass

    def run(self):
        pygame.init()
        pygame.key.set_repeat(250, 40)
        self.screen = pygame.display.set_mode(size=self.window_size)
        pygame.display.set_caption("Game of Life")

        self.screen.fill(self.color_bg)
        self.draw_state(self.color_alive)
        pygame.display.flip()

        # start queue translator
        queue_translator_thread = threading.Thread(
            target=queue_translator, args=[pygame.event, self.queue])
        queue_translator_thread.start()

        right_mouse_button_is_down = False

        last_event_was_mouse_motion = False

        update_view = False

        done = False
        while not done:
            event = pygame.event.wait()  # blocking

            if event.type == pygame.QUIT:
                self.hub_queue.put(("quit", None))
                done = True

            elif event.type == pygame.USEREVENT:
                if event.msg == "quit":
                    done = True
                if event.msg == "update":
                    self.gol = event.attr
                    update_view = True

            elif event.type == pygame.MOUSEBUTTONDOWN:

                # Left mouse button
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    zoom = pow(ZOOM_FACTOR, self.new_zoom) * BASE_CELL_SIZE

                    cell_x = (
                        mouse_x - self.window_size[0]/2) / zoom + self.gol_center[0]
                    cell_y = (
                        mouse_y - self.window_size[1]/2) / zoom + self.gol_center[1]

                    if cell_x < 0:
                        cell_x -= 1

                    if cell_y < 0:
                        cell_y -= 1

                    self.hub_queue.put(
                        ("toggle_cell", (int(cell_x), int(cell_y))))

                # Right mouse button
                elif event.button == 3:
                    right_mouse_button_is_down = True

                # Scroll wheel up
                elif event.button == 4:
                    self.zoom_out()
                    update_view = True

                # Scroll wheel down
                elif event.button == 5:
                    self.zoom_in()
                    update_view = True

            elif event.type == pygame.MOUSEBUTTONUP:
                # Right mouse button
                if event.button == 3:
                    right_mouse_button_is_down = False
                    if last_event_was_mouse_motion:
                        update_view = True
                        last_event_was_mouse_motion = False

            elif event.type == pygame.MOUSEMOTION:
                if right_mouse_button_is_down:
                    last_event_was_mouse_motion = True

                    zoom = pow(ZOOM_FACTOR, self.new_zoom) * BASE_CELL_SIZE

                    self.gol_center[0] -= event.rel[0] / zoom
                    self.gol_center[1] -= event.rel[1] / zoom

            if update_view:
                self.draw()
                update_view = False

        pygame.quit()

    def draw(self):
        self.hub_queue.put(("view-busy", None))
        self.screen.fill(self.color_bg)
        self.draw_state(self.color_alive)
        pygame.display.flip()
        self.hub_queue.put(("view_idle", None))

    def zoom_in(self):
        self.new_zoom += 1

    def zoom_out(self):
        if self.new_zoom > 0:
            self.new_zoom -= 1

    def draw_state(self, colour):

        zoom = pow(ZOOM_FACTOR, self.new_zoom) * BASE_CELL_SIZE

        for x, y in self.gol:

            # translate scale center to origin
            x -= self.gol_center[0]
            y -= self.gol_center[1]

            # scale
            x *= zoom
            y *= zoom

            # translate to view center
            x += self.window_size[0]/2
            y += self.window_size[1]/2

            pygame.draw.rect(self.screen, colour,
                             (x, y, zoom-1, zoom-1))
