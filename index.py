import instaloader
import requests
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Instagram loader
loader = instaloader.Instaloader()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Salom! Instagram havolasini yuboring.")


def fetch_instagram_media(url):
    try:
        # Instagram postdan shortcode olish
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.is_video:
            response = requests.get(post.video_url, stream=True)
            if response.status_code == 200:
                media = BytesIO(response.content)
                media.seek(0)
                return media, "video"
        else:
            response = requests.get(post.url, stream=True)
            if response.status_code == 200:
                media = BytesIO(response.content)
                media.seek(0)
                return media, "image"
    except Exception as e:
        return None, str(e)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if "instagram.com" in url:
        await update.message.reply_text("Media yuklanmoqda. Bir oz kuting...")
        media, media_type = fetch_instagram_media(url)

        if media:
            try:
                # Rasm yoki video bilan matnni bitta narsa sifatida yuborish
                caption_text = ("📥 @InstaSaveTobot  yordamida yuklangan."
                                "\n📥 Uploaded using @InstaSaveTobot.")
                if media_type == "video":
                    # Video bilan bitta matnni yuborish
                    await context.bot.send_video(chat_id=update.effective_chat.id, video=media, caption=caption_text)
                else:
                    # Rasm bilan bitta matnni yuborish
                    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=media, caption=caption_text)
            except Exception as e:
                await update.message.reply_text(f"Xato: {e}")
        else:
            await update.message.reply_text(f"Media yuklashda xato: {media_type}")
    else:
        await update.message.reply_text("Iltimos, haqiqiy Instagram post havolasini yuboring.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Xatolik yuz berdi: {context.error}")


if __name__ == "__main__":
    TOKEN = "7987605938:AAFdM74GYwBx2pcgxAWJ6OPAgPyvpvbmObc"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.add_error_handler(error_handler)

    print("Bot ishga tushdi...")
    application.run_polling()
