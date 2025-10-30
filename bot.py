from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import urllib.parse

TOKEN = "8321950419:AAEyAnjqPXmMDpDNmQWJ048cnp6-ibVzRhs"
ADMIN_ID = 7927748815  # tavo telegram ID

TEMPLATE_URL = "https://www.vinted.lt/items/7444829312"

PRODUCTS = {
    "syberia": 5,
    "pablo": 5,
    "velo": 5
}

pending_orders = {}  # laikysim laikinai užsakymą pagal user ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sveikas 👋\n"
        "Įrašyk prekę ir kiekį, pvz:\n"
        "Syberia 3\n\n"
        "Prekės: Syberia / Pablo / Velo"
    )


async def handle_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()
    parts = text.split()

    if len(parts) != 2:
        return await update.message.reply_text("⚠️ Format: Produktas Kiekis (pvz: Syberia 3)")

    product, q = parts

    if product not in PRODUCTS:
        return await update.message.reply_text("❌ Tokio produkto nėra. Galimi: Syberia, Pablo, Velo")

    if not q.isdigit():
        return await update.message.reply_text("❌ Kiekis turi būti skaičius")

    quantity = int(q)
    total = PRODUCTS[product] * quantity
    user_id = update.message.from_user.id

    pending_orders[user_id] = {
        "product": product,
        "quantity": quantity,
        "total": total,
        "chat_id": update.message.chat_id
    }

    # klientui
    await update.message.reply_text("✅ Užsakymas gautas, ruošiame prekę 👌\nLiks tik paspausti nuorodą.")


    # adminui pranešimas
    keyboard = [
        [
            InlineKeyboardButton("✅ Paruošta", callback_data=f"ok_{user_id}"),
            InlineKeyboardButton("❌ Atmesti", callback_data=f"no_{user_id}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📦 Naujas užsakymas!\n\n"
             f"👤 Klientas ID: {user_id}\n"
             f"🛍️ Produktas: {product.capitalize()}\n"
             f"🔢 Kiekis: {quantity}\n"
             f"💰 Kaina: {total}€\n\n"
             f"Pasiruošęs siųsti?",
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, user = query.data.split("_")
    user = int(user)

    if action == "ok":
        if user in pending_orders:
            order = pending_orders[user]
            params = urllib.parse.urlencode({
                "title": f"{order['product'].capitalize()} x{order['quantity']}",
                "price": order['total']
            })

            link = f"{TEMPLATE_URL}?{params}"

            await context.bot.send_message(
                chat_id=order["chat_id"],
                text=f"✅ Užsakymas paruoštas!\nSpausk čia 👇\n{link}"
            )

            await query.edit_message_text("✅ Išsiųsta klientui!")
            del pending_orders[user]

    else:
        await context.bot.send_message(
            chat_id=user,
            text="❌ Užsakymas atšauktas."
        )
        await query.edit_message_text("🚫 Atmesta.")
        if user in pending_orders:
            del pending_orders[user]


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_order))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
