using AiGame.Context;
using Autofac;
using Autofac.Extensions.DependencyInjection;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using Pomelo.EntityFrameworkCore.MySql.Infrastructure; // 添加此 using
using System.Net;
using System.Text;
namespace AiGame
{
    public class Program
    {
        public static void Main(string[] args)
        {

            var builder = WebApplication.CreateBuilder(args);
            var tempLogger = builder.Services.BuildServiceProvider().GetRequiredService<ILogger<Program>>();
            tempLogger.LogCritical("【启动检查】临时日志记录器创建成功，这是一条 Critical 级别的日志。");
            builder.WebHost.UseUrls(builder.Configuration.GetValue<string>("Urls"));
            builder.Logging.AddConsole();
            builder.Services.AddCors(options =>
            {
                options.AddPolicy("AllowAll", policy =>
                {
                    policy.AllowAnyOrigin()   // 允许所有来源
                          .AllowAnyMethod()   // 允许所有 HTTP 方法
                          .AllowAnyHeader();  // 允许所有 HTTP 头部
                });
            });
            // Add services to the container.
            //builder.Host.UseServiceProviderFactory(new AutofacServiceProviderFactory());
            builder.Services.AddControllers();

            //builder.Host.ConfigureContainer<ConfigurationBuilder>(con =>
            //{

            //});
            var secretKey = builder.Configuration.GetValue<string>("Jwt:SecretKey");

            builder.Services.AddAuthentication(options =>
            {
                options.DefaultScheme = JwtBearerDefaults.AuthenticationScheme;
                options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
            })
             .AddJwtBearer(options =>
             {
                 options.TokenValidationParameters = new TokenValidationParameters
                 {
                     ValidateIssuerSigningKey = true,
                     IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
                     ValidateLifetime = true,
                     ClockSkew = TimeSpan.FromMinutes(5),ValidateAudience = false, 
                     ValidateIssuer = false
                 };           
             });
            // Learn more about configuring Swagger/OpenAPI at https://aka.ms/aspnetcore/swashbuckle
            builder.Services.AddEndpointsApiExplorer();
            builder.Services.AddSwaggerGen();
            builder.Services.AddHostedService<AppInitializer>();
            var con = builder.Configuration.GetConnectionString("Mysql");
            // 这里需要传递 ServerVersion
            builder.Services.AddDbContext<AIGameContext>(options =>
                    options.UseMySql(con, ServerVersion.AutoDetect(con))
            );
            var app = builder.Build();
            // Configure the HTTP request pipeline.
            if (app.Environment.IsDevelopment())
            {
                app.UseSwagger();
                app.UseSwaggerUI();
            }
            app.UseWebSockets();
            app.UseHttpsRedirection();
            app.UseCors("AllowAll");
            app.UseAuthorization();

            app.MapControllers();

            app.Run();
        }
    }
}
