import queue
from loader_coro import load_file
from saver import save_file


class GolController():

    def __init__(self, model, engine, grid_view, info_view):
        self.queue = queue.Queue()
        self.model = model
        self.engine = engine
        self.grid_view = grid_view(self.queue)
        self.info_view = info_view(self.queue)

        self.go()

    def go(self):
        done = False
        auto_advance = False
        view_busy = False
        self.grid_view.queue.put(("update", self.model.state))
        while not done:
            msg, attr = self.queue.get()  # blocking
            if msg == "quit":
                self.info_view.queue.put(("quit", None))
                self.grid_view.queue.put(("quit", None))
                done = True
            elif msg == "open":
                try:
                    self.model = load_file(attr)
                except FileNotFoundError:
                    self.info_view.queue.put(("error_loading", None))
                else:
                    self.info_view.queue.put(("model", self.model))
                    self.grid_view.queue.put(("update", self.model.state))
                    view_busy = True
            elif msg == "save":
                try:
                    save_file(self.model, attr)
                except FileNotFoundError:
                    self.info_view.queue.put(("error_saving", None))
            elif msg == "step":
                self.model = self.engine.advance(self.model)
                self.grid_view.queue.put(("update", self.model.state))
                view_busy = True
            elif msg == "run":
                auto_advance = not auto_advance
            elif msg == "view_idle":
                view_busy = False
            elif msg == "view_busy":
                view_busy = True
            elif msg == "toggle_cell":
                if attr in self.model.state:
                    self.model.state.remove(attr)
                else:
                    self.model.state.add(attr)
                self.grid_view.queue.put(("update", self.model.state))
                view_busy = True

            if auto_advance and not view_busy:
                self.model = self.engine.advance(self.model)
                self.grid_view.queue.put(("update", self.model.state))
                view_busy = True
