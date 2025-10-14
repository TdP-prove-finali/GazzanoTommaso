import flet as ft
from UI.view import View
from model.modello import Model

class Controller:
    def __init__(self, view : View, model : Model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and hold the data
        self._model = model



