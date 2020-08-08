import logging
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


def main():
    logging.basicConfig(format="%(asctime)s.%(msecs)03d - %(levelname)s: %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.DEBUG)

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Asset explorer")

    layout = QVBoxLayout()

    test_button = QPushButton(text="Do the thing!")
    test_button.clicked.connect(button_clicked)
    layout.addWidget(test_button)

    window.setLayout(layout)
    window.show()

    app.exec()


def button_clicked():
    logging.info("Did a thing!")


if __name__ == '__main__':
    main()
