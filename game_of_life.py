from gol.model import GolModel
from gol.engine.isotropic import GolEngine
from gol.view.info import GolInfoView
from gol.view.grid import GolGridView
from gol.controller import GolController


engine = GolEngine()
model = GolModel()
model.state = set({(-1, 0), (0, 0), (1, 0)})

hub = GolController(model, engine, GolGridView, GolInfoView)
