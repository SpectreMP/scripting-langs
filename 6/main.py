import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel,
    QFileDialog, QComboBox, QLineEdit, QHBoxLayout, QMessageBox,
    QDoubleSpinBox
)
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DataAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ данных")
        self.setGeometry(100, 100, 800, 600)
        self.data = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Основные элементы управления
        controls_layout = QHBoxLayout()
        self.load_button = QPushButton("Загрузить CSV")
        self.load_button.clicked.connect(self.load_csv)
        self.graph_type = QComboBox()
        self.graph_type.addItems(
            ["Линейный график", "Гистограмма", "Круговая диаграмма"])
        self.graph_type.currentIndexChanged.connect(self.on_graph_type_changed)

        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(self.graph_type)
        layout.addLayout(controls_layout)

        # График
        self.canvas = FigureCanvas(Figure(figsize=(10, 6)))
        layout.addWidget(self.canvas)

        # Панель ввода данных
        self.input_layout = QHBoxLayout()

        # Создаем все поля ввода
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.date_input.setValidator(QRegExpValidator(
            QRegExp(r"^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$")))

        self.value1_input = QDoubleSpinBox()
        self.value2_input = QDoubleSpinBox()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Категория")

        # Кнопка добавления
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_value)

        # Добавляем все в layout
        for widget in [
            (QLabel("Дата:"), self.date_input),
            (QLabel("Значение 1:"), self.value1_input),
            (QLabel("Значение 2:"), self.value2_input),
            (QLabel("Категория:"), self.category_input),
            (self.add_button, None)
        ]:
            self.input_layout.addWidget(widget[0])
            if widget[1]:
                self.input_layout.addWidget(widget[1])

        layout.addLayout(self.input_layout)
        self.update_visible_fields()

    def update_visible_fields(self):
        # Скрываем все поля
        for i in range(self.input_layout.count()):
            widget = self.input_layout.itemAt(i).widget()
            if widget:
                widget.hide()

        # Показываем нужные поля
        graph_type = self.graph_type.currentText()
        if graph_type == "Линейный график":
            fields = [self.input_layout.itemAt(0).widget(), self.date_input,
                      self.input_layout.itemAt(2).widget(), self.value1_input]
        elif graph_type == "Гистограмма":
            fields = [self.input_layout.itemAt(0).widget(), self.date_input,
                      self.input_layout.itemAt(4).widget(), self.value2_input]
        else:  # Круговая диаграмма
            fields = [self.input_layout.itemAt(
                6).widget(), self.category_input]

        fields.append(self.add_button)
        for widget in fields:
            widget.show()

    def add_value(self):
        if self.data is None:
            self.data = pd.DataFrame(
                columns=["Date", "Value1", "Value2", "Category"])

        try:
            new_data = {
                "Date": self.date_input.text() or "2024-01-01",
                "Value1": self.value1_input.value(),
                "Value2": self.value2_input.value(),
                "Category": self.category_input.text() or "Default"
            }

            self.data = pd.concat(
                [self.data, pd.DataFrame([new_data])], ignore_index=True)
            self.plot_graph()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def plot_graph(self):
        if self.data is None or self.data.empty:
            return

        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)

        try:
            graph_type = self.graph_type.currentText()

            if graph_type == "Линейный график":
                ax.plot(self.data["Date"], self.data["Value1"], marker='o')
                ax.set_title("Значения по датам")
                ax.tick_params(axis='x', rotation=45)

            elif graph_type == "Гистограмма":
                dates = pd.to_datetime(self.data["Date"])
                ax.bar(dates, self.data["Value2"])
                ax.set_title("Значения Value2 по датам")
                ax.tick_params(axis='x', rotation=45)

            else:  # Круговая диаграмма
                counts = self.data["Category"].value_counts()
                if not counts.empty:
                    ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
                    ax.set_title("Распределение по категориям")

            self.canvas.figure.tight_layout()
            self.canvas.draw()

        except Exception as e:
            QMessageBox.warning(self, "Ошибка отрисовки", str(e))

    def load_csv(self):
        try:
            filename, _ = QFileDialog.getOpenFileName(
                self, "Открыть CSV", "", "CSV files (*.csv)")
            if filename:
                self.data = pd.read_csv(filename)
                self.plot_graph()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def on_graph_type_changed(self):
        self.update_visible_fields()
        self.plot_graph()


def main():
    app = QApplication(sys.argv)
    window = DataAnalysisApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
