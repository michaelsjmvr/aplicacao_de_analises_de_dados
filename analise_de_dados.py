# Importando as bibliotecas necessárias
import sys
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit
from PySide6.QtGui import QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Classe para criar um widget que exibe gráficos do Matplotlib
class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = Figure()  # Cria uma figura Matplotlib
        self.canvas = FigureCanvas(self.figure)  # Cria um canvas para exibir a figura
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

# Classe principal da aplicação
class DataAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aplicação de Análise de Dados")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        # Criar a interface do usuário
        central_widget = QWidget()
        layout = QVBoxLayout()

        self.add_data_button = QPushButton("Adicionar no Banco de Dados")  # Botão para adicionar dados ao banco de dados
        self.load_data_button = QPushButton("Carregar Dados")  # Botão para carregar dados do banco de dados
        self.clear_data_button = QPushButton("Limpar Banco de Dados")  # Botão para limpar o banco de dados

        self.category_label = QLabel("Categoria:")
        self.category_input = QLineEdit()
        self.value_label = QLabel("Valor:")
        self.value_input = QLineEdit()

        layout.addWidget(self.category_label)
        layout.addWidget(self.category_input)
        layout.addWidget(self.value_label)
        layout.addWidget(self.value_input)

        layout.addWidget(self.add_data_button)
        layout.addWidget(self.load_data_button)
        layout.addWidget(self.clear_data_button)

        self.matplotlib_widget = MatplotlibWidget()  # Widget para exibir gráficos
        layout.addWidget(self.matplotlib_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Conectar botões às funções correspondentes
        self.add_data_button.clicked.connect(self.add_data_to_db)
        self.load_data_button.clicked.connect(self.load_data)
        self.clear_data_button.clicked.connect(self.clear_data)

        # Inicializar banco de dados SQLite
        self.conn = sqlite3.connect("data.db")
        self.create_table()

    def create_table(self):
        # Criar a tabela no banco de dados SQLite para armazenar os dados
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Category TEXT,
                Value TEXT
            )
        """)
        self.conn.commit()

    def add_data_to_db(self):
        # Obter os valores da categoria e valor dos campos de entrada
        category = self.category_input.text()
        value = self.value_input.text()

        # Formatar o valor com duas casas decimais antes da inserção
        try:
            formatted_value = "{:.2f}".format(float(value))
        except ValueError:
            formatted_value = value

        # Inserir os dados no banco de dados SQLite
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO data (Category, Value) VALUES (?, ?)", (category, formatted_value))
        self.conn.commit()

        # Limpar os campos de entrada após a inserção
        self.category_input.clear()
        self.value_input.clear()

    def load_data(self):
        # Carregar dados do banco de dados SQLite em um DataFrame
        query = "SELECT * FROM data"
        df = pd.read_sql_query(query, self.conn)

        # Armazenar o DataFrame como um atributo da classe
        self.dataframe = df

        # Plotar dados após o carregamento
        self.plot_data()

    def plot_data(self):
        if hasattr(self, "dataframe"):
            # Exemplo de plotagem de gráfico
            self.matplotlib_widget.figure.clf()
            ax = self.matplotlib_widget.figure.add_subplot(111)
            ax.bar(self.dataframe["Category"], self.dataframe["Value"])
            ax.set_xlabel("Categoria")
            ax.set_ylabel("Valor")
            ax.set_title("Gráfico de Barras")
            self.matplotlib_widget.canvas.draw()

    def clear_data(self):
        # Limpar todos os dados no banco de dados
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM data")
        self.conn.commit()
        self.load_data()  # Recarregar os dados após a limpeza

    def closeEvent(self, event):
        # Fechar a conexão com o banco de dados quando a janela é fechada
        self.conn.close()
        event.accept()

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataAnalysisApp()
    window.show()
    sys.exit(app.exec())
