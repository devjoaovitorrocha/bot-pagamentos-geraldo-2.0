import logging
import sys
import os
from multiprocessing import Process
from ui.main_window import run_app

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)  # ou outra pasta onde o .exe está


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def start_ui():
    run_app()

if __name__ == "__main__":
    p = Process(target=start_ui)
    p.start()
    p.join()
