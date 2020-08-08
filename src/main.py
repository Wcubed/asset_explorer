import sys

from PyQt5.QtWidgets import QApplication, QWidget


def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Asset explorer")
    window.show()
    
    app.exec()


if __name__ == '__main__':
    main()
