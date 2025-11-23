using System;
using System.Collections.Generic;

namespace AiGame.Game
{
    // 1. 移除 static 关键字
    public class GomokuGame
    {
        private const int BoardSize = 15; // 15x15 棋盘
        private const int WinCount = 5;   // 五连子获胜
        private const int SpreadLayers = 4; // 扩散四层

        // --- 成员变量不再是 static ---
        private List<List<int>> _currentBoard;
        private bool _isGameOver = false;

        // 2. 添加构造函数，在创建实例时自动初始化棋盘
        public GomokuGame()
        {
            InitializeBoard();
        }

        /// <summary>
        /// 检查落子是否合法
        /// </summary>
        public bool IsValidMove(int x, int y)
        {
            if (_currentBoard == null)
            {
                throw new InvalidOperationException("棋盘尚未初始化。");
            }
            if (x < 0 || x >= BoardSize || y < 0 || y >= BoardSize)
                return false;
            return _currentBoard[x][y] == 0 && !_isGameOver;
        }

        /// <summary>
        /// 执行落子操作，并检查是否获胜。
        /// </summary>
        public int MakeMove(int x, int y, int player)
        {
            if (!IsValidMove(x, y))
            {
                return 0; // 落子无效
            }

            _currentBoard[x][y] = player;

            int winner = CheckWin(x, y);
            if (winner != 0)
            {
                _isGameOver = true;
                Console.WriteLine($"玩家 {winner} 获胜！");
            }
            return winner;
        }

        /// <summary>
        /// 检查落子后是否获胜
        /// </summary>
        private int CheckWin(int x, int y)
        {
            int currentPlayer = _currentBoard[x][y];
            if (currentPlayer == 0)
                return 0;

            int[][] directions = new int[][]
            {
                new int[] { 0, 1 }, new int[] { 0, -1 },
                new int[] { 1, 0 }, new int[] { -1, 0 },
                new int[] { 1, 1 }, new int[] { -1, -1 },
                new int[] { 1, -1 }, new int[] { -1, 1 }
            };

            int[] counts = new int[directions.Length];

            for (int i = 0; i < directions.Length; i++)
            {
                int[] dir = directions[i];
                int count = 0;
                for (int step = 1; step <= SpreadLayers; step++)
                {
                    int nx = x + dir[0] * step;
                    int ny = y + dir[1] * step;
                    if (nx < 0 || nx >= BoardSize || ny < 0 || ny >= BoardSize || _currentBoard[nx][ny] != currentPlayer)
                        break;
                    count++;
                }
                counts[i] = count;
            }

            if (counts[0] + counts[1] + 1 >= WinCount ||
                counts[2] + counts[3] + 1 >= WinCount ||
                counts[4] + counts[5] + 1 >= WinCount ||
                counts[6] + counts[7] + 1 >= WinCount)
                return currentPlayer;

            return 0;
        }

        /// <summary>
        /// 初始化空棋盘。
        /// </summary>
        public void InitializeBoard()
        {
            _currentBoard = new List<List<int>>();
            for (int i = 0; i < BoardSize; i++)
            {
                var row = new List<int>();
                for (int j = 0; j < BoardSize; j++)
                    row.Add(0);
                _currentBoard.Add(row);
            }
            _isGameOver = false;
            Console.WriteLine("新棋盘已初始化。");
        }

        /// <summary>
        /// 清空当前棋盘，用于开始新游戏。
        /// </summary>
        public void ClearBoard()
        {
            InitializeBoard();
        }

        /// <summary>
        /// 打印当前棋盘（调试用）
        /// </summary>
        public void PrintBoard()
        {
            if (_currentBoard == null)
            {
                Console.WriteLine("棋盘尚未初始化。");
                return;
            }
            Console.WriteLine("  0 1 2 3 4 5 6 7 8 9 A B C D E");
            for (int i = 0; i < BoardSize; i++)
            {
                Console.Write($"{i:X} ");
                for (int j = 0; j < BoardSize; j++)
                {
                    char c = _currentBoard[i][j] switch
                    {
                        0 => '.',
                        1 => 'X',
                        2 => 'O',
                        _ => '?'
                    };
                    Console.Write($"{c} ");
                }
                Console.WriteLine();
            }
        }

        /// <summary>
        /// 获取当前棋盘的可序列化状态。
        /// </summary>
        public (int[][] Board, int Size) GetBoardState()
        {
            if (_currentBoard == null)
            {
                throw new InvalidOperationException("棋盘尚未初始化。");
            }
            var arr = new int[BoardSize][];
            for (int i = 0; i < BoardSize; i++)
            {
                arr[i] = new int[BoardSize];
                for (int j = 0; j < BoardSize; j++)
                {
                    arr[i][j] = _currentBoard[i][j];
                }
            }
            return (arr, BoardSize);
        }
    }
}