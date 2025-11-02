from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8321950419:AAEyAnjqPXmMDpDNmQWJ048cnp6-ibVzRhs"
ADMIN_ID = 7927748815

PRODUCTS = {
    "syberia": 5,
    "pablo": 5,
    "velo": 5
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sveikas! 👋\n"
        "Įrašyk produktą ir kiekį, pvz:\n\n"
        "Syberia 3\nPablo 2\nVelo 10"
    )

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.lower().strip()
    parts = text.split()

    if len(parts) != 2:
        return await update.message.reply_text("⚠️ Formatas: Produktas Kiekis")

    product, quantity_str = parts

    if product not in PRODUCTS:
        return await update.message.reply_text("❌ Galimi: Syberia, Pablo, Velo")

    if not quantity_str.isdigit():
        return await update.message.reply_text("❌ Kiekis turi būti skaičius")

    quantity = int(quantity_str)
    total_price = PRODUCTS[product] * quantity

    await update.message.reply_text(
        f"✅ Užsakymas priimtas!\n"
        f"📦 {product.capitalize()} x{quantity}\n"
        f"💶 {total_price}€\n"
        f"⚠️ Palaukite, kol pardavėjas patvirtins."
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📩 *Naujas užsakymas*\n"
            f"👤 {user.first_name} (@{user.username})\n"
            f"ID: {user.id}\n"
            f"📦 {product.capitalize()} x{quantity}\n"
            f"💶 {total_price}€\n\n"
            f"🧾 Kai paruoši linką, parašyk:\n"
            f"/send {user.id} LINKAS"
        ),
        parse_mode="Markdown"
    )

async def send_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    parts = update.message.text.split(maxsplit=2)
    if len(parts) != 3:
        return await update.message.reply_text("⚠️ Naudok formatą: /send USER_ID LINK")

    _, user_id, link = parts

    try:
        user_id = int(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Užsakymas paruoštas!\n🔗 {link}"
        )
        await update.message.reply_text("✅ Išsiųsta klientui")
    except:
        await update.message.reply_text("❌ Nepavyko išsiųsti")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_link))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))

    app.run_polling()

if __name__ == "__main__":
    main()

