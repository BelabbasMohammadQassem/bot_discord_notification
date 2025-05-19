import discord
from discord.ext import commands
import os
import dotenv
import Levenshtein


dotenv.load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


SALON_SURVEILLE_ID = 1102350490416709672 


LOGICIEL_CHANNEL_ID = 1310765800835256350  
MATERIEL_CHANNEL_ID = 697726206891655168  


MOTS_QUESTION = ["comment", "pourquoi", "qui", "quand", "où", "quoi", "quel", "quelle", 
                "quels", "quelles", "est-ce que", "est ce que"]


SIMILARITE_THRESHOLD = 0.75

def est_similaire_a_un_mot_question(mot, longueur_minimum=3):
    """Vérifie si un mot est similaire à un mot de question connu."""
    if len(mot) < longueur_minimum:
        return False
        
    for mot_question in MOTS_QUESTION:
        
        similarite = Levenshtein.ratio(mot, mot_question)
        if similarite >= SIMILARITE_THRESHOLD:
            return True
    return False

def contient_mot_question_avec_fautes(texte):
    """Analyse le texte pour trouver des mots similaires aux mots de questions."""
    mots = texte.lower().split()
    
    
    for i in range(min(3, len(mots))):
        if est_similaire_a_un_mot_question(mots[i]):
            return True
    return False

@bot.event
async def on_ready():
    print(f'{bot.user.name} est connecté et prêt!')
    print(f'ID du bot: {bot.user.id}')
    print('------')

@bot.event
async def on_message(message):
    
    if message.author == bot.user:
        return
    
    
    if message.channel.id == SALON_SURVEILLE_ID:
        contenu = message.content.lower()
        
        
        est_question = False
        
        
        if "?" in contenu:
            est_question = True
        
        
        for mot in MOTS_QUESTION:
            if contenu.startswith(mot + " "):
                est_question = True
                break
        
        
        if not est_question and len(contenu) > 5:  
            est_question = contient_mot_question_avec_fautes(contenu)
        
        
        if est_question:
            response = f"{message.author.mention}, merci d'utiliser les salons <#{LOGICIEL_CHANNEL_ID}> (logiciel) ou <#{MATERIEL_CHANNEL_ID}> (matériel) pour vos questions."
            await message.reply(response)
    
    
    await bot.process_commands(message)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓")


token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(token)
