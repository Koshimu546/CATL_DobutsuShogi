import pygame

class Piece:
    def __init__(self, name, owner, image_path):
        self.name = name
        self.owner = owner
        self.image = pygame.image.load(image_path)
        # 画像がでかすぎるのでサイズを調整
        self.image = pygame.transform.smoothscale(self.image, (80, 80)) 

    def __str__(self):
        return f"{self.name} ({self.owner})"

class DobutsuShogi:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((600, 800))
        pygame.display.set_caption("CATLどうぶつしょうぎ")
        self.board = [[None for _ in range(3)] for _ in range(4)]
        self.initialize_pieces()
        self.turn = "先手"
        self.running = True
        self.cell_size = 200
        self.selected_piece = None
        self.winner = None
        self.message = ""

    #コマの初期配置を定義
    def initialize_pieces(self):
        # 先手のプレイヤーの駒を配置（最下段）
        self.board[3][0] = Piece("Elephant", "先手", "elephant.png")
        self.board[3][1] = Piece("Lion", "先手", "lion_p1.png")
        self.board[3][2] = Piece("Giraffe", "先手", "giraffe.png")
        self.board[2][1] = Piece("Hiyoko", "先手", "hiyoko.png")

        # 後手のプレイヤーの駒を配置（最上段、先手の配置を反転）
        self.board[0][0] = Piece("Giraffe", "後手", "giraffe.png")
        self.board[0][1] = Piece("Lion", "後手", "lion_p2.png")
        self.board[0][2] = Piece("Elephant", "後手", "elephant.png")
        self.board[1][1] = Piece("Hiyoko", "後手", "hiyoko.png")

        # 後手の駒を180度回転させる
        for row in range(2):
            for col in range(3):
                if self.board[row][col] is not None:
                    self.board[row][col].image = pygame.transform.rotate(self.board[row][col].image, 180)

    # ボードの描写
    def draw_board(self):
        self.screen.fill((255, 255, 255))
        for row in range(4):
            for col in range(3):
                rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                if self.selected_piece == (row, col):
                # 選択されたコマの周りを黄色で光らせる
                    pygame.draw.rect(self.screen, (255, 255, 0), rect) 
                # 選択してない時は白に光らせて見えないようにする
                else:
                    pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
                piece = self.board[row][col]
                #コマのサイズ調整
                if piece:
                    piece_rect = piece.image.get_rect(center=(col * self.cell_size + self.cell_size // 2, row * self.cell_size + self.cell_size // 2))
                    self.screen.blit(piece.image, piece_rect.topleft)

        # 勝者の表示
        if self.winner:
            # 文字化けしたのでフォントを突っ込んだ
            font = pygame.font.Font("umeplus-gothic.ttf", 30) 
            text = font.render(f"{self.winner}の勝ち", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

        # 諸々のメッセージの表示
        if self.message:
            # 文字化けしたのでフォントを突っ込んだ
            font = pygame.font.Font("umeplus-gothic.ttf", 30)
            text = font.render(self.message, True, (0, 0, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 50))
            self.screen.blit(text, text_rect)

        pygame.display.flip()

    #クリック位置の座標を返す
    def get_cell_from_mouse(self, pos):
        x, y = pos
        col = x // self.cell_size
        row = y // self.cell_size
        return row, col

    def move_piece(self, from_row, from_col, to_row, to_col):
        if self.board[from_row][from_col] is None:
            self.message = "選択された位置に駒がありません"
            return

        piece = self.board[from_row][from_col]
        if piece.owner != self.turn:
            self.message = "今は相手のターンです"
            return

        # 移動の検証
        if not (0 <= to_row < 4 and 0 <= to_col < 3):
            self.message = "範囲外の移動です"
            return

        # 駒の動きの制限
        if piece.name == "Hiyoko":
            if piece.owner == "先手":
                if not (to_row == from_row - 1 and to_col == from_col):
                    self.message = "ひよこは前に1マスしか進めません"
                    return
            elif piece.owner == "後手":
                if not (to_row == from_row + 1 and to_col == from_col):
                    self.message = "ひよこは前に1マスしか進めません"
                    return
            # ひよこが相手陣地の最奥に到達した場合、にわとりに進化
            if (piece.owner == "先手" and to_row == 0) or (piece.owner == "後手" and to_row == 3):
                piece.name = "Niwatori"
                piece.image = pygame.image.load("niwatori.png")
                piece.image = pygame.transform.smoothscale(piece.image, (80, 80))

                if piece.owner == "後手":
                    piece.image = pygame.transform.rotate(piece.image, 180)
                self.message = f"{piece.owner}のひよこがにわとりに進化しました！"

        elif piece.name == "Giraffe":
            if not ((abs(to_row - from_row) == 1 and to_col == from_col) or (to_row == from_row and abs(to_col - from_col) == 1)):
                self.message = "きりんは斜めに進むことができません"
                return
            
        elif piece.name == "Elephant":
            if not (abs(to_row - from_row) == 1 and abs(to_col - from_col) == 1):
                self.message = "ぞうは縦横に進むことができません"
                return
            
        elif piece.name == "Lion":
            if not (abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1):
                self.message = "2マス以上進むことはできません"
                return
            
        elif piece.name == "Niwatori":
            if not ((abs(to_row - from_row) <= 1 and abs(to_col - from_col) <= 1) and not (to_row == from_row + 1 and abs(to_col - from_col) == 1)):
                self.message = "にわとりは斜め後ろ以外に1マス進めます"
                return

        # 勝敗の判定
        target_piece = self.board[to_row][to_col]
        if target_piece and target_piece.name == "Lion":
            if target_piece.owner == "先手":
                self.winner = "後手"
            else:
                self.winner = "先手"
            self.running = False
            return

        # 駒を移動させる
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None

        # ターンを変更する
        self.turn = "先手" if self.turn == "後手" else "後手"
        self.message = ""

    # ゲームの表示
    def play(self):
        self.selected_piece = None
        while self.running:
            self.draw_board()
            for event in pygame.event.get():
                # 閉じるボタンが押されたら終了
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # コマが選択されていない場合、クリックされた座標を取得
                    if self.selected_piece is None:
                        self.selected_piece = self.get_cell_from_mouse(event.pos)
                    # コマが選択されている場合、移動処理
                    else:
                        to_pos = self.get_cell_from_mouse(event.pos)
                        self.move_piece(self.selected_piece[0], self.selected_piece[1], to_pos[0], to_pos[1])
                        self.selected_piece = None

        # ゲーム終了後も勝者を表示する、勝者が決まっても閉じないように
        while True:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

if __name__ == "__main__":
    game = DobutsuShogi()
    game.play()
