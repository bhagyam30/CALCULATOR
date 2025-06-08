import sys
import math
import re
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLineEdit, QPushButton,
    QSizePolicy, QLabel, QVBoxLayout, QHBoxLayout, QTextEdit,
    QTabWidget, QComboBox, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ScientificCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator Converter Graph")
        self.setGeometry(100, 100, 1000, 600)
        self.degrees_mode = True
        self.memory = 0
        self.create_ui()

    def create_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Left side: Tabs for Calculator and Unit Converter
        self.tabs = QTabWidget()
        self.tabs.setMinimumWidth(700)
        main_layout.addWidget(self.tabs)

        # Calculator tab
        self.calc_tab = QWidget()
        self.tabs.addTab(self.calc_tab, "Calculator")
        self.calc_layout = QVBoxLayout()
        self.calc_tab.setLayout(self.calc_layout)

        # Calculator display and buttons
        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(60)
        self.display.setFont(QFont("Arial", 22))
        self.display.setStyleSheet("font-size: 22px; color: #ffffff; background-color: #2e2e2e;")
        self.calc_layout.addWidget(self.display)

        self.mode_label = QLabel("Mode: Degrees")
        self.mode_label.setStyleSheet("color: #aaaaaa; font-size: 16px;")
        self.calc_layout.addWidget(self.mode_label)

        # Buttons grid
        self.layout_buttons = QGridLayout()
        self.calc_layout.addLayout(self.layout_buttons)

        button_style = """
            QPushButton {
                font-size: 22px;
                padding: 20px;
                min-width: 80px;
                min-height: 60px;
                color: #ffffff;
                background-color: #3a3a3a;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """

        buttons = {
            '7': (2, 0), '8': (2, 1), '9': (2, 2), '/': (2, 3), 'C': (2, 4),
            '4': (3, 0), '5': (3, 1), '6': (3, 2), '*': (3, 3), '(': (3, 4),
            '1': (4, 0), '2': (4, 1), '3': (4, 2), '-': (4, 3), ')': (4, 4),
            '0': (5, 0), '.': (5, 1), '=': (5, 2), '+': (5, 3), 'sqrt': (5, 4),
            'sin': (6, 0), 'cos': (6, 1), 'tan': (6, 2), 'log': (6, 3), 'ln': (6, 4),
            'M+': (7, 0), 'MR': (7, 1), 'MC': (7, 2), '^': (7, 3), 'exp': (7, 4),
        }

        for btnText, pos in buttons.items():
            button = QPushButton(btnText)
            button.setStyleSheet(button_style)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.clicked.connect(self.button_clicked)
            self.layout_buttons.addWidget(button, pos[0], pos[1])

        # Bottom buttons: Mode toggle, Clear History, Graph
        bottom_layout = QHBoxLayout()
        self.calc_layout.addLayout(bottom_layout)

        self.toggle_button = QPushButton("Toggle Deg/Rad")
        self.toggle_button.setStyleSheet("background-color: #444; color: white; font-size: 18px; padding: 10px;")
        self.toggle_button.clicked.connect(self.toggle_mode)
        bottom_layout.addWidget(self.toggle_button)

        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.setStyleSheet("background-color: #880000; color: white; font-size: 18px; padding: 10px;")
        self.clear_history_button.clicked.connect(self.clear_history)
        bottom_layout.addWidget(self.clear_history_button)

        self.graph_button = QPushButton("Graph")
        self.graph_button.setStyleSheet("background-color: #004488; color: white; font-size: 18px; padding: 10px;")
        self.graph_button.clicked.connect(self.open_graph_window)
        bottom_layout.addWidget(self.graph_button)

        # History Panel on right side of calculator tab
        self.history_panel = QTextEdit()
        self.history_panel.setReadOnly(True)
        self.history_panel.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-size: 16px;")
        self.history_panel.setFixedWidth(280)
        main_layout.addWidget(self.history_panel)

        # Unit Converter tab
        self.converter_tab = UnitConverter()
        self.tabs.addTab(self.converter_tab, "Unit Converter")

    def toggle_mode(self):
        self.degrees_mode = not self.degrees_mode
        mode_text = "Degrees" if self.degrees_mode else "Radians"
        self.mode_label.setText(f"Mode: {mode_text}")

    def clear_history(self):
        self.history_panel.clear()
        open("calc_history.txt", "w").close()

    def button_clicked(self):
        sender = self.sender()
        text = sender.text()

        if text == 'C':
            self.display.clear()
        elif text == '=':
            self.evaluate_expression()
        elif text == 'M+':
            try:
                value = float(self.display.text())
                self.memory += value
            except:
                self.display.setText("Error")
        elif text == 'MR':
            self.display.setText(str(self.memory))
        elif text == 'MC':
            self.memory = 0
            self.display.clear()
        else:
            self.display.setText(self.display.text() + text)

    def evaluate_expression(self):
        try:
            expr = self.display.text()
            expr = self.prepare_expression(expr)
            result = eval(expr, {"math": math, "__builtins__": {}})
            self.display.setText(str(result))
            self.save_history(expr, result)
        except Exception as e:
            self.display.setText("Error")

    def prepare_expression(self, expr):
        expr = expr.replace('^', '**')
        expr = expr.replace('sqrt', 'math.sqrt')
        expr = expr.replace('log', 'math.log10')
        expr = expr.replace('ln', 'math.log')
        expr = expr.replace('exp', 'math.exp')

        def convert(match):
            func = match.group(1)
            val = match.group(2)
            if self.degrees_mode:
                return f'math.{func}(math.radians({val}))'
            else:
                return f'math.{func}({val})'

        expr = re.sub(r'(sin|cos|tan)\(([^()]*)\)', convert, expr)
        return expr

    def save_history(self, expression, result):
        line = f"{expression} = {result}"
        self.history_panel.append(line)
        with open("calc_history.txt", "a") as file:
            file.write(line + "\n")

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self.evaluate_expression()
        elif key == Qt.Key_Backspace:
            self.display.setText(self.display.text()[:-1])
        else:
            text = event.text()
            # Only allow valid chars: numbers, operators, parentheses, dot
            if text in "0123456789.+-*/^()":
                self.display.setText(self.display.text() + text)

    def open_graph_window(self):
        self.graph_win = GraphWindow(self.degrees_mode)
        self.graph_win.show()


class UnitConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Dropdown for conversion types
        self.conv_type = QComboBox()
        self.conv_type.addItems(["Temperature", "Length", "Weight"])
        self.conv_type.currentIndexChanged.connect(self.update_units)
        layout.addWidget(self.conv_type)

        # Input unit dropdown & input box
        hbox1 = QHBoxLayout()
        self.unit_from = QComboBox()
        self.unit_to = QComboBox()
        self.input_val = QLineEdit()
        self.input_val.setPlaceholderText("Enter value")
        hbox1.addWidget(QLabel("From:"))
        hbox1.addWidget(self.unit_from)
        hbox1.addWidget(QLabel("To:"))
        hbox1.addWidget(self.unit_to)
        hbox1.addWidget(self.input_val)
        layout.addLayout(hbox1)

        # Convert button
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_units)
        layout.addWidget(self.convert_button)

        # Result label
        self.result_label = QLabel("")
        self.result_label.setFont(QFont("Arial", 18))
        layout.addWidget(self.result_label)

        self.units_data = {
            "Temperature": ["Celsius", "Fahrenheit", "Kelvin"],
            "Length": ["Meter", "Centimeter", "Inch", "Foot"],
            "Weight": ["Kilogram", "Gram", "Pound", "Ounce"]
        }

        self.update_units()

    def update_units(self):
        ctype = self.conv_type.currentText()
        units = self.units_data[ctype]
        self.unit_from.clear()
        self.unit_to.clear()
        self.unit_from.addItems(units)
        self.unit_to.addItems(units)
        self.result_label.setText("")

    def convert_units(self):
        ctype = self.conv_type.currentText()
        from_unit = self.unit_from.currentText()
        to_unit = self.unit_to.currentText()
        val_str = self.input_val.text()

        try:
            val = float(val_str)
        except:
            self.result_label.setText("Invalid input")
            return

        # Temperature conversion
        if ctype == "Temperature":
            res = self.convert_temperature(val, from_unit, to_unit)
        elif ctype == "Length":
            res = self.convert_length(val, from_unit, to_unit)
        else:  # Weight
            res = self.convert_weight(val, from_unit, to_unit)

        self.result_label.setText(f"{val} {from_unit} = {res:.4f} {to_unit}")

    def convert_temperature(self, val, from_unit, to_unit):
        # Convert from input unit to Celsius first
        if from_unit == "Celsius":
            c = val
        elif from_unit == "Fahrenheit":
            c = (val - 32) * 5 / 9
        elif from_unit == "Kelvin":
            c = val - 273.15
        else:
            return None

        # Convert Celsius to target unit
        if to_unit == "Celsius":
            return c
        elif to_unit == "Fahrenheit":
            return c * 9 / 5 + 32
        elif to_unit == "Kelvin":
            return c + 273.15
        else:
            return None

    def convert_length(self, val, from_unit, to_unit):
        # Convert all to meters first
        factors = {
            "Meter": 1,
            "Centimeter": 0.01,
            "Inch": 0.0254,
            "Foot": 0.3048
        }
        if from_unit not in factors or to_unit not in factors:
            return None
        meters = val * factors[from_unit]
        return meters / factors[to_unit]

    def convert_weight(self, val, from_unit, to_unit):
        # Convert all to kilograms first
        factors = {
            "Kilogram": 1,
            "Gram": 0.001,
            "Pound": 0.45359237,
            "Ounce": 0.02834952
        }
        if from_unit not in factors or to_unit not in factors:
            return None
        kg = val * factors[from_unit]
        return kg / factors[to_unit]


