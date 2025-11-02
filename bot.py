from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "8321950419:AAEyAnjqPXmMDpDNmQWJ048cnp6-ibVzRhs"
ADMIN_ID = 7927748815  

PRODUCTS = {
    "syberia": 5,
    "pablo": 5,
    "velo": 5
}

pending_orders = {}  # user_id -> admin_wait_state

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sveikas 👋\n\n"
        "Įrašyk produktą ir kiekį, pvz:\n\n"
        "Syberia 3\nPablo 2\nVelo 10"
    )

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.lower().strip()
    parts = text.split()

    if len(parts) != 2:
        return await update.message.reply_text("⚠️ Formatas: Produktas Kiekis (pvz: Syberia 3)")

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
        f"💶 {total_price}€"
    )

    # Mygtukas adminui
    keyboard = [
        [InlineKeyboardButton("✅ Paruošta", callback_data=f"ready_{user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 *Naujas užsakymas*\n"
             f"👤 {user.first_name} (ID: {user.id})\n"
             f"📦 {product.capitalize()} x{quantity}\n"
             f"💶 {total_price}€\n\n"
             f"Paspausk 'Paruošta' kai turėsi link.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("ready_") and query.from_user.id == ADMIN_ID:
        user_id = int(data.split("_")[1])
        pending_orders[ADMIN_ID] = user_id
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="Įklijuok Vinted nuorodą 👇"
        )

async def handle_admin_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id == ADMIN_ID and ADMIN_ID in pending_orders:
        user_id = pending_orders.pop(ADMIN_ID)
        link = update.message.text

        # Siunčiam klientui
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Jūsų užsakymas paruoštas!\n🔗 {link}"
        )

        # Patvirtinimas adminui
        await update.message.reply_text("🔥 Išsiųsta klientui!")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_link))  # admin link handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
