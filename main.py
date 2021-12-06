from aiogram import executor

import bot


executor.start_polling(
    bot.dp,
    skip_updates=True,
    on_shutdown=bot.on_shutdown
    )