class GraphWindow(QWidget):
    def __init__(self, degrees_mode=True):
        super().__init__()
        self.setWindowTitle("Function Grapher")
        self.setGeometry(200, 200, 700, 500)
        self.degrees_mode = degrees_mode
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        input_layout = QHBoxLayout()
        layout.addLayout(input_layout)

        self.func_input = QLineEdit()
        self.func_input.setPlaceholderText("Enter function of x, e.g. sin(x), cos(x), x**2")
        self.func_input.setFont(QFont("Arial", 16))
        input_layout.addWidget(QLabel("f(x) = "))
        input_layout.addWidget(self.func_input)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_function)
        input_layout.addWidget(self.plot_button)

        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

    def plot_function(self):
        expr = self.func_input.text().strip()
        if not expr:
            QMessageBox.warning(self, "Input Error", "Please enter a function to plot.")
            return

        x_vals = np.linspace(-10, 10, 400)
        y_vals = []

        # Prepare the expression safely for numpy vectorized eval
        # Allowed names
        allowed_names = {
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "log": np.log10,
            "ln": np.log,
            "exp": np.exp,
            "sqrt": np.sqrt,
            "pi": np.pi,
            "e": np.e,
            "abs": np.abs,
            "x": x_vals
        }

        # If degrees mode, convert x to radians inside trig funcs
        def safe_eval(expr, x):
            # Replace sin(...), cos(...), tan(...) with versions that handle degrees if needed
            # We replace sin(x) with sin(radians(x)) if degrees_mode
            # but since x_vals are numpy arrays, convert in vectorized way

            # We'll just define our own sin, cos, tan that do this:

            def sin_func(z):
                return np.sin(np.radians(z)) if self.degrees_mode else np.sin(z)

            def cos_func(z):
                return np.cos(np.radians(z)) if self.degrees_mode else np.cos(z)

            def tan_func(z):
                return np.tan(np.radians(z)) if self.degrees_mode else np.tan(z)

            local_dict = {
                "sin": sin_func,
                "cos": cos_func,
                "tan": tan_func,
                "log": np.log10,
                "ln": np.log,
                "exp": np.exp,
                "sqrt": np.sqrt,
                "pi": np.pi,
                "e": np.e,
                "abs": np.abs,
                "x": x
            }

            return eval(expr, {"__builtins__": {}}, local_dict)

        try:
            y_vals = safe_eval(expr, x_vals)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Invalid function or error:\n{e}")
            return

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(x_vals, y_vals)
        ax.set_title(f"y = {expr}")
        ax.grid(True)
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = ScientificCalculator()
    calc.show()
    sys.exit(app.exec_())
