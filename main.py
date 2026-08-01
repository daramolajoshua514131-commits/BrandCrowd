import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI

# Load local environment variables if available
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Initialize OpenAI Client
client = None

# System prompt templates for specialized design assets
PROMPT_TEMPLATES = {
    "logo": (
        "Professional vector logo design, clean graphic symbol, minimal aesthetic, "
        "high contrast, isolated on a solid light background, vector art style for: "
    ),
    "businesscard": (
        "Professional modern business card design template, realistic layout mockup, "
        "clean typography, minimalist branding style, clear alignment for: "
    ),
    "socialgraphic": (
        "Eye-catching social media banner/post graphic, modern digital marketing aesthetic, "
        "vibrant composition, high quality, professional brand visual for: "
    ),
    "brandkit": (
        "Complete brand identity kit breakdown showing logo mark, color palette swatches, "
        "typography sample, and brand elements arranged neatly on a clean grid layout for: "
    )
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends start instructions with available design commands."""
    welcome_text = (
        "🎨 **Welcome to AI Design Studio Bot!**\n\n"
        "Generate professional design assets using specialized AI commands:\n\n"
        "• `/logo <description>` - Minimal & modern vector logos\n"
        "• `/businesscard <details>` - Professional business card layouts\n"
        "• `/socialgraphic <topic>` - Marketing & social media post visuals\n"
        "• `/brandkit <company>` - Complete brand identity kit grid\n\n"
        "**Example:** `/logo tech startup named CyberSphere with a glowing minimalist globe`"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def generate_design(update: Update, template_type: str, user_description: str):
    """Helper function to format prompts and invoke DALL-E 3 API."""
    if not user_description:
        await update.message.reply_text(
            f"⚠️ Please provide a description after the command.\n"
            f"**Example:** `/{template_type} luxury coffee shop brand`",
            parse_mode="Markdown"
        )
        return

    # Indicate generating state
    await update.message.reply_text("🎨 *Generating your design asset... Please wait 10-15 seconds.*", parse_mode="Markdown")

    # Construct complete prompt
    prefix = PROMPT_TEMPLATES.get(template_type, "")
    full_prompt = f"{prefix} {user_description}"

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt

        # Send generated image back to user
        await update.message.reply_photo(
            photo=image_url,
            caption=f"✨ **Generated Design ({template_type.capitalize()})**\n\n_{user_description}_",
            parse_mode="Markdown"
        )

    except Exception as e:
        logging.error(f"Image generation error: {e}")
        await update.message.reply_text("⚠️ An error occurred while generating the image. Please try again.")

# Command Handlers
async def handle_logo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_desc = " ".join(context.args)
    await generate_design(update, "logo", user_desc)

async def handle_businesscard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_desc = " ".join(context.args)
    await generate_design(update, "businesscard", user_desc)

async def handle_socialgraphic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_desc = " ".join(context.args)
    await generate_design(update, "socialgraphic", user_desc)

async def handle_brandkit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_desc = " ".join(context.args)
    await generate_design(update, "brandkit", user_desc)

if __name__ == "__main__":
    telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip().strip("'\"")
    openai_key = os.environ.get("OPENAI_API_KEY", "").strip().strip("'\"")

    if not telegram_token or not openai_key:
        logging.critical("❌ Missing TELEGRAM_BOT_TOKEN or OPENAI_API_KEY environment variables.")
        exit(1)

    client = OpenAI(api_key=openai_key)

    app = ApplicationBuilder().token(telegram_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("logo", handle_logo))
    app.add_handler(CommandHandler("businesscard", handle_businesscard))
    app.add_handler(CommandHandler("socialgraphic", handle_socialgraphic))
    app.add_handler(CommandHandler("brandkit", handle_brandkit))

    print("🚀 Design Bot is running...")
    app.run_polling(drop_pending_updates=True)
