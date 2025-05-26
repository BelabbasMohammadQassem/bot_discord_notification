import discord
from discord.ext import commands
import os
import dotenv
import time
import difflib

dotenv.load_dotenv()

# Configuration du bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# IDs des salons
SALON_SURVEILLE_ID = 1102350490416709672
LOGICIEL_CHANNEL_ID = 1310765800835256350
MATERIEL_CHANNEL_ID = 697726206891655168
AUTRES_CHANNEL_ID = 1313130476093046835

# Mots et expressions pour détecter les demandes d'aide
MOTS_AIDE = [
    "aide", "aider", "aidez", "help", "besoin", "problème", "probleme", "problèm", "problém", "problàme",
    "probleme", "problèmes", "problemes", "pb", "bug", "erreur", "error", "ne fonctionne pas", 
    "marche pas", "ne marche pas", "ne parviens pas", "bloqué", "bloque", "coincé", "solution", 
    "résoudre", "résolu", "resoudre", "réglé", "reglé", "comprends pas", "comprend pas", 
    "soutien", "support", "dépanner", "réparer", "répare", "galère", "galere", "impossible de", 
    "difficulté", "difficulte", "souci", "préoccupation", "assistance", "secours", 
    "rencontre un problème", "rencontre un probleme", "cherche une solution", 
    "à l'aide", "a l'aide", "issue", "troubleshoot", "fix", "broken", "stuck", 
    "struggle", "struggling", "can't", "cant", "unable to", "help me", "anyone know", 
    "quelqu'un sait", "beug", "bugg"
]

# Dictionnaire pour stocker le dernier timestamp de réponse par utilisateur
last_response_time = {}

def mots_similaires(mot, liste_mots, seuil=0.85):
    """Vérifie si un mot est similaire à l'un des mots de la liste avec un seuil donné."""
    for mot_cible in liste_mots:
        if len(mot) > 3 and len(mot_cible) > 3:  # Ignorer les mots trop courts
            ratio = difflib.SequenceMatcher(None, mot, mot_cible).ratio()
            if ratio >= seuil:
                return True
    return False

def contient_demande_aide(texte):
    """Vérifie si le texte contient des mots ou expressions liés à une demande d'aide, même avec des fautes."""
    texte_lower = texte.lower()
    
    # Vérifier les mots individuels
    mots = texte_lower.split()
    for mot in mots:
        # Vérification exacte
        if mot in MOTS_AIDE:
            return True
        
        # Vérification de similarité pour les mots plus longs
        if len(mot) > 3 and mots_similaires(mot, MOTS_AIDE):
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
        user_id = message.author.id
        
        # Vérifier si c'est une demande d'aide
        if contient_demande_aide(contenu):
            current_time = time.time()
            
            # Vérifier si l'utilisateur a déjà reçu une réponse dans les 5 dernières minutes
            if user_id not in last_response_time or (current_time - last_response_time[user_id]) >= 120:  # 300 secondes = 5 minutes
                response = "👋 Poste ta question dans <#{0}>, <#{1}> ou <#{2}>".format(
                    LOGICIEL_CHANNEL_ID, MATERIEL_CHANNEL_ID, AUTRES_CHANNEL_ID
                )
                await message.reply(response)
                
                # Enregistrer le timestamp de cette réponse
                last_response_time[user_id] = current_time
    
    await bot.process_commands(message)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓")

token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(token)
