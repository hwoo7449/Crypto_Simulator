import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.pyplot import rcParams
import matplotlib.pyplot as plt
import numpy as np
import random

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cur_xpos = 0  # 현재 x 위치
        self.cur_ypos = 0  # 현재 y 위치
        
        self.points = []   # 데이터 포인트를 저장할 리스트
        self.initUI()      # UI 초기화 함수 호출

    def initUI(self):
        self.setWindowTitle('Crypto Simulator')  # 창 제목 설정
        
        # 메인 위젯 생성
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QHBoxLayout(self.main_widget)

        # Matplotlib figure 생성
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # # 데이터 입력 위젯 레이아웃 생성
        # data_layout = QVBoxLayout()
        # layout.addLayout(data_layout)
        
        # # 데이터를 추가하기 위한 위젯들 생성
        # self.x_label = QLabel("X 값:")
        # self.x_input = QLineEdit()
        # self.y_label = QLabel("Y 값:")
        # self.y_input = QLineEdit()
        # self.add_button = QPushButton("Add Data")
        # self.add_button.clicked.connect(self.add_data)

        # # 데이터 입력 위젯들을 레이아웃에 추가
        # layout.addWidget(self.x_label)
        # layout.addWidget(self.x_input)
        # layout.addWidget(self.y_label)
        # layout.addWidget(self.y_input)
        # layout.addWidget(self.add_button)
        
        # 타이머 설정 및 시그널 연결
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.add_random_data)
        self.timer.start(100)

        self.plot()  # 그래프를 그리는 메소드

        # def add_data(self):
        #     # 사용자 입력 가져오기
        #     x_val = float(self.x_input.text())
        #     y_val = float(self.y_input.text())

        #     # 그래프에 데이터 추가
        #     ax = self.figure.axes[0]
        #     ax.plot(x_val, y_val, 'bo')  # 데이터 포인트 플롯
        #     self.canvas.draw()

    def plot(self):
        # 이전 그래프 지우기
        self.figure.clear()

        # 샘플 데이터 생성
        # x = np.linspace(0, 10, 100)
        # y = np.sin(x)

        # figure에 서브플롯 추가
        ax = self.figure.add_subplot(111)

        # 축 레이블 및 제목 설정
        ax.set_xlabel('X 축')
        ax.set_ylabel('Y 축')
        ax.set_title('그래프')
        
        # 캔버스 갱신
        self.canvas.draw()
        
    def add_random_data(self):
        # 랜덤 데이터 생성
        self.cur_ypos += random.randint(-5, 5)  # y 위치를 랜덤으로 변경
        
        # 현재 x 위치와 y 위치로 데이터 포인트 플롯
        ax = self.figure.axes[0]
        color = 'bo' if self.cur_ypos < 0 else 'ro' # 음수인 경우 파란색 양수인 경우 빨간색
            
        ax.plot(self.cur_xpos, self.cur_ypos, color)
        self.points.append((self.cur_xpos, self.cur_ypos))

        # 포인트 개수가 50을 초과하는지 확인
        if len(self.points) > 50:
            # 첫 번째 포인트 삭제
            ax.lines[0].remove()
            del self.points[0]
            
        # 현재 x 위치 증가
        self.cur_xpos += 1
        
        # 캔버스 갱신
        self.canvas.draw()

if __name__ == '__main__':
    rcParams['font.family'] ='Malgun Gothic'
    rcParams['axes.unicode_minus'] =False
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())