import logging
import sys

from PyQt5.QtWidgets import QApplication

from main_window import MainWindow


def main():
    logging.basicConfig(format="%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.DEBUG)

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    main()
