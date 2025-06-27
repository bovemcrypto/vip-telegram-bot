import requests
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "7663161973:AAEY74Dq-sg8c5-cx2lpoYU-_YBeWPiDUxI"

WALLETS = {
    "BTC": "1CE2m4QwLUkL8z4ZQTqrbDEkofEMFk4qyZ",
    "ETH": "0xcffbd451c11b571caa92bddc7d5118ee6b08133f",
    "SOL": "3uU2iqUF1tqpZCYCDSbp6ym3yqW2c6PxShZP72qdUxAF"
}

PRICES = {
    "1month": 99,
    "3months": 199,
    "1year": 499
}

# Cache za cene
cache = {}
CACHE_EXPIRY = 60  # Cache traja 60 sekund

def get_price(coin_id: str) -> float:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[coin_id]['usd']
    except Exception as e:
        print(f"Error fetching price for {coin_id}: {e}")
        return None

def get_price_cached(coin_id: str) -> float:
    now = time.time()
    if coin_id in cache:
        cached_price = cache[coin_id]['price']
        cached_time = cache[coin_id]['timestamp']
        if now - cached_time < CACHE_EXPIRY:
            return cached_price

    # Če cache ni veljaven ali ne obstaja, pokliči API
    price = get_price(coin_id)
    if price is not None:
        cache[coin_id] = {'price': price, 'timestamp': now}
    return price

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Bovem signals: 99 USD / 1 month", callback_data='plan_1month')],
        [InlineKeyboardButton("Bovem signals: 199 USD / 3 months", callback_data='plan_3months')],
        [InlineKeyboardButton("Bovem signals: 499 USD / 1 year", callback_data='plan_1year')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚀 Maximize Profits with Our VIP Signals!\n\n"
        "👑 VIP Plan Includes:\n"
        "💎 High-Accuracy Futures Signals\n"
        "💎 5–50 Daily Crypto Signals\n"
        "💎 Up to 2000% Profit Potential\n"
        "💎 Beginner's Guide & Support\n"
        "💎 Simple Copy-Trade Signals\n"
        "💎 Entry, Take-Profit & Stop Loss Targets\n"
        "💎 Dedicated Support Team\n\n"
        "💬 Contact us: @bovemcrypto\n"
        "📣 Public Channel: [Click here to join](https://t.me/+OSox_uy2XmM4MGZk)\n\n"
        "👇 Select your plan below to unlock VIP Access:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )



async def plan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = query.data.split("_")[1]
    context.user_data["selected_plan"] = plan

    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='coin_BTC')],
        [InlineKeyboardButton("ETH", callback_data='coin_ETH')],
        [InlineKeyboardButton("SOL", callback_data='coin_SOL')],
        [InlineKeyboardButton("⬅ Back", callback_data='back_to_plans')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if plan == "1month":
        text = (
            "🚀 Bovem Signals\n"
            "💰 $99 for 1 Month Access\n\n"
            "By completing this order, you will receive access to the following signals:\n"
            "📈 Bovem VIP 💎 High Leverage & Long-Term Trades\n\n"
            "You’ll get full access to premium crypto signals, expert guidance, and continuous support to help you grow your portfolio.\n\n"
            "👇 Choose your payment method below:"
        )
    elif plan == "3months":
        text = (
            "🚀 Bovem Signals\n"
            "💰 $199 for 3 Months Access\n\n"
            "By completing this order, you will receive access to the following signals:\n"
            "📈 Bovem VIP 💎 High Leverage & Long-Term Trades\n\n"
            "Lock in 3 months of premium signals at a discounted rate. Get more time to develop consistent profits with expert guidance and timely updates.\n\n"
            "👇 Choose your payment method below:"
        )
    elif plan == "1year":
        text = (
            "🚀 Bovem Signals\n"
            "💰 $499 for 1 Year Access\n\n"
            "By completing this order, you will receive access to the following signals:\n"
            "📈 Bovem VIP 💎 High Leverage & Long-Term Trades\n\n"
            "Get the best value for your money. Enjoy uninterrupted access to elite signals, daily trade ideas, and full support — all year long.\n\n"
            "👇 Choose your payment method below:"
        )
    else:
        text = "Invalid plan selected."

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def coin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    coin = query.data.split("_")[1]
    plan = context.user_data.get("selected_plan")
    if not plan:
        await query.edit_message_text("Please start again with /start")
        return

    price_usd = PRICES[plan]

    coin_id_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana"
    }

    coin_id = coin_id_map.get(coin)
    if coin_id is None:
        await query.edit_message_text("Unknown coin selected.")
        return

    current_price = get_price_cached(coin_id)
    if current_price is None:
        await query.edit_message_text("Error fetching current price. Please try again later.")
        return

    amount = price_usd / current_price
    amount_str = f"{amount:.8f}"
    wallet_address = WALLETS[coin]

    keyboard = [[InlineKeyboardButton("⬅ Back", callback_data='back_to_coins')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        f"💳 *Please complete the following payment:*\n\n"
        f"• *Amount:* `{amount_str} {coin}`\n"
        f"• *Network:* {coin}\n"
        f"• *Deposit Address (click to copy):* `{wallet_address}`\n\n"
        f"⚠️ *Please send the exact amount (after fees).*\n\n"
        f"📌 *Important:*\n"
        f"- Send only {coin} to this address. Sending any other currency may result in the loss of your funds.\n"
        f"- After sending the payment, wait at least *15 minutes* after the first confirmation.\n\n"
        f"📩 After confirmation, contact support: [@bovemcrypto](https://t.me/bovemcrypto)\n\n"
        f"❌ *This order will be automatically canceled in 6 hours if no payment is received.*"
    )

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def back_to_plans_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("1 Month – 99 $", callback_data='plan_1month')],
        [InlineKeyboardButton("3 Months – 199 $", callback_data='plan_3months')],
        [InlineKeyboardButton("1 Year – 499 $", callback_data='plan_1year')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        "👋 Welcome to the VIP Crypto Signals Bot!\n\nChoose your subscription plan:",
        reply_markup=reply_markup
    )

async def back_to_coins_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan = context.user_data.get("selected_plan")
    if not plan:
        await query.edit_message_text("Please start again with /start")
        return
    keyboard = [
        [InlineKeyboardButton("BTC", callback_data='coin_BTC')],
        [InlineKeyboardButton("ETH", callback_data='coin_ETH')],
        [InlineKeyboardButton("SOL", callback_data='coin_SOL')],
        [InlineKeyboardButton("⬅ Back", callback_data='back_to_plans')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        f"You selected *{plan.replace('1month', '1 Month').replace('3months', '3 Months').replace('1year', '1 Year')}*.\n"
        "Now choose your payment coin:",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(plan_handler, pattern="^plan_"))
    app.add_handler(CallbackQueryHandler(coin_handler, pattern="^coin_"))
    app.add_handler(CallbackQueryHandler(back_to_plans_handler, pattern="^back_to_plans$"))
    app.add_handler(CallbackQueryHandler(back_to_coins_handler, pattern="^back_to_coins$"))

    print("Bot is running...")
    app.run_polling()
