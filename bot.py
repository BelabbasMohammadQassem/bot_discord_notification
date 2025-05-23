import discord
from discord.ext import commands
import os
import dotenv
import Levenshtein
import time

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

# Dictionnaire pour suivre les réponses aux utilisateurs
user_responses = {}  # Format: {user_id: [(timestamp1, message_id1), (timestamp2, message_id2), ...]}

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

def peut_repondre(user_id):
    """Vérifie si le bot peut répondre à cet utilisateur (max 2 fois par minute)."""
    current_time = time.time()
    
    # Si l'utilisateur n'est pas dans le dictionnaire, on peut répondre
    if user_id not in user_responses:
        user_responses[user_id] = [(current_time, None)]
        return True
    
    # Filtrer les timestamps de moins d'une minute
    recent_responses = [(ts, msg_id) for ts, msg_id in user_responses[user_id] if current_time - ts < 60]
    
    # Mettre à jour la liste des réponses récentes pour cet utilisateur
    user_responses[user_id] = recent_responses
    
    # Si moins de 2 réponses récentes, on peut répondre
    if len(recent_responses) < 2:
        user_responses[user_id].append((current_time, None))
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
        
        # Vérifier si c'est une demande d'aide et si on peut répondre à cet utilisateur
        if contient_demande_aide(contenu) and peut_repondre(user_id):
            response = "👋 Poste ta question dans <#{0}>, <#{1}> ou <#{2}>".format(LOGICIEL_CHANNEL_ID, MATERIEL_CHANNEL_ID, AUTRES_CHANNEL_ID)
            reply = await message.reply(response)
            
            # Mettre à jour l'ID du message de réponse dans le dictionnaire
            recent_responses = user_responses.get(user_id, [])
            if recent_responses:
                # Mettre à jour le dernier élément ajouté avec l'ID du message
                recent_responses[-1] = (recent_responses[-1][0], reply.id)
    
    await bot.process_commands(message)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong! 🏓")

token = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
bot.run(token)
