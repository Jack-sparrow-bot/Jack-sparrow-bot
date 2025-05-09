import logging
import google.generativeai as genai
from telegram import Update, Bot
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
from MainMenuHandling import *
from VacationHandler import *
date_str = datetime.now().strftime("%d/%m/%y")


GOOGLE_API_KEY = "AIzaSyDjx2MKVIyOB6v9hUrp31qXnl-L4jkrb34"

# Initialize the generative AI model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')



STATE_MAIN , GettingInfo , GettingVacationDays , RequstResultsSTATE , DetectingSoftware ,GettingVacationPurpose , VacationFailed= 0 , 1 , 2 , 3 , 4, 5 , 6




# Set up logging

TOKEN = "7771712926:AAHHSNhvgz3FkvVc92xZzMZQEejYXK1mv6k"


def Modify_Message(update : Update, context: ContextTypes.DEFAULT_TYPE, bot):
    message = update.message
    user = {
        "ID" : update.effective_user.id , 
        "Full Name": f"{update.effective_user.first_name} {update.effective_user.last_name or ''}" ,
        "Username" : update.effective_user.username
    }
    
    is_reply_to_bot = message.reply_to_message and user["ID"] == bot.id
    is_mention = message.entities and any(entity.type == "mention" and message.text[entity.offset:entity.offset + entity.length] == f"@{bot.username}" for entity in message.entities)
    if not (message.chat.type == 'private' or is_reply_to_bot or is_mention):
        return False
    user_message = message.text
    if is_mention:
        user_message = user_message.replace(f"@{bot.username}", "").strip()

    return user_message

# Handle incoming messages
async def Send_Response(update : Update, Response : str):
    await update.message.reply_text(Response)

async def Cancel_Process(update : Update , context: ContextTypes.DEFAULT_TYPE):
    await Send_Response(update, "Your Process is Cancelled, what else can I help you with ?")
    context.user_data["state"] = STATE_MAIN

async def DEEPSEEK_API_CALL(user_input):
    response = model.generate_content(build_prompt(user_input))
    bot_response = response.text.strip()
    return bot_response

def build_prompt(user_input, context=None):
    return  f"""
        You are a helpful Telegram bot assistant named 'JackSparrow'.  +
          Your role is to help sales agents to fix their issue, request days off, get their results
        Respond concisely in markdown. Follow these rules:\n
        - Be polite but informal\n
        - Use bullet points for lists\n
        - Don't add any extra word to your respond, make your response based on my commands
        {user_input}
        """




async def ExtractUserMessage(update : Update, context : ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        return update.message.caption
    else:
        return update.message.text






async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot = await application.bot.get_me()
    user = {
        "ID" : update.effective_user.id , 
        "Full Name": f"{update.effective_user.first_name} {update.effective_user.last_name or ''}" ,
        "Username" : update.effective_user.username
    }
    if Modify_Message(update , context, bot) == False:
        return
    user_message = Modify_Message(update, context, bot)
    try:
        #conversation_history = user_conversations.get(user["ID"], [])
        #conversation_history.append({"role": "user", "parts": [user_message]})
        #response = model.generate_content(conversation_history)
        #bot_response = response.text.strip()
        #conversation_history.append({"role": "model", "parts": [bot_response]})
        #user_conversations[user["ID"]] = conversation_history[-6:]
        #await message.reply_text(bot_response)
        current_state = context.user_data.get("state", STATE_MAIN)
        
        if current_state == STATE_MAIN:
            await HandleMainMenu(update , context)
        
        if current_state == DetectingSoftware:
            await DetectingSoftwareHandler(update, context)
        
        if current_state == GettingInfo:
            await GettingInfoHandler(update , context)
        
        if current_state == GettingVacationDays:
            await HandleVacationDays(update , context)
        
        
    except Exception as e:
        print(f"Error: {str(e)}")
        await message.reply_text("Sorry, something went wrong. Please try again.")

# Start command handler





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = "Hello! I'm a bot powered by Google AI. You can:\n1. DM me directly\n2. Reply to my messages\n3. Mention me with @botname\nAsk me anything!"
    await update.message.reply_text(welcome_message)




# Main function to run the bot
if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO & ~filters.COMMAND, handle_message))
    application.run_polling()
