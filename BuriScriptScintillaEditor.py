from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qsci import *
import os
import sys
import threading
from BuriScriptLinterForPython import run_pylint
from BuriScriptFileModel import CustomTreeView
from BuriScriptLexers import CustomLexerPython, CustomLexerSQL, NoLexer
from MySQLScintilla.MySQLScintillaMain import CustomWidget
import warnings
import re
import csv


warnings.simplefilter(action='ignore', category=FutureWarning)

check_backspace: list = []


class BuriScriptEditor(QsciScintilla):
    def __init__(self, parent_directory: str, tab_file_path_absolute: str, python_terminal_class_not_instance, parent=None):
        """Parent Directory -> home_path -> the path where BuriScript exists
           tab_file_path_name has the full file path with the file name and file extension. It is stored under
           -> self.file_to_open_in_new_tab"""

        super(BuriScriptEditor, self).__init__(parent)
        self.parent_directory = parent_directory
        self.file_to_open_in_new_tab = tab_file_path_absolute
        self.python_terminal_class = python_terminal_class_not_instance
        self.__parent = parent

        self.boolean_backspace = False
        self.backspace_deletion = ""
        self.current_margin_width = 2
        self.__parent_window = parent
        self.SendScintilla(self.SCI_SETMULTIPLESELECTION, True)
        self.SendScintilla(self.SCI_SETMULTIPASTE, 1)
        self.SendScintilla(self.SCI_SETADDITIONALSELECTIONTYPING, True)
        self.SendScintilla(self.SCI_SETINDENTATIONGUIDES, self.SC_IV_REAL)
        self.SendScintilla(self.SCI_SETTABWIDTH, 4)
        self.setFolding(self.BoxedFoldStyle)
        self.setFoldMarginColors(QColor("#111111"), QColor("#111111"))

        StandardIconSize = 16
        StandardMarginWidth = 20

        os.chdir(self.parent_directory)

        self.SendScintilla(self.SCI_SETMARGINWIDTHN, 1, 0)
        self.SendScintilla(self.SCI_SETMARGINWIDTHN, 2, StandardMarginWidth)
        self.SendScintilla(self.SCI_RGBAIMAGESETHEIGHT, StandardIconSize)
        self.SendScintilla(self.SCI_RGBAIMAGESETWIDTH, StandardIconSize)
        fldr = QImage("images_icons\\arrow_right.png")  # ImageQt(Image.open("images_icons\\arrow_right.png"))
        open_image = QImage("images_icons\\arrow_down.png") # ImageQt(Image.open("images_icons\\arrow_down.png"))
        self.SendScintilla(self.SCI_MARKERDEFINERGBAIMAGE, self.SC_MARKNUM_FOLDER, fldr)
        self.SendScintilla(self.SCI_MARKERDEFINERGBAIMAGE, self.SC_MARKNUM_FOLDEROPEN, open_image)

        self.SendScintilla(self.SCI_SETMOUSEDWELLTIME, 10)
        self.SCN_DWELLSTART.connect(self.hover)
        self.SCN_DWELLEND.connect(self.hover)

        self.SCN_MODIFIED.connect(self.modify)
        self.setFrameShape(QFrame.NoFrame)
        self.set_text_in_editor()

    def keyPressEvent(self, event):
        global check_backspace
        selected_text = self.selectedText()
        all_pairs = {
            39: "'",
            40: ")",
            34: '"',
            91: "]",
            123: "}"
        }
        try:
            text_in_editor = self.text().replace("\r", '')
            text_in_editor = text_in_editor.split("\n")
            cursor_position = self.getCursorPosition()
            current_line_text = ""
            for line_number, line in enumerate(text_in_editor):
                if line_number == cursor_position[0]:
                    current_line_text = line
                    break
            try:
                # print(current_line_text)
                # print(current_line_text[cursor_position[1] - 1] \
                # == "(", current_line_text[cursor_position[1] + 1] == ")")
                if current_line_text[cursor_position[1] - 1] == "(" and current_line_text[cursor_position[1] + 1] == ")":
                    self.boolean_backspace = True
                if event.key() == 16777219:
                    self.backspace_deletion = current_line_text[cursor_position[1] - 1]
                # if event.modifiers() == Qt.ControlModifier and event.key() == 84:
                #     """84 is letter t """
                #     self.__parent_window.tab_widget.add_new_tab()
                #     self.SendScintilla(QsciScintillaBase.SCI_LINETRANSPOSE)

                if event.modifiers() == Qt.ControlModifier and event.key() == 16777217:
                    """16777217 is tab"""
            except Exception as error:
                pass
            return super(BuriScriptEditor, self).keyPressEvent(event)
        finally:
            try:
                get_current_line = ""
                for line_number, line in enumerate(self.text().split("\n")):
                    if line_number == self.getCursorPosition()[0]:
                        get_current_line = line
                        break
                try:
                    is_character_in_front = True if len(get_current_line) == 1 else \
                        False if get_current_line[self.getCursorPosition()[1]] not in """)]}'\"\r\n :""" else True
                except IndexError:
                    is_character_in_front = True
                # WARNING: Any error in autocompletion of brackets can be caused due to the try-except of is_character
                # is_character_in_front = True
                if event.key() in all_pairs and is_character_in_front:
                    self.insert(f"{selected_text}{all_pairs[event.key()]}")
                    check_backspace.append("YES")
                    if selected_text:
                        [self.SendScintilla(QsciScintillaBase.SCI_CHARRIGHT)
                         for _ in f"{selected_text}{all_pairs[event.key()]}"]
                else: check_backspace.append(event.key())
                # print(check_backspace, event.key() == 16777219 and check_backspace[-2] == "YES")
                self.backspace_deletion = current_line_text[cursor_position[1] - 1]  # Can remove with no issues
                completion_dictionary = {
                    '"': '"',
                    "'": "'",
                    "(": ")",
                    "[": "]",
                    "{": "}"
                }
                if (self.boolean_backspace and event.key() == 16777219) and (event.key() == 16777219
                                                                             and check_backspace[-2] == "YES"):
                    """event.key() == 16777219 and check_backspace[-2] == "YES" or """
                    # print(text_in_line[cursor_position[1]]) # the above if condition has or between parenthesis
                    self.boolean_backspace = False
                    try:
                        [check_backspace.remove(x) for x in check_backspace[-1:2:-1]]
                    except Exception as error:
                        pass
                    self.SendScintilla(QsciCommand.Delete)
                    # was elif current_line_text[cursor_position[1]] == ")" \
                    #                         and event.key() == 16777219 and self.backspace_deletion == "(":
                    # if something goes wrong in delete couple-pair places -> check above elif and implement accordingly
                    # Function of self.backspace_deletion forgot (now unknown).
                elif (current_line_text[cursor_position[1]] == completion_dictionary[self.backspace_deletion]\
                        and event.key() == 16777219 and self.backspace_deletion in """([{"'""")\
                        or (current_line_text[cursor_position[1]] == ")"
                                             and event.key() == 16777219 and self.backspace_deletion == "("):
                    self.backspace_deletion = ""
                    self.SendScintilla(QsciCommand.Delete)
            except Exception:
                pass
                # print('deleted')
            from os.path import exists
            # global file_path_user_opened, home_path
            # print(file_path_user_opened, 'no')
            if os.path.isfile(self.file_to_open_in_new_tab) or self.file_to_open_in_new_tab != "":
                """with open(file_path_user_opened, "w") as file_to_write:
                    file_to_write.write(self.text().replace('\r', ''))
                    os.chdir(home_path)"""
                self.run_auto_save = threading.Thread(target=self.write_to_file_thread,
                                                      args=[self.file_to_open_in_new_tab]
                                                      )
                self.run_auto_save.start()
                os.chdir(self.parent_directory)  # warning: crash may be caused due to this, if suspect is -> (auto-save-thread)
                with open('images_icons\\previous_data_file.txt', 'w') as file_to_w:
                    file_to_w.write(self.file_to_open_in_new_tab)
            self.check_margin_width()
            # self.run_pylint_on_new_thread()
            if event.key() == 16777216:
                try:
                    if self.__parent_window.findChildren(CustomWidget):
                        self.setFocus()
                        self.__parent_window.customwidget.close()
                    if self.__parent_window.findChildren(self.python_terminal_class):
                        self.setFocus()
                        self.__parent_window.python_terminal_window.close()
                        self.__parent_window.python_terminal_window.close_all_widgets_and_exit()
                        # runs when escape is pressed
                except BaseException as error:
                    print(error)

    def check_margin_width(self):
        number_of_lines = len(self.text().split('\n'))
        digits = len(str(number_of_lines))
        self.setMarginWidth(0, "0"*(digits + 1))
        self.current_margin_width = digits = len(str(number_of_lines))

    def set_fold(self, prev, line, fold, full):
        if prev[0] >= 0:
            f_max = max(fold, prev[1])
            for item in range(prev[0], line + 1):
                self.SendScintilla(self.SCI_SETFOLDLEVEL, item,
                                   f_max | (0, self.SC_FOLDLEVELHEADERFLAG)[item + 1 < full])

    def line_empty(self, line):
        return self.SendScintilla(self.SCI_GETLINEENDPOSITION, line) \
            <= self.SendScintilla(self.SCI_GETLINEINDENTPOSITION, line)

    def modify(self, position, modificationType, text, length, linesAdded,
               line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        full = self.SC_MOD_INSERTTEXT | self.SC_MOD_DELETETEXT
        if ~modificationType & full == full:
            return
        prev = [-1, 0]
        full = self.SendScintilla(self.SCI_GETLINECOUNT)
        lbgn = self.SendScintilla(self.SCI_LINEFROMPOSITION, position)
        lend = self.SendScintilla(self.SCI_LINEFROMPOSITION, position + length)
        for item in range(max(lbgn - 1, 0), -1, -1):
            if ((item == 0) or not self.line_empty(item)):
                lbgn = item
                break
        for item in range(min(lend + 1, full), full + 1):
            if ((item == full) or not self.line_empty(item)):
                lend = min(item + 1, full)
                break
        for item in range(lbgn, lend):
            if (self.line_empty(item)):
                if (prev[0] == -1):
                    prev[0] = item
            else:
                fold = self.SendScintilla(self.SCI_GETLINEINDENTATION, item)
                fold //= self.SendScintilla(self.SCI_GETTABWIDTH)
                self.set_fold(prev, item - 1, fold, full)
                self.set_fold([item, fold], item, fold, full)
                prev = [-1, fold]
        self.set_fold(prev, lend - 1, 0, full)

    def hover(self, position, xpos, ypos):
        StandardMarginWidth = (self.current_margin_width + 1) * 20
        mask = self.SendScintilla(self.SCI_GETMARGINMASKN, 2)
        mask = (mask | self.SC_MASK_FOLDERS, mask & ~self.SC_MASK_FOLDERS) \
            [xpos > StandardMarginWidth]
        self.SendScintilla(self.SCI_SETMARGINMASKN, 2, mask)

    def write_to_file_thread(self, file_path):
        try:
            with open(file_path, "w", encoding='utf8') as file_to_write:
                file_to_write.write(self.text().replace('\r', '').replace("\t", "    "))
                os.chdir(self.parent_directory)
                sys.exit()
        except Exception as error:
            print(error, 'FROM SCINTILLA COMPONENT EDITOR  WRITE TO FILE THREAD')

    def run_pylint_on_new_thread(self):
        try:
            os.chdir(self.get_file_path_with_file_name(self.file_to_open_in_new_tab))
            all_instances_of_errors_list: list[list] = run_pylint(
                                                                  filename=str(os.path.basename(
                                                                      self.file_to_open_in_new_tab)))
            for line_number_start, column_start, line_number_end, column_end in all_instances_of_errors_list:
                print(line_number_start, column_start, line_number_end, column_end )
                self.clearIndicatorRange(0, 0, QsciScintilla.SCI_GETLINECOUNT, QsciScintilla.SCI_GETLINECOUNT,
                                                         2)
                self.fillIndicatorRange(line_number_start - 1, column_start, line_number_end, column_end, 2)
        except BaseException as error:
            print(error.__class__.__name__, error)

    @staticmethod
    def get_file_path_with_file_name(absolute_file_path):
        """function returns same as the staticmethod get_file_path_and_file_name in CustomMainWindow"""
        return os.path.dirname(absolute_file_path)

    def run_basic_configuration(self) -> None:
        settings_data = self.settings_editor()
        self.setUtf8(True)  # Set encoding to UTF-8
        self.setIndentationsUseTabs(False)  # can cause IndentationError. Column parameter messages are logged due to
        # this. Jedi auto-complete also doesn't work.
        self.setIndentationGuides(True)
        self.setTabWidth(4)
        self.setCaretForegroundColor(QColor("white"))
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#333333"))
        self.setAutoIndent(True)
        self.setMarginType(0, self.NumberMargin)
        self.check_margin_width()
        self.margin_font = QFont(settings_data['FONT'])
        self.margin_font.setPointSize(int(settings_data['FONT_SIZE']))
        self.setMarginsFont(self.margin_font)
        self.setMarginsForegroundColor(QColor("white"))
        self.setMarginsBackgroundColor(QColor("#111111"))
        self.setSelectionBackgroundColor(QColor("#033870"))
        self.setBraceMatching(1)
        self.setMatchedBraceBackgroundColor(QColor("#38543f"))
        self.setUnmatchedBraceBackgroundColor(QColor("#6b2c2e"))
        self.setMatchedBraceForegroundColor(QColor("white"))
        self.setUnmatchedBraceForegroundColor(QColor("white"))

    def run_sql_lexer(self):
        self.__lexer = CustomLexerSQL(self)
        self.__lexer.setFoldCompact(False)
        self.__lexer.setFoldComments(True)
        self.__lexer.setFoldAtElse(True)
        self.__lexer.setFoldOnlyBegin(True)
        self.__lexer.setDefaultFont(QFont(self.settings_editor()['FONT']))
        self.__lexer.setDefaultColor(QColor("white"))
        self.__lexer.setDefaultPaper(QColor("#111111"))
        self.setLexer(self.__lexer)
        lexer_color_code = \
            {
                self.__lexer.Default: "white",
                self.__lexer.Comment: "#7d7d7d",
                self.__lexer.CommentLine: "#7d7d7d",
                self.__lexer.CommentDoc: "#7d7d7d",
                self.__lexer.Number: "#6b6fe3",
                self.__lexer.Keyword: "#56A3FA",
                self.__lexer.DoubleQuotedString: "#E2EA83",
                self.__lexer.SingleQuotedString: "#E2EA83",
                self.__lexer.PlusKeyword: "#00758f",
                self.__lexer.PlusPrompt: "#56A3FA",
                self.__lexer.Operator: "#56A3FA",
                self.__lexer.Identifier: "white",
                self.__lexer.PlusComment: "#7d7d7d",
                self.__lexer.CommentLineHash: "#7d7d7d",
                self.__lexer.CommentDocKeyword: "#7d7d7d",
                self.__lexer.CommentDocKeywordError: "#7d7d7d",
                self.__lexer.QuotedIdentifier: "white",
                self.__lexer.QuotedOperator: "#00758f",
                self.__lexer.KeywordSet5: "#32d929"
            }
        for enum, color_code in lexer_color_code.items():
            self.__lexer.setColor(QColor(color_code), enum)
            self.__lexer.setFont(QFont(self.settings_editor()['FONT']), enum)
        self.__lexer.setFont(QFont("Consolas"), self.__lexer.Operator)
        self.run_basic_configuration()

    def run_python_lexer(self):
        self.__lexer = CustomLexerPython(self)
        self.__lexer.setFoldQuotes(True)
        self.__lexer.setFoldCompact(False)
        self.__lexer.setFoldComments(True)
        self.__lexer.setDefaultPaper(QColor("#111111"))
        self.__lexer.setDefaultColor(QColor("white"))
        settings_data = self.settings_editor()
        self.__lexer.setDefaultFont(QFont(settings_data['FONT']))
        self.operator_font = QFont("Consolas")
        self.operator_font.setPointSize(int(settings_data['FONT_SIZE']) + 2)
        self.change_font_color_type(self.__lexer, "#CF8E6D", QsciLexerPython.Keyword) #dc5cff
        self.change_font_color_type(self.__lexer, "#a1e5ff", QsciLexerPython.Number)
        self.change_font_color_type(self.__lexer, "#bff765", QsciLexerPython.Comment)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.UnclosedString)
        self.change_font_color_type(self.__lexer, "#bff765", QsciLexerPython.CommentBlock)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.DoubleQuotedString) #23a608
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.SingleQuotedString)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.TripleDoubleQuotedString)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.TripleSingleQuotedString)
        self.change_font_color_type(self.__lexer, "#54A4EF", QsciLexerPython.FunctionMethodName)
        self.change_font_color_type(self.__lexer, "white", QsciLexerPython.Operator)
        self.__lexer.setFont(self.operator_font, QsciLexerPython.Operator)
        self.change_font_color_type(self.__lexer, "white", QsciLexerPython.Identifier)  # #68CEFE - the default blue color
        self.change_font_color_type(self.__lexer, "#9a9af5", QsciLexerPython.HighlightedIdentifier)  #8e57fa
        self.change_font_color_type(self.__lexer, "#f7ff57", QsciLexerPython.Decorator)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.DoubleQuotedFString)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.SingleQuotedFString)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.TripleDoubleQuotedFString)
        self.change_font_color_type(self.__lexer, "#6bcf6e", QsciLexerPython.TripleSingleQuotedFString)
        self.change_font_color_type(self.__lexer, "#65baa9", QsciLexerPython.ClassName)
        # change_font_color_type(self.__lexer, "red", QsciLexerPython.Inconsistent)
        self.__lexer.setPaper(QColor("#660f00"), QsciLexerPython.UnclosedString)
        self.setLexer(self.__lexer)
        self.run_basic_configuration()
        """
        ----------------------------------------AUTOCOMPLETION------------------------------------------------------

        """
        self.__api: QsciAPIs = QsciAPIs(self.__lexer)
        os.chdir(self.parent_directory)
        with open("autocompletions.txt", "r") as pre_filled_auto_completions:
            autocomplete_words = pre_filled_auto_completions.readlines()
            pattern = re.compile(r"[^\n]")
            without_new_line_autocomplete_words = []
            for x in autocomplete_words:
                delete_new_line = pattern.findall(x)
                without_new_line_autocomplete_words.append(''.join(delete_new_line))
            without_new_line_autocomplete_words = list(set(without_new_line_autocomplete_words))
            for autocomplete_word in without_new_line_autocomplete_words:
                self.__api.add(autocomplete_word)
            self.__api.prepare()
        self.setCallTipsStyle(QsciScintilla.CallTipsNone)
        self.setCallTipsVisible(-1)
        self.setCallTipsPosition(QsciScintilla.CallTipsBelowText)
        self.setCallTipsBackgroundColor(QColor("#323437"))
        self.setCallTipsForegroundColor(QColor("white"))
        self.setCallTipsHighlightColor(QColor("#0060f0"))
        self.setCallTipsVisible(False)
        """


        """
        self.autoCompletionSource()
        self.setAutoCompletionSource(QsciScintilla.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(True)
        self.setAutoCompletionReplaceWord(True)

        """ Auto completions Python """
        import autocompletions_python as autopy
        self.__auto_complete = autopy.AutoCompletion("This_is_a_file.py", self.__api, self)
        self.__auto_complete.finished.connect(self.load_autocomplete)
        self.cursorPositionChanged.connect(self._cursor_position_changed)

    def run_no_lexer(self):
        self.__lexer = NoLexer(self)
        font = QFont(self.settings_editor()['FONT'])
        font_size: int = int(self.settings_editor()['FONT_SIZE'])
        font.setPointSize(font_size)
        self.__lexer.setDefaultFont(font)
        self.__lexer.setDefaultColor(QColor("white"))
        self.__lexer.setDefaultPaper(QColor("#111111"))
        self.setLexer(self.__lexer)
        self.run_basic_configuration()

    def set_text_in_editor(self):
        if not os.path.isfile(self.file_to_open_in_new_tab): return
        with open(self.file_to_open_in_new_tab, 'r') as f_read:
            text_content = []
            for line in f_read:
                text_content.append(line)
            self.setText(''.join(text_content))
            number_of_lines = len(str(len(self.text().split("\n")))) + 1
            self.setMarginWidth(0, "0" * number_of_lines)

    def settings_editor(self):
        os.chdir(self.parent_directory)
        with open('images_icons\\settings.csv', mode='r') as file:
            csv_file = csv.reader(file)
            data = {}
            for lines in csv_file:
                data[lines[0]] = lines[1]
        return data

    def change_font_color_type(self, lexer_name, font_color_hex, enum_to_change):
        lexer_name.setColor(QColor(f'{font_color_hex}'), enum_to_change)
        settings_data = self.settings_editor()
        editor_font = QFont(settings_data['FONT'])
        editor_font.setPointSize(int(settings_data['FONT_SIZE']))
        lexer_name.setFont(editor_font, enum_to_change)

    def load_autocomplete(self):
        pass

    def _cursor_position_changed(self, line: int, index: int) -> None:
        self.__auto_complete.get_completions(line + 1, index, self.text())

