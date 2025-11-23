class GreedyGomokuAI:
    """
    一个纯粹的五子棋AI逻辑类。
    不包含任何I/O、API或进程通信代码。
    仅提供计算最佳落子的核心功能。
    """

    def __init__(self, board_size=15):
        self.board_size = board_size
        self.scores = {
            (5, 0): 1000000, (5, 1): 1000000,
            (4, 0): 100000, (4, 1): 10000,
            (3, 0): 1000, (3, 1): 100,
            (2, 0): 10, (2, 1): 5,
            (1, 0): 1, (1, 1): 0.5
        }

    def _evaluate_line(self, line, player):
        """评估一条直线上的棋型得分（内部辅助方法）"""
        max_score = 0
        n = len(line)
        opponent = 3 - player
        for i in range(n):
            if line[i] != player and line[i] != 0:
                continue

            count, blocked = 0, 0
            # 正向
            for j in range(i, n):
                if line[j] == player:
                    count += 1
                elif line[j] == 0:
                    break
                else:
                    blocked += 1
                    break
            # 反向
            for j in range(i - 1, -1, -1):
                if line[j] == player:
                    count += 1
                elif line[j] == 0:
                    break
                else:
                    blocked += 1
                    break

            if count > 0:
                key = (min(count, 5), min(blocked, 1))
                max_score = max(max_score, self.scores.get(key, 0))
        return max_score

    def _calculate_score(self, board, x, y, player):
        """计算在(x, y)落子后，玩家的得分（内部辅助方法）"""
        # 模拟落子
        new_board = [row.copy() for row in board]
        new_board[x][y] = player

        total_score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            line = []
            for i in range(-4, 5):
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < self.board_size and 0 <= ny < self.board_size:
                    line.append(new_board[nx][ny])
                else:
                    line.append(3 - player)  # 边界视为对手阻挡
            total_score += self._evaluate_line(line, player)
        return total_score

    def get_best_move(self, board, player=2):
        """
        计算并返回最佳落子坐标。

        :param board: 一个15x15的二维整数列表，0=空, 1=玩家1, 2=玩家2。
        :param player: AI所代表的玩家编号 (1 或 2)。
        :return: 一个包含最佳落子(x, y)坐标的元组。
        """
        best_score = -1
        best_move = (0, 0)  # 默认值，实际会被覆盖
        opponent = 3 - player

        # 遍历棋盘上的每一个空位
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board[x][y] == 0:
                    # 计算进攻得分和防守得分
                    attack_score = self._calculate_score(board, x, y, player)
                    defend_score = -self._calculate_score(board, x, y, opponent)
                    total_score = attack_score + defend_score

                    # 更新最佳落子
                    if total_score > best_score:
                        best_score = total_score
                        best_move = (x, y)
        return best_move