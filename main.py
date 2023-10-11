import sys
import logging
import time
import asyncio
from os import remove

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.i18n import gettext as _
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import FSMI18nMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from language_keyboard import make_row_keyboard, LanguageCallbackFactory, FLAGS
from chat_gpt import generate_text_chunks, generate_image, whisper, message_to_tg_chunks
import config
messages = {}  # save all individual user messages

# TODO: add more languages
# ["en", "uk", "ru", 'de',
#    'fr', 'es', 'it', 'pl',#
#    'cs', 'ja', 'zh', 'ko',
#    'hi', 'nl', 'bg', 'be',
#    'he', 'ar', 'el', 'da',
#    'et', 'fi', 'ka', 'id',
#    'ga', 'kk', 'lt', 'lv',
#    'ro', 'mn', 'ne', 'sl',
#    'sk', 'th', 'tr', 'uz',
#    'vi', 'af',]

bot = Bot(config.TOKEN, parse_mode=ParseMode.HTML)
i18n = I18n(path="locales", default_locale="en", domain="messages")
i18n_midleware = FSMI18nMiddleware(i18n=i18n)
available_languages = i18n.available_locales

# All handlers should be attached to the Dispatcher (or Router)
dp = Dispatcher()
dp.message.middleware(i18n_midleware)


def add_user_message(message: Message, user_message: str):
    userid = message.from_user.username

    if userid not in messages:
        messages[userid] = []
    messages[userid].append({"role": "user", "content": user_message})
    messages[userid].append({"role": "user",
                                "content": f"Now {time.strftime('%d/%m/%Y %H:%M:%S')} user: {message.from_user.full_name} message: {user_message}"})  # noqa: E501
    logging.info(f'{userid}: {user_message}')


async def answer_on_text(message: Message, user_message: str):
    userid = message.from_user.username

    if len(user_message) > 2048:
        await message.reply(_('Currently, the character limit for ChatGPT is 2048 characters'))
        return None

    add_user_message(message, user_message)

    processing_message = await message.reply(_('processing...'))
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    full_answer = ""
    try:
        chunks = await generate_text_chunks(messages[userid], userid)
        async for chunk in chunks:
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None and len(content) > 0:
                full_answer += content
                if content == " ":  # telegram thinks its trash message
                    continue
                if len(full_answer) < 4095:
                    await processing_message.edit_text(text=full_answer)
                else: # new message
                    full_answer = content
                    processing_message = await message.reply(text=full_answer)

    except Exception as e:
        logging.error(e)
        await message.reply(
            _("Nice try!")
        )


class ChooseLanguage(StatesGroup):
    choosing_lang_name = State()
    choose_end = State()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    userid = message.from_user.id

    if userid not in messages:
        answer = _("Hello, {name}, im Chat GPT")
    else:
        answer = _("Hello, {name}, all messages cleaned")
    messages[userid] = []

    await message.answer(
        _(answer).format(
            name=hbold(message.from_user.full_name)
        )
    )


@dp.message(Command("help", "h"))
async def command_help_handler(message: Message) -> None:
    await message.answer(
        _("This is a AI bot that will answer your questions.\nChange language: /language /lang /l\nCreate image(works only with GPT-4): /image /img /i")
    )


@dp.message(Command("image", "img", "i"))
async def send_image(message: Message):
    if config.MODEL == "gpt-4":
        try:
            description = message.text.replace('/image', '').strip()
            if not description:
                await message.reply(_("Please add a description of the image after the /image command. For example, /image Neon City."))
                return
        except Exception as e:
            logging.error(f'Error in send_image: {e}')
        try:
            image_url = await generate_image(description)
            await message.answer_photo(chat_id=message.chat.id, photo=image_url)
        except Exception as e:
            await message.reply(_("An error occurred during image generation:") + str(e))
    else:
        await message.answer(
            _("Sorry, works only with gpt-4")
        )


@dp.message(Command("language", "lang", "l"))
async def language_cmd(message: Message, state: FSMContext):

    await message.answer(
        _('language_selection'),
        reply_markup=make_row_keyboard(available_languages)
    )
    # Set user state choosing lang
    await state.set_state(ChooseLanguage.choosing_lang_name)


@dp.message(F.voice)
async def answer_by_voice(message: types.Message):
    size = message.voice.file_size
    if size < 25000000:
        document = message.voice
        filename = f"{message.from_user.id}.ogg"
        await bot.download(document, destination=filename)
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")

        text_whisper = await whisper(filename)
        logging.debug(f"text_whisper:{text_whisper}")
        remove(filename)

        for text in message_to_tg_chunks(text_whisper):
            await message.reply(f"Text: {text}")
        await answer_on_text(message, text_whisper)
    else:
        await message.reply("Voice to large(>25 Mb)")


@dp.message(F.audio)
async def transribe_audio(message: types.Message):
    size = message.audio.file_size
    if size < 25000000:
        filename = f"{message.from_user.id}.ogg"
        await bot.download(message.audio, destination=filename)
        await bot.send_chat_action(chat_id=message.chat.id, action="typing")

        text_whisper = await whisper(filename)
        logging.debug(f"text_whisper:{text_whisper}")
        remove(filename)

        for text in message_to_tg_chunks(text_whisper):
            await message.reply(f"Text: {text}")
    else:
        await message.reply("Audio to large(>25 Mb)")


@dp.callback_query(LanguageCallbackFactory.filter(F.action == "change"))
async def callbacks_lang_change(
    callback: types.CallbackQuery,
    callback_data: LanguageCallbackFactory,
    state: FSMContext,
):
    user_id = callback.from_user.id
    language = callback_data.value
    logging.debug(
        f'user_id:{user_id}, callback_data: action:{callback_data.action},value:{language}')

    await i18n_midleware.set_locale(state, language)
    await callback.message.edit_text(f"Selected language: {FLAGS[language]['flag']} {language}, {FLAGS[language]['native']}")
    await callback.answer()


@dp.message(F.text)
async def text_handler(message: types.Message) -> None:
    user_message = message.text
    await answer_on_text(message, user_message)


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{config.BASE_WEBHOOK_URL}{config.WEBHOOK_PATH}", drop_pending_updates=True)


def main_webhook() -> None:
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        # secret_token=config.WEBHOOK_SECRET,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=config.WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=config.WEB_SERVER_HOST, port=config.WEB_SERVER_PORT)


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    # And the run events dispatching
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    if config.USE_WEBHOOK:
        main_webhook()
    else:
        asyncio.run(main())
