using AiGame.Game;

namespace AiGame
{
    public class AppInitializer : IHostedService
    {
        private readonly IServiceProvider _serviceProvider;

        public AppInitializer(IServiceProvider serviceProvider)
        {
            _serviceProvider = serviceProvider;
        }

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            using var scope = _serviceProvider.CreateScope();
            var services = scope.ServiceProvider;

            try
            {
            }
            catch (Exception ex)
            {
                Console.WriteLine($"初始化失败：{ex.Message}");
                throw;
            }
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            // 应用停止时执行的逻辑（可选）
            return Task.CompletedTask;
        }
    }
}
