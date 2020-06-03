"""Contains the information view

Must contain a 'GolInfoView' class that starts itself as a thread
"""

import queue
import threading
import tkinter
import tkinter.filedialog
from tkinter import messagebox

class GolInfoView(threading.Thread):
    """Everything needed for the info window
    """

    def __init__(self, hub_queue):
        threading.Thread.__init__(self)
        self.hub_queue = hub_queue
        self.queue = queue.Queue()
        self.model = None
        self.running = False
        self.start()

    def run(self):
        # Set up the tkinter window
        root = tkinter.Tk()
        root.title("Game of Life")

        load_button = tkinter.Button(
            root, text="Open file...", command=self.open_file)
        load_button.pack()

        save_button = tkinter.Button(
            root, text="Save file..", command=self.save_file)
        save_button.pack()

        step_button = tkinter.Button(root, text="Step", command=self.step)
        step_button.pack()

        self.run_button = tkinter.Button(
            root, text="Run", command=self.auto_advance)
        self.run_button.pack()

        self.description = tkinter.Text(root, width=80, height=10)
        self.description.pack()

        self.root = root

        self.running = False

        # Poll the queue every 200ms
        root.after(200, self.check_queue)

        # tkinter main loop
        root.mainloop()

        # Tell controller to quit
        self.hub_queue.put(("quit", None))

        # Delete anything from self that refers to tkinter
        # Needed so the object does not also try to destroy the tkinter session,
        # causing tkinter to be accessed from another thread

        del self.root
        del self.run_button
        del self.description

    def check_queue(self):
        """Check if there are messages on the queue
        """

        while not self.queue.empty():
            msg, attr = self.queue.get()

            if msg == "quit":
                self.root.destroy()
            elif msg == "model":
                self.model = attr
                self.update_info()
            elif msg == "error_saving":
                messagebox.showwarning("Warning", "Could not save file.")
            elif msg == "error_loading":
                messagebox.showerror("Error", "Could not load file.")

        # Schedule another check after 200ms
        self.root.after(200, self.check_queue)

    def update_info(self):
        """Update the description/comments text-box
        """

        self.description.delete(1.0, tkinter.END)
        for line in self.model.description:
            self.description.insert(tkinter.END, line+"\n")

    def open_file(self):
        """Ask which file to open, and send message to controller
        """

        filename = tkinter.filedialog.askopenfilename(initialdir=".")
        self.hub_queue.put(("open", filename))

    def save_file(self):
        """Ask for filename to save the game of life, and send message to controller
        """

        filename = tkinter.filedialog.asksaveasfilename(initialdir=".")
        self.hub_queue.put(("save", filename))

    def step(self):
        """Tell controller to advance one tick/generation
        """

        self.hub_queue.put(("step", 1))

    def auto_advance(self):
        """Tell controller to start/stop 'running'. Also change button text to match.
        """

        self.running = not self.running
        if self.running:
            self.run_button.config(text="Stop")
        else:
            self.run_button.config(text="Run")
        self.hub_queue.put(("run", None))
