import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import random



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.cur_xpos = 0
        self.cur_ypos = 0
        
        self.points = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Crypto Simulator')
        
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)

        # Create a Matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        data_layout = QVBoxLayout()
        layout.addLayout(data_layout)
        
        # Widgets for adding data
        self.x_label = QLabel("X 값:")
        self.x_input = QLineEdit()
        self.y_label = QLabel("Y 값:")
        self.y_input = QLineEdit()
        self.add_button = QPushButton("Add Data")
        self.add_button.clicked.connect(self.add_data)

        layout.addWidget(self.x_label)
        layout.addWidget(self.x_input)
        layout.addWidget(self.y_label)
        layout.addWidget(self.y_input)
        layout.addWidget(self.add_button)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.add_random_data)
        self.timer.start(100)

        self.plot()  # Call the method to plot data


    def plot(self):
        # Clear the previous plot
        self.figure.clear()

        # Generate some sample data
        # x = np.linspace(0, 10, 100)
        # y = np.sin(x)

        # # Add a subplot to the figure
        ax = self.figure.add_subplot(111)

        # # Set labels and title
        ax.set_xlabel('X aixs')
        ax.set_ylabel('Y axis')
        ax.set_title('Graph')
        
        
        # # Refresh canvas
        self.canvas.draw()
        
    def add_data(self):
        # Retrieve user input
        x_val = float(self.x_input.text())
        y_val = float(self.y_input.text())

        # Add data to the plot
        ax = self.figure.axes[0]
        ax.plot(x_val, y_val, 'bo')  # Plot data point
        self.canvas.draw()
        
    def add_random_data(self):
        # Generate random data
        
        
        self.cur_xpos
        self.cur_ypos += random.randint(-5, 5)
        
        ax = self.figure.axes[0]
        
        if self.cur_ypos < 0:
            ax.plot(self.cur_xpos, self.cur_ypos, 'bo')
        else: 
            ax.plot(self.cur_xpos, self.cur_ypos, 'ro')
            
            
        self.points.append((self.cur_xpos, self.cur_ypos))

        # Check if the number of points exceeds 50
        if len(self.points) > 50:
            # Remove the first point
            ax.lines[0].remove()
            del self.points[0]
            

        # Add data to the plot
        
        #ax.plot(self.cur_xpos, self.cur_ypos, 'b')  # Plot data point
        
        self.cur_xpos += 1
        
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())