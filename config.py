from environs import Env
from logging import info


env = Env()
env.read_env()

# Bot token can be obtained via https://t.me/BotFather
TOKEN: str = env.str("TOKEN")
# OpenAi key can be obtained via https://platform.openai.com/account/api-keys
OPENAI_API_KEY: str = env.str("OPENAI_API_KEY")
MODEL = env.str("MODEL", "gpt-3.5-turbo")  # gpt-3.5-turbo or gpt-4
USE_WEBHOOK: bool = env.bool("USE_WEBHOOK", False)
info(f"USE_WEBHOOK: {USE_WEBHOOK}")

if USE_WEBHOOK:
    WEBHOOK_PATH: str = env.str("WEBHOOK_PATH", "/bot/")
    # WEBHOOK_SECRET: str = env.str("WEBHOOK_SECRET","secret")
    BASE_WEBHOOK_URL: str = env.str("BASE_WEBHOOK_URL")
    # for ipv6: "::", ipv4: 0.0.0.0
    WEB_SERVER_HOST: str = env.str("WEB_SERVER_HOST", "::")
    WEB_SERVER_PORT: int = env.int("WEB_SERVER_PORT", 8350)
