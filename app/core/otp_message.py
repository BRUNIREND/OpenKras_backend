def create_otp_html(code: str):
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                <h2 style="color: #333; text-align: center;">Открой Красноярск</h2>
                <p style="font-size: 16px; color: #555;">Здравствуйте!</p>
                <p style="font-size: 16px; color: #555;">Используйте этот код для подтверждения регистрации в приложении:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #007bff; background: #e7f3ff; padding: 10px 20px; border-radius: 5px;">
                        {code}
                    </span>
                </div>
                <p style="font-size: 14px; color: #888; text-align: center;">Код действителен в течение 5 минут.</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 12px; color: #aaa; text-align: center;">Если вы не запрашивали этот код, просто проигнорируйте письмо.</p>
            </div>
        </body>
    </html>
    """