from pathlib import Path

import simplematrixbotlib as botlib
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class MatrixSettings(BaseModel):
    server: str
    user: str
    password: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_nested_delimiter="_"
    )
    matrix: MatrixSettings
    prefix: str = "!"
    # = MatrixSettings()  # type:ignore[reportCallIssue]


settings = Settings()  # type:ignore[reportCallIssue]
data_path = Path("~/.local/share/intellitrix").expanduser()
if not data_path.exists():
    data_path.mkdir(parents=True)

creds = botlib.Creds(
    homeserver=settings.matrix.server,
    username=settings.matrix.user,
    password=settings.matrix.password,
    session_stored_file=str(data_path / "session.txt"),
)
config = botlib.Config()
config.encryption_enabled = True
config.join_on_invite = False
config.emoji_verify = True
config.ignore_unverified_devices = True
config.store_path = str(data_path / "crypto_store")
bot = botlib.Bot(creds, config)


@bot.listener.on_reaction_event
async def echo_reaction(room, event, reaction):
    resp_message = f"Reaction: {reaction}"
    await bot.api.send_text_message(room.room_id, resp_message)


@bot.listener.on_message_event
async def echo(room, message):
    match = botlib.MessageMatch(room, message, bot, settings.prefix)
    if match.is_not_from_this_bot():
        print(f"Received message {message}")
        breakpoint()

    if match.is_not_from_this_bot() and match.prefix() and match.command("echo"):

        await bot.api.send_text_message(
            room.room_id, " ".join(arg for arg in match.args())
        )


if __name__ == "__main__":
    bot.run()
