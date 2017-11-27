#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Project:    Proverbial Hangman
File:       hangman-pyside.py
Author:     Korvin F. Ezüst

Created:    2017-11-24
IDE:        PyCharm Community Edition

Description:
            A simple hangman game written using PySide.
            To play the game, figure out a proverb by guessing
            letters. If you guess a letter that's not in the
            proverb and you've already guessed it, you get
            a penalty. The game ends when you guess all letters
            correctly or when the hangman is finished.

Notes:
            See the docstring of hangman.py for notes.
"""

from hangman import *
from lib.GuiMain import *
from lib.GuiLanguageSelect import *
from lib.get_ui_strings import *

__author__ = "Korvin F. Ezüst"
__copyright__ = "Copyright (c) 2017., Korvin F. Ezüst"
__license__ = "Apache 2.0"
__version__ = "1.0"
__email__ = "dev@korvin.eu"
__status__ = "Development"

# TODO: test on Windows


class SelectLanguage(QtGui.QMainWindow, Ui_LanguageSelector):
    def __init__(self):
        super(SelectLanguage, self).__init__()
        self.setupUi(self)

        # center window
        self.setGeometry(QtGui.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            self.size(),
            QtGui.qApp.desktop().availableGeometry()))

        self.setWindowTitle("Select Language")

        # Add available languages to the list
        self.comboBox.clear()
        lang_file = os.path.join("resources", "lang.csv")
        self.comboBox.addItems(get_language_list(lang_file))

        # start the game with the selected language
        def start_game():
            selected = self.comboBox.currentText()
            # write selected language to file
            save = os.path.join("resources", "language_selected")
            with open(save, "w") as f:
                f.write(selected)
            self.hide()
            # start game with selected language
            self.game = GameWindow(selected)
            self.game.show()

        self.SetLanguage.clicked.connect(start_game)


class GameWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, selected_lang="English"):
        super(GameWindow, self).__init__()
        self.setupUi(self)

        # center window
        self.setGeometry(QtGui.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            self.size(),
            QtGui.qApp.desktop().availableGeometry()))

        self.ExitButton.clicked.connect(self.close)

        # call the language selector on button click
        def change_language():
            self.hide()
            self.lang_changer = SelectLanguage()
            self.lang_changer.show()
        self.ToolButton.clicked.connect(change_language)

        # restart game when the new game button is clicked
        def new_game():
            sys.stdout.flush()
            os.execl("hangman-pyside.py", " ")

        self.NewGameButton.clicked.connect(new_game)

        # set fonts to monospace
        self.GuessText.setFont("Monospace")
        self.ProverbText.setFont("Monospace")

        # set language selector's icon
        img = os.path.join("resources", "img", "globe.svg")
        icon = QtGui.QIcon(img)
        self.ToolButton.setIcon(icon)

        # set focus on the input field
        self.PlayerInput.setFocus()

        # get strings to use on the GUI
        lang_file = os.path.join("resources", "lang.csv")
        gui_strings = get_strings(lang_file, selected_lang)

        # set error texts
        input_error = gui_strings[16]

        # set up message window to be used
        # in case of invalid input and at the end of the game
        def message_box(title, msg):
            msg_box = QtGui.QMessageBox()
            msg_box.setWindowTitle(title)
            msg_box.setText(msg)
            msg_box.exec_()
            if title == input_error:
                self.PlayerInput.setFocus()
                self.PlayerInput.selectAll()
                pass
            else:
                new_game()

        # set strings
        game_over = gui_strings[17]
        win_message = gui_strings[12]
        lose_message = gui_strings[13]
        invalid_character = gui_strings[9]
        self.setWindowTitle(gui_strings[14])
        self.ExitButton.setText(gui_strings[22])
        self.NewGameButton.setText(gui_strings[21])
        self.ProverbLabel.setText(gui_strings[18][:-1])
        self.GuessLabel.setText(gui_strings[19][:-1])
        self.ProverbText.setText("...")
        self.GuessText.setText("...")
        # set starting image
        self.ImageLabel.setPixmap(os.path.join("resources", "img", "0.png"))

        # filename and path of proverbs file
        gui_prv_file = gui_strings[1]
        gui_prv_path = os.path.join("resources", gui_prv_file)

        # Proverb
        gui_proverb_original = get_proverb(gui_prv_path)
        # Uppercase proverb
        gui_proverb = gui_proverb_original.upper()
        # Valid characters
        gui_alphabet = get_alphabet(gui_prv_path)
        # List of the letters guessed and not in the proverb
        gui_non_matches = []
        # List of the letters guessed and in the proverb
        gui_matches = []

        # Display empty guess list
        self.GuessText.setText(
            wrong_guesses_to_display(sorted(gui_non_matches)))
        # Display proverb with underscores replacing alphabet characters
        self.ProverbText.setText(
            incomplete_proverb(gui_proverb, gui_matches, gui_alphabet))

        # Check guess after player hits enter or presses OK
        def check_guess(ge):
            if already_guessed(ge, gui_non_matches):
                # incorrect guess already given, append "penalty"
                gui_non_matches.append("+1")
            elif in_proverb(ge, gui_proverb):
                # append guess to matches list
                gui_matches.append(ge)
            else:
                # append guess to non-matches list
                gui_non_matches.append(ge)

            # update guess list with the wrong guesses
            self.GuessText.setText(
                wrong_guesses_to_display(sorted(gui_non_matches)))

            # update displayed proverb with the correctly guessed characters
            gui_incomplete = incomplete_proverb(
                gui_proverb,
                gui_matches,
                gui_alphabet)
            self.ProverbText.setText(gui_incomplete)

            # update hangman image
            image = os.path.join("resources", "img",
                                 f"{len(gui_non_matches)}.png")
            self.ImageLabel.setPixmap(image)

            # check if game was won or hangman is complete
            if len(gui_non_matches) == get_max_guess_number():
                message_box(game_over,
                            lose_message + "\n\n" + gui_proverb_original)
            if complete_proverb(gui_incomplete):
                message_box(game_over,
                            win_message + "\n\n" + gui_proverb_original)

        # Get player input
        def ok_pressed():
            ge = self.PlayerInput.text().upper()
            # check validity, display error if invalid
            if len(ge) > 1 or ge not in gui_alphabet:
                message_box(input_error, invalid_character)
            else:
                check_guess(ge)
                self.PlayerInput.setFocus()
                self.PlayerInput.selectAll()

        self.OkButton.clicked.connect(ok_pressed)
        self.PlayerInput.returnPressed.connect(ok_pressed)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    # check if language was selected previously
    language_selected = os.path.join("resources", "language_selected")
    # run game if the file with the selected language exists
    # or run language selector otherwise
    if os.path.isfile(language_selected):
        with open(language_selected) as file:
            lang = file.readline()
        window = GameWindow(lang)
    else:
        window = SelectLanguage()

    window.show()
    sys.exit(app.exec_())
