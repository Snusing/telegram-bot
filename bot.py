from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "8321950419:AAEyAnjqPXmMDpDNmQWJ048cnp6-ibVzRhs"
ADMIN_ID = 7927748815  # Įrašytas tavo ID ✅

TEMPLATE_URL = "https://www.vinted.lt/items/7444829312/edit"

PRODUCTS = {
    "syberia": 5,
    "pablo": 5,
    "velo": 5
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sveikas 👋\n"
        "Įrašyk produktą ir kiekį, pvz:\n\n"
        "Syberia 3\n"
        "Pablo 2\n"
        "Velo 10"
    )

async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        text = update.message.text.lower().strip()
        parts = text.split()

        if len(parts) != 2:
            return await update.message.reply_text("⚠️ Formatas: Produktas Kiekis (pvz: Syberia 3)")

        product, quantity_str = parts

        if product not in PRODUCTS:
            return await update.message.reply_text("❌ Tokio produkto nėra. Galimi: Syberia, Pablo, Velo")

        if not quantity_str.isdigit():
            return await update.message.reply_text("❌ Kiekis turi būti skaičius")

        quantity = int(quantity_str)
        total_price = PRODUCTS[product] * quantity

        # Paruošti mygtuką
        final_url = f"{TEMPLATE_URL}?title={product}+x{quantity}&price={total_price}"
        button = InlineKeyboardButton("✅ Patvirtinti Vinted skelbimą", url=final_url)
        keyboard = InlineKeyboardMarkup([[button]])

        await update.message.reply_text(
            f"✅ Užsakymas:\n\n"
            f"📦 Produktas: {product.capitalize()}\n"
            f"🔢 Kiekis: {quantity}\n"
            f"💶 Kaina: {total_price}€\n\n",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text("❌ Tu nesi administratorius.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚠️ Nesupratau. Parašyk pvz: Syberia 3")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
    app.run_polling()

if __name__ == "__main__":
    main()
