import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

COUNTRY, SALARY = range(2)

devise_info = {
    "Côte d'Ivoire": {"devise": "FCFA", "seuil_petit": 100000},
    "Sénégal": {"devise": "FCFA", "seuil_petit": 90000},
    "Burkina Faso": {"devise": "FCFA", "seuil_petit": 85000},
    "Mali": {"devise": "FCFA", "seuil_petit": 85000},
    "Togo": {"devise": "FCFA", "seuil_petit": 80000},
    "Bénin": {"devise": "FCFA", "seuil_petit": 80000},
    "France": {"devise": "EUR", "seuil_petit": 1200},
    "Belgique": {"devise": "EUR", "seuil_petit": 1300},
    "Canada": {"devise": "CAD", "seuil_petit": 1500},
}

liste_pays = list(devise_info.keys())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clavier = ReplyKeyboardMarkup(
        [[pays] for pays in liste_pays],
        one_time_keyboard=True,
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Bienvenue sur *MySalaryBot* !\n"
        "Choisis ton pays dans la liste ou écris-le :",
        reply_markup=clavier
    )
    return COUNTRY

async def country(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = update.message.text.strip()
    
    if country not in devise_info:
        await update.message.reply_text(
            "Désolé, ce pays n'est pas encore pris en charge.\n"
            "Merci d'en choisir un dans la liste ou réessaye."
        )
        return COUNTRY

    context.user_data["country"] = country
    await update.message.reply_text(f"Super, tu es en {country}. Quel est ton salaire mensuel en {devise_info[country]['devise']} ?")
    return SALARY

async def salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        salaire = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Merci d'entrer un chiffre valide pour ton salaire.")
        return SALARY

    country = context.user_data["country"]
    info = devise_info[country]
    seuil = info["seuil_petit"]
    devise = info["devise"]

    await update.message.reply_text(f"Dans {country}, voici une répartition budgétaire conseillée :\n"
                                    f"- Loyer : {int(salaire * 0.25)} {devise}\n"
                                    f"- Nourriture : {int(salaire * 0.2)} {devise}\n"
                                    f"- Transport : {int(salaire * 0.1)} {devise}\n"
                                    f"- Factures : {int(salaire * 0.1)} {devise}\n"
                                    f"- Épargne : {int(salaire * 0.1)} {devise}\n"
                                    f"- Loisirs/Divers : {int(salaire * 0.25)} {devise}")

    if salaire < seuil:
        await update.message.reply_text(
            "💡 *Attention, ton salaire semble faible par rapport au coût de la vie.*\n"
            "Voici quelques conseils :\n"
            "- Réduis le loyer si possible.\n"
            "- Épargne même de petites sommes.\n"
            "- Tape /revenus pour des idées pour augmenter tes revenus."
        )
    else:
        await update.message.reply_text(
            "Bonne nouvelle, ton salaire semble correct. Pense à épargner régulièrement !"
        )

    return ConversationHandler.END

async def revenus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💡 Idées simples pour augmenter tes revenus :\n"
        "- Petit commerce local\n"
        "- Services ponctuels (coiffure, baby-sitting)\n"
        "- Apprendre une compétence (graphisme, réseaux sociaux)\n"
        "- Épargne progressive"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Opération annulée. Tape /start pour recommencer.")
    return ConversationHandler.END

def main():
    token = os.getenv("7986723581:AAF63TF8ihVr-OgdeYazlTByJA1BXoar7jY")
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, country)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("revenus", revenus))

    print("Bot lancé...")
    app.run_polling()

if __name__ == "__main__":
    main()
