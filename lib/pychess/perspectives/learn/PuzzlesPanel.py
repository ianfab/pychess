import asyncio
# import random
from io import StringIO

from gi.repository import Gtk

from pychess.System.prefix import addDataPrefix
from pychess.Utils.const import WHITE, BLACK, LOCAL, NORMALCHESS, ARTIFICIAL
from pychess.Utils.GameModel import GameModel
from pychess.Utils.TimeModel import TimeModel
from pychess.Variants import variants
from pychess.Players.Human import Human
from pychess.Players.engineNest import discoverer
from pychess.System import conf
from pychess.perspectives import perspective_manager
from pychess.Savers import fen as fen_loader

__title__ = _("Puzzles")

__icon__ = addDataPrefix("glade/panel_book.svg")

__desc__ = _("Puzzles from GM games")


# http://wtharvey.com/
PUZZLES = (
    ("mate_in_2.txt", "Mate in two"),
    ("mate_in_3.txt", "Mate in three"),
    ("mate_in_4.txt", "Mate in four"),
)


class Sidepanel():
    def load(self, persp):
        self.persp = persp
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.tv = Gtk.TreeView()

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(_("Title"), renderer, text=1)
        self.tv.append_column(column)

        self.tv.connect("row-activated", self.row_activated)

        self.store = Gtk.ListStore(str, str)

        for file_name, title in PUZZLES:
            self.store.append([file_name, title])

        self.tv.set_model(self.store)
        self.tv.get_selection().set_mode(Gtk.SelectionMode.BROWSE)

        scrollwin = Gtk.ScrolledWindow()
        scrollwin.add(self.tv)
        scrollwin.show_all()

        self.box.pack_start(scrollwin, True, True, 0)
        self.box.show_all()

        return self.box

    def row_activated(self, widget, path, col):
        if path is None:
            return
        filename = addDataPrefix("lectures/%s" % PUZZLES[path[0]][0])
        fen = self.get_fen(filename)

        timemodel = TimeModel(0, 0)
        gamemodel = GameModel(timemodel)
        gamemodel.set_practice_game()

        name = conf.get("firstName", _("You"))
        p0 = (LOCAL, Human, (WHITE, name), name)

        engine = discoverer.getEngineByName("stockfish")
        name = discoverer.getName(engine)
        p1 = (ARTIFICIAL, discoverer.initPlayerEngine,
              (engine, BLACK, 20, variants[NORMALCHESS], 60, 0, 0, True), name)

        perspective = perspective_manager.get_perspective("games")
        asyncio.async(perspective.generalStart(
            gamemodel, p0, p1, loaddata=(StringIO(fen), fen_loader, 0, -1)))

    def get_fen(self, text_file):
        """ Choose a random FEN position from text_file """
        print(text_file)
        fen = ""
        with open(text_file, encoding="latin-1") as f:
            for line in f:
                if line.strip().endswith(" 1 0"):
                    fen = line.strip()
                else:
                    continue
        return fen