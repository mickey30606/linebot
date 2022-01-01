from transitions.extensions import GraphMachine

from utils import send_text_message
from WS.WS import WS

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_find_music(self, event):
        result = WS(event.message.text)
        for i in result:
            if i.lower() == "youtube" or i.lower == "yt":
                return True
        return False

    def is_going_to_cut_music(self, event):
        result = WS(event.message.text)
        if len(result) == 1 and (result[0] == '1' or result[0] == '2' or result[0] == '3'):
            return True
        return False

    def is_going_go_back(self, event):
        result = WS(event.message.text)
        for i in result:
            if i == "從頭再來一次":
                return True
        return False

    def is_going_to_final_state(self, start, end, duration):
        if start < 0:
            return False
        if end > duration:
            return False
        if start >= end:
            return False
        return True

    def on_enter_find_music(self, event):
        print("I'm entering find music")
        return

    def on_exit_find_music(self, event):
        print("Leaving find music")
        return

    def on_enter_cut_music(self, event):
        print("I'm entering cut music")
        return
