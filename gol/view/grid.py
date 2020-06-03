"""Contains the grid view of the cells

Must contain a GolGridView class that starts itself as a thread
"""

import queue
import threading
import pygame

# The size of a cell without scaling
BASE_CELL_SIZE = 100

# Each step of zoom scales the cell-size by this factor
ZOOM_FACTOR = 0.75


def queue_translator(event_queue, view_queue):
    """Listens for messages on the view queue and puts them into pygames queue

    Parameters:
    event_queue: pygames queue
    view_queue: view queue
    """

    done = False
    while not done:
        # Waits for a message on this threads queue
        msg, attr = view_queue.get()
        # Put it into pygames queue as a USEREVENT
        event = pygame.event.Event(pygame.USEREVENT, msg=msg, attr=attr)
        event_queue.post(event)
        if msg == "quit":
            done = True


class GolGridView(threading.Thread):
    """Everything needed to view the cells in a window

    """

    def __init__(self, hub_queue: queue.Queue):
        threading.Thread.__init__(self)

        # The controllers queue
        self.hub_queue = hub_queue

        # This threads queue
        self.queue = queue.Queue()

        # Start with no zoom
        self.zoom = 0

        # Size of the window
        self.window_size = (1000, 1000)

        # Window background color
        self.color_bg = (50, 50, 50)

        # Cell color
        self.color_alive = (255, 220, 70)

        # Start with no alive cells
        self.gol = set()

        # Which cell is centered in the window?
        self.gol_center = [0, 0]

        # pygame screen
        self.screen = None

        # Start as thread
        self.start()


    def run(self):
        """Setup and run the grid view loop
        """

        # Set up pygame
        pygame.init()
        pygame.key.set_repeat(250, 40)
        self.screen = pygame.display.set_mode(size=self.window_size)
        pygame.display.set_caption("Game of Life")

        # Draw cells
        self.screen.fill(self.color_bg)
        self.draw_state(self.color_alive)
        pygame.display.flip()

        # Start queue translator
        queue_translator_thread = threading.Thread(
            target=queue_translator, args=[pygame.event, self.queue])
        queue_translator_thread.start()

        # To keep track of the status of the right mouse button when
        # moving the center point of the window
        right_mouse_button_is_down = False
        last_event_was_mouse_motion = False

        update_view = False

        done = False
        while not done:
            # Wait for event in pygame queue
            event = pygame.event.wait()

            if event.type == pygame.QUIT:
                self.hub_queue.put(("quit", None))
                done = True

            # This is the messages from the controller
            elif event.type == pygame.USEREVENT:
                if event.msg == "quit":
                    done = True
                if event.msg == "update":
                    self.gol = event.attr
                    update_view = True

            elif event.type == pygame.MOUSEBUTTONDOWN:

                # Left mouse button - Toggle cell on/off
                if event.button == 1:
                    mouse_x, mouse_y = event.pos
                    zoom = pow(ZOOM_FACTOR, self.zoom) * BASE_CELL_SIZE

                    cell_x = (
                        mouse_x - self.window_size[0]/2) / zoom + self.gol_center[0]
                    cell_y = (
                        mouse_y - self.window_size[1]/2) / zoom + self.gol_center[1]

                    # To make float to int rounding error point to the correct cell
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
                    if self.zoom > 0:
                        self.zoom -= 1
                    update_view = True

                # Scroll wheel down
                elif event.button == 5:
                    self.zoom += 1
                    update_view = True

            elif event.type == pygame.MOUSEBUTTONUP:
                # Right mouse button
                if event.button == 3:
                    right_mouse_button_is_down = False
                    if last_event_was_mouse_motion:
                        update_view = True
                        last_event_was_mouse_motion = False

            elif event.type == pygame.MOUSEMOTION:
                # Move the center point when the right mouse button is down
                if right_mouse_button_is_down:
                    last_event_was_mouse_motion = True

                    zoom = pow(ZOOM_FACTOR, self.zoom) * BASE_CELL_SIZE

                    self.gol_center[0] -= event.rel[0] / zoom
                    self.gol_center[1] -= event.rel[1] / zoom

            if update_view:
                self.draw()
                update_view = False

        pygame.quit()


    def draw(self):
        """Handles the administative tasks of drawing of the cells in the grid window
        """

        # Tell the controller that we are busy updating the window
        self.hub_queue.put(("view-busy", None))

        # Clear window and draw it again
        self.screen.fill(self.color_bg)
        self.draw_state(self.color_alive)
        pygame.display.flip()

        # Tell the controller we are not busy anymore
        self.hub_queue.put(("view_idle", None))


    def draw_state(self, color):
        """Draw the cells in the grid window

        Parameters:
        color: Color of the alive cells. See pygame documentation for format.
        """

        # Calculate scaling factor
        scale = pow(ZOOM_FACTOR, self.zoom) * BASE_CELL_SIZE

        for x, y in self.gol:

            # translate scale center to origin
            x -= self.gol_center[0]
            y -= self.gol_center[1]

            # scale
            x *= scale
            y *= scale

            # translate to view center
            x += self.window_size[0]/2
            y += self.window_size[1]/2

            pygame.draw.rect(self.screen, color,
                             (x, y, scale-1, scale-1))
