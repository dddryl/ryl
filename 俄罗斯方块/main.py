import pygame
from random import choice

# 游戏参数
FPS = 60
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 480
BLOCK_SIZE = 20
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BOARD_POS_X = 50
BOARD_POS_Y = 50
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 128, 128)]
BLANK = -1

# 初始化游戏界面和背景音乐
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
bg_sound = pygame.mixer.Sound('简弘亦 - 我最亲爱的.ogg')
bg_sound.play(loops=-1)

# 俄罗斯方块索引
I_BLOCK = 0
J_BLOCK = 1
L_BLOCK = 2
O_BLOCK = 3
S_BLOCK = 4
T_BLOCK = 5
Z_BLOCK = 6

# 俄罗斯方块形状
SHAPES = [
    [[1, 1, 1, 1]], 
    [[1, 1, 1], [BLANK, BLANK, 1]], 
    [[1, 1, 1], [1, BLANK, BLANK]], 
    [[1, 1], [1, 1]], 
    [[BLANK, 1, 1], [1, 1, BLANK]], 
    [[1, 1, 1], [BLANK, 1, BLANK]], 
    [[1, 1, BLANK], [BLANK, 1, 1]]
]

# 俄罗斯方块类
class Block:
    def __init__(self, x, y, index):
        self.x = x
        self.y = y
        self.index = index
        self.color = COLORS[index]
        self.shape = SHAPES[index]
        self.rotation = 0

    # 旋转俄罗斯方块
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.shape)

    # 绘制俄罗斯方块
    def draw(self, surface):
        for i, row in enumerate(self.shape[self.rotation]):
            for j, column in enumerate(row):
                if column == 1:
                    pygame.draw.rect(surface, self.color, (BOARD_POS_X + (self.x+j)*BLOCK_SIZE, BOARD_POS_Y + (self.y+i)*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)


# 游戏主循环
def main():
    # 初始化游戏面板
    board = [[BLANK] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

    # 生成新的俄罗斯方块
    def new_block():
        return Block(3, 0, choice(range(7)))

    # 检测俄罗斯方块是否越界或碰撞
    def is_valid_position(x, y, block):
        for i, row in enumerate(block.shape[block.rotation]):
            for j, column in enumerate(row):
                if column == 1:
                    pos_x, pos_y = x+j, y+i # 方块在游戏面板的坐标
                    if pos_x < 0 or pos_x >= BOARD_WIDTH or pos_y >= BOARD_HEIGHT or (pos_y >= 0 and board[pos_y][pos_x] != BLANK):
                        return False
        return True

    # 将当前俄罗斯方块保存到游戏面板中
    def place_block(x, y, block):
        for i, row in enumerate(block.shape[block.rotation]):
            for j, column in enumerate(row):
                if column == 1:
                    pos_x, pos_y = x+j, y+i # 方块在游戏面板的坐标
                    if pos_y >= 0:
                        board[pos_y][pos_x] = block.index

    # 清除游戏面板上已满的行
    def clear_lines():
        lines_cleared = 0
        for i in range(BOARD_HEIGHT-1, -1, -1):
            if all(j != BLANK for j in board[i]):
                lines_cleared
                # 将上面所有行下移
                for j in range(i, 0, -1):
                    board[j] = board[j - 1][:]
                board[0] = [BLANK] * BOARD_WIDTH
                lines_cleared += 1
        return lines_cleared

    # 绘制游戏面板
    def draw_board(surface):
        for i, row in enumerate(board):
            for j, column in enumerate(row):
                color = COLORS[column] if column != BLANK else (255, 255, 255)
                pygame.draw.rect(surface, color,
                                 (BOARD_POS_X + j * BLOCK_SIZE, BOARD_POS_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                                 0)

    # 游戏主循环
    score = 0
    current_block = new_block()
    next_block = new_block()
    game_over = False
    while not game_over:
        clock.tick(FPS)

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_over = True
                elif event.key == pygame.K_LEFT:
                    if is_valid_position(current_block.x - 1, current_block.y, current_block):
                        current_block.x -= 1
                elif event.key == pygame.K_RIGHT:
                    if is_valid_position(current_block.x + 1, current_block.y, current_block):
                        current_block.x += 1
                elif event.key == pygame.K_DOWN:
                    if is_valid_position(current_block.x, current_block.y + 1, current_block):
                        current_block.y += 1
                    else:
                        place_block(current_block.x, current_block.y, current_block)
                        lines_cleared = clear_lines()
                        score += lines_cleared ** 2
                        current_block = next_block
                        next_block = new_block()
                        if not is_valid_position(current_block.x, current_block.y, current_block):
                            game_over = True
                elif event.key == pygame.K_UP:
                    current_block.rotate()

        # 绘制游戏场景
        screen.fill((0, 0, 0))
        current_block.draw(screen)
        draw_board(screen)
        font = pygame.font.Font(None, 30)
        text = font.render('Score: %d' % score, True, (255, 255, 255))
        screen.blit(text, (10, 10))
        text = font.render('Next:', True, (255, 255, 255))
        screen.blit(text, (BOARD_POS_X + BLOCK_SIZE * BOARD_WIDTH + 50, BOARD_POS_Y))
        next_block.draw(screen)

        # 更新画面
        pygame.display.flip()

    # 停止背景音乐，并退出游戏
    bg_sound.stop()
    pygame.quit()