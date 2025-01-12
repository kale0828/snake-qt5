import sys
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPainter, QColor, QPixmap, QTransform

class SnakeGame(QWidget):
    def __init__(self):
        super().__init__()
        self.cell_size = 20
        self.setFixedSize(600, 600)
        self.setWindowTitle('贪吃蛇')
        
        # 计算游戏网格大小
        self.game_width = self.width() // self.cell_size
        self.game_height = self.height() // self.cell_size
        
        # 设置游戏定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        
        # 初始化游戏计数和基础速度
        self.game_count = 0
        self.base_speed = 150
        
        # 初始化分数
        self.score = 0
        
        # 蛇的最大长度
        self.max_len = 15
        
        # 加载蛇身贴图
        self.snake_head = QPixmap("snake_head.png")
        self.snake_body = QPixmap("snake_body.png")
        self.snake_tail = QPixmap("snake_tail.png")
        
        # 初始化游戏
        self.init_game_state()
        self.show()

    def init_game_state(self):
        # 初始化游戏状态
        self.is_game_over = False
        if hasattr(self, 'is_winner'):
            if self.is_winner:
                self.game_count += 1  # 只在获胜后增加计数
            delattr(self, 'is_winner')
        
        # 初始化蛇的位置和方向
        start_x = self.game_width // 2
        start_y = self.game_height // 2
        self.snake = [(start_x, start_y), (start_x-1, start_y), (start_x-2, start_y)]  # 初始长度为3
        self.direction = Qt.Key_Right
        
        # 生成第一个食物
        self.generate_food()
        
        # 根据游戏次数调整速度
        speed = max(50, self.base_speed - (self.game_count * 20))  # 每次获胜后速度加快20ms，最快50ms
        self.timer.start(speed)
        
    def initUI(self):
        pass
        
    def initGame(self):
        pass
        
    def generate_food(self):
        while True:
            x = random.randint(0, self.game_width - 1)
            y = random.randint(0, self.game_height - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
        
    def get_angle(self, direction_or_dx, dy=None):
        if dy is None:
            # 根据方向计算角度
            if direction_or_dx == Qt.Key_Left:
                return 180
            elif direction_or_dx == Qt.Key_Right:
                return 0
            elif direction_or_dx == Qt.Key_Up:
                return 270
            elif direction_or_dx == Qt.Key_Down:
                return 90
        else:
            # 根据坐标差值计算角度
            if direction_or_dx == 0:
                if dy > 0:
                    return 270
                else:
                    return 90
            elif direction_or_dx > 0:
                return 180
            else:
                return 0
                
    def keyPressEvent(self, event):
        key = event.key()
        
        if self.is_game_over:
            if key == Qt.Key_Space:  # 按空格键重新开始
                self.init_game_state()
                self.update()
                return
        else:
            # 确保蛇不能直接向反方向移动
            if key == Qt.Key_Left and self.direction != Qt.Key_Right:
                self.direction = Qt.Key_Left
            elif key == Qt.Key_Right and self.direction != Qt.Key_Left:
                self.direction = Qt.Key_Right
            elif key == Qt.Key_Up and self.direction != Qt.Key_Down:
                self.direction = Qt.Key_Up
            elif key == Qt.Key_Down and self.direction != Qt.Key_Up:
                self.direction = Qt.Key_Down
            
    def update_game(self):
        if self.is_game_over:
            return
            
        # 获取蛇头位置
        head = self.snake[0]
        
        # 根据方向移动蛇头
        if self.direction == Qt.Key_Left:
            new_head = (head[0] - 1, head[1])
        elif self.direction == Qt.Key_Right:
            new_head = (head[0] + 1, head[1])
        elif self.direction == Qt.Key_Up:
            new_head = (head[0], head[1] - 1)
        else:  # Qt.Key_Down
            new_head = (head[0], head[1] + 1)
            
        # 检查是否撞墙或撞到自己
        if (new_head[0] < 0 or new_head[0] >= self.game_width or
            new_head[1] < 0 or new_head[1] >= self.game_height or
            new_head in self.snake):
            self.is_game_over = True
            self.update()  # 立即刷新窗口
            return
            
        # 移动蛇
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            self.generate_food()
            self.score += 10  # 每次吃到食物增加10分
            # 检查是否达到长度
            if len(self.snake) >= self.max_len:
                self.is_game_over = True
                self.is_winner = True
                self.update()  # 立即刷新窗口
                return
        else:
            self.snake.pop()
            
        # 更新界面
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制网格
        painter.setPen(QColor(200, 200, 200))  # 浅灰色网格
        for x in range(self.game_width):
            for y in range(self.game_height):
                painter.drawRect(x * self.cell_size, y * self.cell_size, 
                               self.cell_size, self.cell_size)
            
        # 绘制蛇
        for i, segment in enumerate(self.snake):
            x = segment[0] * self.cell_size
            y = segment[1] * self.cell_size
            if i == 0:
                # 根据方向旋转蛇头
                angle = self.get_angle(self.direction)
                rotated_head = self.snake_head.transformed(QTransform().rotate(angle))
                painter.drawPixmap(x, y, rotated_head)
            elif i == len(self.snake) - 1:
                # 根据方向旋转蛇尾
                prev_segment = self.snake[i - 1]
                dx = segment[0] - prev_segment[0]
                dy = segment[1] - prev_segment[1]
                angle = self.get_angle(dx, dy)
                rotated_tail = self.snake_tail.transformed(QTransform().rotate(angle))
                painter.drawPixmap(x, y, rotated_tail)
            else:
                painter.drawPixmap(x, y, self.snake_body)
            
        # 绘制食物
        food_x = self.food[0] * self.cell_size
        food_y = self.food[1] * self.cell_size
        painter.fillRect(food_x, food_y, self.cell_size, self.cell_size, QColor(255, 0, 0))

        # 绘制游戏结束信息
        if self.is_game_over:
            # 绘制半透明背景
            overlay = QColor(0, 0, 0, 180)  # 黑色半透明
            painter.fillRect(self.rect(), overlay)
            
            # 设置字体
            font = painter.font()
            font.setPointSize(20)  # 设置字体大小
            painter.setFont(font)
            
            # 设置文字颜色
            painter.setPen(QColor(255, 255, 255))  # 白色文字
            
            # 显示游戏结束消息
            message = "恭喜获胜！" if hasattr(self, 'is_winner') and self.is_winner else "游戏结束！"
            painter.drawText(self.rect(), Qt.AlignCenter, message)
            
            # 显示重新开始提示和当前分数
            font.setPointSize(12)  # 较小的字体
            painter.setFont(font)
            restart_message = f"按空格键重新开始"

            # 在主消息下方显示重新开始提示
            rect = self.rect()
            rect.translate(0, 50)  # 向下偏移50像素
            painter.drawText(rect, Qt.AlignCenter, restart_message)
            
        # 绘制当前分数
        font = painter.font()
        font.setPointSize(16)  # 设置字体大小
        painter.setFont(font)
        score_message = f"分数: {self.score}"
        painter.drawText(self.rect().adjusted(20, 0, -self.width() // 2, 0), Qt.AlignTop | Qt.AlignLeft, score_message)

        # 绘制当前速度
        speed = max(50, self.base_speed - (self.game_count * 20))
        speed_message = f"速度: {speed}ms"
        painter.drawText(self.rect().adjusted(self.width() // 2, 0, -20, 0), Qt.AlignTop | Qt.AlignRight, speed_message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = SnakeGame()
    sys.exit(app.exec_())