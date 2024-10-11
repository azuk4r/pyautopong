from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QVBoxLayout, QLabel, QPushButton, QDialog
from PyQt5.QtGui import QPainter, QColor, QFont
from pyautogui import FAILSAFE, moveTo
from PyQt5.QtCore import Qt, QTimer
from sys import argv, exit

FAILSAFE = False

class BarWindow(QWidget):
	def __init__(self):
		super().__init__()
		screen_geometry = QDesktopWidget().screenGeometry()
		self.screen_width = screen_geometry.width()
		self.screen_height = screen_geometry.height()
		self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setGeometry(0, 0, self.screen_width, self.screen_height)
		self.bar_width = 20
		self.bar_height = 100
		self.bar_speed = 40
		self.left_bar_y = self.screen_height // 2 - self.bar_height // 2
		self.right_bar_y = self.screen_height // 2 - self.bar_height // 2
		self.left_bar_x = 0
		self.right_bar_x = self.screen_width - self.bar_width
		self.left_score = 0
		self.right_score = 0
		self.ball_speed_x = 60
		self.ball_speed_y = 45
		self.ball_x = self.screen_width // 2
		self.ball_y = self.screen_height // 2
		self.max_sets = 2
		self.ball_timer = QTimer(self)
		self.ball_timer.timeout.connect(self.move_ball)
		self.ball_timer.start(30)
		self.bar_timer = QTimer(self)
		self.bar_timer.timeout.connect(self.move_bars)
		self.bar_timer.start(20)
		self.bar_movement_up = False
		self.bar_movement_down = False
		self.right_bar_movement_up = False
		self.right_bar_movement_down = False

	def move_bars(self):
		if self.bar_movement_up:
			self.left_bar_y = max(0, self.left_bar_y - self.bar_speed)
		if self.bar_movement_down:
			self.left_bar_y = min(self.height() - self.bar_height, self.left_bar_y + self.bar_speed)
		if self.right_bar_movement_up:
			self.right_bar_y = max(0, self.right_bar_y - self.bar_speed)
		if self.right_bar_movement_down:
			self.right_bar_y = min(self.height() - self.bar_height, self.right_bar_y + self.bar_speed)
		self.update()

	def move_ball(self):
		self.ball_x += self.ball_speed_x
		self.ball_y += self.ball_speed_y
		if self.ball_y <= 0 or self.ball_y >= self.screen_height:
			self.ball_speed_y *= -1
		if self.ball_x <= self.bar_width and self.left_bar_y <= self.ball_y <= self.left_bar_y + self.bar_height:
			self.ball_speed_x *= -1
		elif self.ball_x >= self.screen_width - self.bar_width and self.right_bar_y <= self.ball_y <= self.right_bar_y + self.bar_height:
			self.ball_speed_x *= -1
		elif self.ball_x < 0:
			self.right_score += 1
			self.reset_ball()
			self.check_winner()
		elif self.ball_x > self.screen_width:
			self.left_score += 1
			self.reset_ball()
			self.check_winner()
		moveTo(self.ball_x, self.ball_y)
		self.update()

	def reset_ball(self):
		self.ball_x = self.screen_width // 2
		self.ball_y = self.screen_height // 2
		self.ball_speed_x *= -1

	def check_winner(self):
		if self.left_score == self.max_sets:
			self.end_game('left player wins!')
		elif self.right_score == self.max_sets:
			self.end_game('right player wins!')

	def end_game(self, message):
		dialog = QDialog(self)
		dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
		dialog.setStyleSheet("""
			QDialog {
				background-color: #111;
				border: 2px solid #00FF00;
			}
			QPushButton {
				background-color: #333;
				color: #00FF00;
				border: 2px solid #00FF00;
				font-family: "Courier New", monospace;
				font-size: 14px;
				padding: 8px;
				width: 100px;
			}
			QPushButton:hover {
				background-color: #222;
			}
		""")
		layout = QVBoxLayout()
		label = QLabel(f'<div style="color: red; font-size: 18px;">{message}</div>')
		label.setAlignment(Qt.AlignCenter)
		label.setStyleSheet("color: red; font-size: 18px; text-align: center;")
		layout.addWidget(label)
		rematch_button = QPushButton('rematch')
		close_button = QPushButton('byebye')
		rematch_button.clicked.connect(lambda: (dialog.accept(), self.reset_game()))
		close_button.clicked.connect(lambda: (dialog.accept(), self.ball_timer.stop(), self.bar_timer.stop(), QApplication.quit()))
		button_layout = QVBoxLayout()
		button_layout.addWidget(rematch_button)
		button_layout.addWidget(close_button)
		button_layout.setAlignment(Qt.AlignCenter)
		layout.addLayout(button_layout)
		dialog.setLayout(layout)
		dialog.setWindowModality(Qt.ApplicationModal)
		dialog.exec_()

	def reset_game(self):
		self.left_score = 0
		self.right_score = 0
		self.reset_ball()
		self.update()

	def paintEvent(self, event):
		painter = QPainter(self)
		painter.setBrush(QColor(0, 0, 0, 150))
		painter.drawRect(80, 30, 80, 60)
		painter.drawRect(self.screen_width - 160, 30, 80, 60)
		painter.setBrush(QColor(255, 255, 255))
		painter.drawRect(self.left_bar_x, self.left_bar_y, self.bar_width, self.bar_height)
		painter.drawRect(self.right_bar_x, self.right_bar_y, self.bar_width, self.bar_height)
		painter.setFont(QFont('Courier', 40))
		painter.setPen(QColor(255, 255, 255))
		painter.drawText(80 + (80 - painter.fontMetrics().width(f'{self.left_score}')) // 2, 30 + (60 - painter.fontMetrics().height()) // 2 + painter.fontMetrics().ascent(), f'{self.left_score}')
		painter.drawText(self.screen_width - 160 + (80 - painter.fontMetrics().width(f'{self.right_score}')) // 2, 30 + (60 - painter.fontMetrics().height()) // 2 + painter.fontMetrics().ascent(), f'{self.right_score}')

	def keyPressEvent(self, event):
		key = event.key()
		if key == Qt.Key_W:
			self.bar_movement_up = True
		elif key == Qt.Key_S:
			self.bar_movement_down = True
		elif key == Qt.Key_Up:
			self.right_bar_movement_up = True
		elif key == Qt.Key_Down:
			self.right_bar_movement_down = True

	def keyReleaseEvent(self, event):
		key = event.key()
		if key == Qt.Key_W:
			self.bar_movement_up = False
		elif key == Qt.Key_S:
			self.bar_movement_down = False
		elif key == Qt.Key_Up:
			self.right_bar_movement_up = False
		elif key == Qt.Key_Down:
			self.right_bar_movement_down = False

if __name__ == '__main__':
	app = QApplication(argv)
	window = BarWindow()
	window.show()
	window.activateWindow()
	window.raise_()
	exit(app.exec_())