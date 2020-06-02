from model import GolModel
from engine_isotropic import GolEngine
from info_view import GolInfoView
from grid_view import GolGridView
from controller import GolController

engine = GolEngine()
model = GolModel()
model.state = set({(-1, 0), (0, 0), (1, 0)})

hub = GolController(model, engine, GolGridView, GolInfoView)
