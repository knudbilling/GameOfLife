import queue
import threading
import tkinter
import tkinter.filedialog
from tkinter import messagebox


class GolInfoView(threading.Thread):

    def __init__(self, hub_queue):
        threading.Thread.__init__(self)
        self.hub_queue = hub_queue
        self.queue = queue.Queue()
        self.model = None
        self.start()

    def run(self):
        root = tkinter.Tk()
        root.title("Game of Life")
        
        label = tkinter.Label(root, text="Hello there!")
        label.pack()

        self.survival = tkinter.Entry(root, text="hgfdghhgdfi")
        self.survival.pack()

        load_button = tkinter.Button(
            root, text="Open file...", command=self.open_file)
        load_button.pack()

        save_button = tkinter.Button(root, text="Save file..", command=self.save_file)
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

        root.after(200, self.check_queue)

        root.mainloop()

        self.hub_queue.put(("quit", None))

        # Delete anything from self that refers to tkinter
        # Needed so the object does not also try to destroy the tkinter session,
        # causing tkinter to be accessed from another thread

        del self.root
        del self.run_button
        del self.description
        del self.survival

    def survival_entry(self):
        print("Survival entry")

    def check_queue(self):
        while not self.queue.empty():
            msg, attr = self.queue.get()

            if msg == "quit":
                self.root.destroy()
            elif msg == "model":
                self.model = attr
                self.update_info()
            elif msg == "error_saving":
                messagebox.showwarning("Warning","Could not save file.")
            elif msg == "error_loading":
                messagebox.showerror("Error","Could not load file.")

        self.root.after(200, self.check_queue)

    def update_info(self):
        self.description.delete(1.0, tkinter.END)
        for line in self.model.description:
            self.description.insert(tkinter.END, line+"\n")

    def open_file(self):
        filename = tkinter.filedialog.askopenfilename(initialdir=".")
        self.hub_queue.put(("open", filename))

    def save_file(self):
        filename = tkinter.filedialog.asksaveasfilename(initialdir=".")
        self.hub_queue.put(("save", filename))

    def step(self):
        self.hub_queue.put(("step", 1))

    def auto_advance(self):
        self.running = not self.running
        if self.running:
            self.run_button.config(text="Stop")
        else:
            self.run_button.config(text="Run")
        self.hub_queue.put(("run", None))
