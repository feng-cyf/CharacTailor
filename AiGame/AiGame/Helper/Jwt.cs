using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.IdentityModel.Tokens;

namespace AiGame.Helper
{
    public class JwtHelper
    {
        string secretKey = "My_AI_Chat";
        /// <summary>
        /// 验证一个 HS256 签名的 JWT Token 的有效性。
        /// </summary>
        /// <param name="token">待验证的 JWT Token</param>
        /// <param name="secretKey">用于签名的密钥 (与 Python 端必须完全相同)</param>
        /// <returns>如果验证成功，则返回 Claims 字典；否则抛出异常。</returns>
        /// <exception cref="SecurityTokenException">当 Token 无效、过期或签名不匹配时抛出。</exception>
        public Dictionary<string, object> ValidateToken(string token)
        {
            if (string.IsNullOrEmpty(token))
                throw new ArgumentException("Token cannot be null or empty.", nameof(token));
            if (string.IsNullOrEmpty(secretKey))
                throw new ArgumentException("Secret key cannot be null or empty.", nameof(secretKey));

            var tokenHandler = new JwtSecurityTokenHandler();
            var key = Encoding.UTF8.GetBytes(secretKey);

            try
            {
                // 配置 Token 验证参数
                TokenValidationParameters validationParameters = new TokenValidationParameters
                {
                    ValidateIssuerSigningKey = true,
                    IssuerSigningKey = new SymmetricSecurityKey(key),
                    ValidAlgorithms = new[] { SecurityAlgorithms.HmacSha256 }, // 明确指定算法为 HS256

                    // 根据你的需求配置以下参数
                    ValidateIssuer = false, // 如果 Python 端设置了 Issuer，请在这里验证
                    ValidateAudience = false, // 如果 Python 端设置了 Audience，请在这里验证
                    ValidateLifetime = true, // 验证令牌是否过期
                    ClockSkew = TimeSpan.Zero // 不允许时间偏差
                };

                // 执行验证
                SecurityToken validatedToken;
                ClaimsPrincipal principal = tokenHandler.ValidateToken(token, validationParameters, out validatedToken);

                // 验证成功，提取 Claims 并转换为字典
                var jwtToken = (JwtSecurityToken)validatedToken;
                var claimsDict = new Dictionary<string, object>();
                foreach (Claim claim in jwtToken.Claims)
                {
                    claimsDict[claim.Type] = claim.Value;
                }

                return claimsDict;
            }
            catch (SecurityTokenException ex)
            {
                // 验证失败（签名错误、令牌过期等）
                throw new SecurityTokenException("Invalid or expired token.", ex);
            }
        }

        // (之前的 DecodePayload 和 DecodeHeader 方法可以保留，用于不需要验证的场景)
        /// <summary>
        /// 仅解码 Payload，不验证签名。
        /// </summary>
        public Dictionary<string, object> DecodePayload(string token)
        {
            if (string.IsNullOrEmpty(token))
                throw new ArgumentException("Token cannot be null or empty.", nameof(token));

            string[] parts = token.Split('.');
            if (parts.Length != 3)
                throw new ArgumentException("Invalid JWT token format.", nameof(token));

            try
            {
                string payloadBase64 = parts[1].Replace('-', '+').Replace('_', '/');
                switch (payloadBase64.Length % 4)
                {
                    case 2: payloadBase64 += "=="; break;
                    case 3: payloadBase64 += "="; break;
                }

                byte[] payloadBytes = Convert.FromBase64String(payloadBase64);
                string payloadJson = Encoding.UTF8.GetString(payloadBytes);

                return JsonSerializer.Deserialize<Dictionary<string, object>>(payloadJson,
                    new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
            }
            catch (Exception ex)
            {
                throw new ArgumentException("Failed to decode payload.", nameof(token), ex);
            }
        }
    }
}