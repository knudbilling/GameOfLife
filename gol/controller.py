"""Controller for Game of Life
Must contain a GolController class as specified below
"""

import queue
from gol.files.loader import load_file
from gol.files.saver import save_file


class GolController():
    """Controller for Game of Life
    """

    def __init__(self, model, engine, grid_view, info_view):
        self.queue = queue.Queue()
        self.model = model
        self.engine = engine
        self.grid_view = grid_view(self.queue)
        self.info_view = info_view(self.queue)

        # Start the controller
        self.go()

    def go(self):
        """Starts the controller loop
        """

        # Exit loop when done is True
        done = False

        # This is True when 'running' the game of life
        auto_advance = False

        # This is True when the view is busy updating the game of life
        view_busy = False

        # Start by telling the grid view to draw the cells
        self.grid_view.queue.put(("update", self.model.state))

        while not done:
            # Wait for message from either view
            msg, attr = self.queue.get()

            if msg == "quit":  # Quit the program
                self.info_view.queue.put(("quit", None))
                self.grid_view.queue.put(("quit", None))
                done = True

            elif msg == "open":  # Load file
                try:
                    self.model = load_file(attr)
                except FileNotFoundError:
                    self.info_view.queue.put(("error_loading", None))
                else:
                    # Update the info in the info view
                    self.info_view.queue.put(("model", self.model))
                    # Tell the grid to draw the new cells
                    self.grid_view.queue.put(("update", self.model.state))
                    view_busy = True

            elif msg == "save":  # Save file
                try:
                    save_file(self.model, attr)
                except FileNotFoundError:
                    self.info_view.queue.put(("error_saving", None))

            elif msg == "step":  # Calculate one generation
                # Calculate the next generation
                self.model = self.engine.advance(self.model)
                # Tell the grid view to draw the cells
                self.grid_view.queue.put(("update", self.model.state))
                view_busy = True

            elif msg == "run":  # 'Run' the game of life
                auto_advance = not auto_advance

            elif msg == "view_idle":  # Grid view is done updating the window
                view_busy = False

            elif msg == "view_busy":  # Grid view is budy updating the window
                view_busy = True

            elif msg == "toggle_cell":  # Turn a cell on or off
                if attr in self.model.state:
                    self.model.state.remove(attr)
                else:
                    self.model.state.add(attr)
                # Tell grid view to update window
                self.grid_view.queue.put(("update", self.model.state))
                view_busy = True

            # When the game of life is 'running'
            # only advance to the next generation and tell the grid view
            # to update the window if it is not busy
            if auto_advance and not view_busy:
                self.model = self.engine.advance(self.model)
                self.grid_view.queue.put(("update", self.model.state))
                view_busy = True
