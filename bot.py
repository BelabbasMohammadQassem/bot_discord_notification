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

# IDs des salons
SALON_SURVEILLE_ID = 1102350490416709672
LOGICIEL_CHANNEL_ID = 1310765800835256350
MATERIEL_CHANNEL_ID = 697726206891655168

# Mots et expressions pour détecter les questions
MOTS_QUESTION = ["comment", "pourquoi", "qui", "quand", "où", "quoi", "quel", "quelle", 
                "quels", "quelles", "est-ce que", "est ce que"]

# Mots et expressions pour détecter les demandes d'aide
MOTS_AIDE = [
    "aide", "aider", "aidez", "help", "besoin", "problème", "probleme", "bug",
    "erreur", "error", "ne fonctionne pas", "marche pas", "ne marche pas", "ne parviens pas",
    "bloqué", "bloque", "coincé", "solution", "résoudre", "résolu", "resoudre",
    "comprends pas", "comprend pas", "soutien", "support", "dépanner", "réparer",
    "répare", "galère", "galere", "impossible de", "difficulté", "difficulte",
    "souci", "préoccupation", "assistance", "secours", "rencontre un problème",
    "rencontre un probleme", "cherche une solution", "à l'aide", "a l'aide",
    "issue", "troubleshoot", "fix", "broken", "stuck", "struggle", "struggling",
    "can't", "cant", "unable to", "help me", "anyone know", "quelqu'un sait"
]

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

def contient_demande_aide(texte):
    """Vérifie si le texte contient des mots ou expressions liés à une demande d'aide."""
    texte_lower = texte.lower()
    
    # Vérifier les mots individuels
    mots = texte_lower.split()
    for mot in mots:
        if mot in MOTS_AIDE:
            return True
    
    # Vérifier les expressions plus longues
    for expression in MOTS_AIDE:
        if " " in expression and expression in texte_lower:
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
        est_demande_aide = False
        
        # Vérifier si c'est une question basée sur la ponctuation ou les mots interrogatifs
        if "?" in contenu:
            est_question = True
        
        for mot in MOTS_QUESTION:
            if contenu.startswith(mot + " "):
                est_question = True
                break
        
        if not est_question and len(contenu) > 5:  
            est_question = contient_mot_question_avec_fautes(contenu)
        
        # Vérifier si c'est une demande d'aide
        if not est_question:
            est_demande_aide = contient_demande_aide(contenu)
        
        # Répondre si c'est une question ou une demande d'aide
        if est_question or est_demande_aide:
            if est_question:
                response = f"{message.author.mention}, merci d'utiliser les salons <#{LOGICIEL_CHANNEL_ID}>  ou <#{MATERIEL_CHANNEL_ID}> pour vos questions."
            else:
                response = f"{message.author.mention}, j'ai détecté que vous avez besoin d'aide. Merci de poster votre demande dans <#{LOGICIEL_CHANNEL_ID}> ou <#{MATERIEL_CHANNEL_ID}>."
            
            await message.reply(response)
    
    await bot.process_commands(message)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓")

token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(token)
