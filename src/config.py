from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str
    admin_link: str
    chat_id: int

    @staticmethod
    def from_env(env: Env):
        token = env.str('BOT_TOKEN')
        admin_link = env.str('ADMIN_LINK')
        chat_id = env.int('LOG_CHAT_ID')

        return TgBot(
            token=token,
            admin_link=admin_link,
            chat_id=chat_id
        )


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
    )
