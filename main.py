import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QWidget, QApplication, QLabel, QLineEdit, QPushButton, \
    QTableWidgetItem, QComboBox, QMessageBox

QUERY = "SELECT author, title, year, publisher, genre FROM inf_about_book"


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("UI1.ui", self)

        global QUERY

        self.con = sqlite3.connect('books.db')
        self.cur = self.con.cursor()

        self.setWindowTitle('Электронная библиотека')

        self.pushButton.clicked.connect(lambda: self.choose(QUERY))
        self.pushButton_2.clicked.connect(self.update_form)
        self.pushButton_3.clicked.connect(self.filter_form)

    def update_form(self):
        self.second_form = SecondForm()
        self.second_form.show()

    def filter_form(self):
        self.third_form = Filtration()
        self.third_form.show()

    def choose(self, query):
        res = self.cur.execute(query).fetchall()
        if not res:
            self.statusBar().showMessage(
                'Ничего не нашлось, нажмите кнопку "Обновить библиотеку", чтобы добавить книги')
            return
        else:
            self.statusBar().showMessage('')
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setMaximumWidth(527)
            for i, row in enumerate(res):
                self.tableWidget.setRowCount(
                    self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(
                        i, j, QTableWidgetItem(str(elem)))
            self.tableWidget.setHorizontalHeaderLabels(['Автор', 'Книга', 'Год', 'Издательство', 'Жанр'])


class SecondForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(282, 200, 350, 350)
        self.setWindowTitle('Обновить данные')

        self.labels = [QLabel(self) for _ in range(5)]
        self.buttn = [QPushButton(self) for _ in range(3)]

        self.bd_list = ['Фамилия автора:', 'Название книги:', 'Год издания:', 'Издатель книги:', 'Жанр произведения:']
        self.name_btn_list = ['Загрузить', 'Удалить по названию', 'Обновить по id']
        self.wy = 10
        self.by = 210

        for i in range(5):
            self.labels[i].setText(self.bd_list[i])
            self.labels[i].resize(120, 30)
            self.labels[i].move(10, self.wy)
            self.wy += 40

        for i in range(3):
            self.buttn[i].move(10, self.by)
            self.buttn[i].setText(self.name_btn_list[i])
            self.buttn[i].resize(120, 25)
            self.buttn[i].clicked.connect(self.define_btn)
            self.by += 40

        self.list_genres = QComboBox(self)
        self.list_genres.resize(100, 22)
        self.list_genres.move(140, 175)
        self.con = sqlite3.connect("books.db")
        self.cur = self.con.cursor()
        result = self.cur.execute("""SELECT title FROM genres""").fetchall()
        for res in result:
            self.list_genres.addItem(res[0])

        self.author = QLineEdit(self)
        self.author.move(140, 15)
        self.author.resize(100, 22)

        self.title = QLineEdit(self)
        self.title.move(140, 55)
        self.title.resize(100, 22)

        self.year = QLineEdit(self)
        self.year.move(140, 95)
        self.year.resize(100, 22)

        self.publisher = QLineEdit(self)
        self.publisher.move(140, 135)
        self.publisher.resize(100, 22)

        self.title_delete = QLineEdit(self)
        self.title_delete.move(140, 252)
        self.title_delete.resize(100, 22)

        self.update_edit = QLineEdit(self)
        self.update_edit.move(140, 292)
        self.update_edit.resize(22, 22)

        self.window_error = QLabel(self)
        self.window_error.move(10, 330)
        self.window_error.resize(300, 22)

    def update(self):
        if self.update_edit.text() == '' or self.author.text() == '' or self.title.text() == '' or (
                self.year.text() == '' or self.year.text().isalpha()) or self.publisher.text() == '':
            self.window_error.setText('Неверно заполнена форма')
        else:
            self.window_error.setText('')
            query = "UPDATE inf_about_book SET author = '{}', title = '{}', " \
                    "year = '{}', publisher = '{}', genre = '{}' WHERE id = {}".format(
                self.author.text(), self.title.text(), self.year.text(), self.publisher.text(),
                self.list_genres.currentText(), int(self.update_edit.text()))
            self.cur.execute(query)
            self.con.commit()
            self.window().close()

    def load(self):
        if self.author.text() == '' or self.title.text() == '' or (
                self.year.text() == '' or self.year.text().isalpha()) or self.publisher.text() == '':
            self.window_error.setText('Неверно введена форма, попробуйте заполнить заново')
            qline_list = [self.author, self.title, self.year, self.publisher]
            for i in range(4):
                qline_list[i].setText('')
        else:
            self.window_error.setText('')
            order_book = "INSERT INTO inf_about_book(author, title, year, publisher, genre) " \
                         "VALUES('{}','{}', '{}', '{}', '{}')".format(
                self.author.text(), self.title.text(), self.year.text(), self.publisher.text(),
                self.list_genres.currentText())
            self.cur.execute(order_book).fetchall()
            self.con.commit()
            self.window().close()

    def delete(self):
        title_list = []
        for title in self.cur.execute("""SELECT title FROM inf_about_book""").fetchall():
            title_list.append(title[0])
        if self.title_delete.text() in title_list:
            valid = QMessageBox.question(
                self, '', "Действительно удалить книгу '{}'".format(self.title_delete.text()),
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                order_delete = "DELETE from inf_about_book WHERE title = '{}'".format(self.title_delete.text())
                self.cur.execute(order_delete)
                self.con.commit()
                self.window().close()
        else:
            self.window_error.setText('Неверно введена форма, попробуйте заполнить заново')

    def define_btn(self):
        order = self.sender().text()
        if order == 'Создать таблицу':
            self.create_table()

        elif order == 'Загрузить':
            self.load()

        elif order == 'Удалить по названию':
            self.delete()

        elif order == 'Обновить по id':
            self.update()


class Filtration(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(400, 200, 350, 200)
        self.setWindowTitle('Фильтрация библиотеки')

        self.con = sqlite3.connect("books.db")
        self.cur = self.con.cursor()

        self.inf_about_book_list = {'Автор': 'author', 'Книга': 'title', 'Издатель': 'publisher',
                                    'Жанр': 'genre'}

        self.combobox1 = QComboBox(self)
        self.combobox1.move(20, 50)
        self.combobox1.resize(150, 25)
        list_a = ['Автор', 'Книга', 'Издатель', 'Жанр', 'Показать всё']
        for i in list_a:
            self.combobox1.addItem(i)

        self.combobox2 = QComboBox(self)
        self.combobox2.move(180, 50)
        self.combobox2.resize(150, 25)

        self.push_btn = QPushButton(self)
        self.push_btn.resize(170, 60)
        self.push_btn.move(90, 100)
        self.push_btn.setText('Обновить данные')
        self.push_btn.clicked.connect(self.filtrations)

    def update_combobox2(self):
        self.combobox2.clear()
        query = "SELECT {} FROM inf_about_book".format(self.inf_about_book_list[self.combobox1.currentText()])
        result = self.cur.execute(query).fetchall()
        for res in result:
            self.combobox2.addItem(res[0])

    def filtrations(self):
        global QUERY
        self.push_btn.setText('Обновить библиотеку')
        if self.combobox1.currentText() and self.combobox2.currentText():
            QUERY = "SELECT author, title, year, publisher, genre from inf_about_book WHERE {} = '{}'".format(
                self.inf_about_book_list[self.combobox1.currentText()], self.combobox2.currentText())
            self.window().close()
            return QUERY
        elif self.combobox1.currentText() == 'Показать всё':
            self.combobox2.hide()
            QUERY = "SELECT * from inf_about_book"
            self.window().close()
            return QUERY
        else:
            self.combobox2.clear()
            query = "SELECT {} FROM inf_about_book".format(self.inf_about_book_list[self.combobox1.currentText()])
            result = self.cur.execute(query).fetchall()
            for res in result:
                self.combobox2.addItem(res[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
