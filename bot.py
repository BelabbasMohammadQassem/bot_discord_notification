import discord
from discord.ext import commands
import os
import dotenv
import time
import re

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

# Mots et expressions qui indiquent clairement une demande d'aide
MOTS_AIDE_STRICTS = [
    "aidez-moi", "j'ai besoin d'aide", "je ne sais pas comment", "comment faire pour",
    "quelqu'un peut m'aider", "help me", "need help", "j'ai un problème avec",
    "je n'arrive pas à", "je ne parviens pas à", "ça ne marche pas", "ca marche pas",
    "comment je peux", "savez-vous comment", "quelqu'un sait comment", "je suis bloqué sur",
    "je suis coincé", "j'ai une erreur", "ça bug", "ca bug", "ne fonctionne plus",
    "impossible de", "comment résoudre", "j'ai essayé mais", "quelqu'un pour m'aider"
]

# Mots indicateurs de demande d'aide potentielle (nécessitent confirmation par le contexte)
MOTS_AIDE = [
    "aide", "aider", "help", "problème", "probleme", "bug", "erreur", "error",
    "bloqué", "coincé", "solution", "résoudre", "comprends pas", "comprend pas",
    "soutien", "support", "dépanner", "réparer", "galère", "galere", "difficulté",
    "difficulte", "souci", "assistance", "secours", "beug", "bugg"
]

# Expressions ou mots qui indiquent qu'il ne s'agit PAS d'une demande d'aide
CONTEXTE_NON_AIDE = [
    "pas de problème", "pas de souci", "pas besoin d'aide", "sans problème",
    "sans souci", "aucun problème", "aucun souci", "c'est", "le but", "permet de",
    "sert à", "fonction", "fonctionnalité", "pour", "afin de", "cela permet",
    "explique", "montre", "présente", "démontre", "simule", "simulant", "en simulant"
]

# Mots indiquant un contexte informatif plutôt qu'une demande d'aide
MOTS_CONTEXTE_INFORMATIF = [
    "car", "parce que", "puisque", "c'est pour", "c'est un", "c'est une",
    "il s'agit de", "cela signifie", "voici comment", "c'est ainsi que",
    "fonctionne", "utiliser", "utilise", "usage", "but", "objectif",
    "permet", "permettre", "pouvoir", "peut", "manière", "façon"
]

# Dictionnaire pour stocker le dernier timestamp de réponse par utilisateur
last_response_time = {}

def contient_demande_aide(texte):
    """Analyse sophistiquée pour déterminer si le message contient une réelle demande d'aide."""
    texte_lower = texte.lower()
    
    # 1. Vérifier les expressions qui indiquent clairement une non-demande d'aide
    for expression in CONTEXTE_NON_AIDE:
        if expression in texte_lower:
            return False
    
    # 2. Vérifier les expressions qui indiquent clairement une demande d'aide (priorité haute)
    for expression in MOTS_AIDE_STRICTS:
        if expression in texte_lower:
            return True
    
    # 3. Analyse de contexte informatif
    mots_informatifs = sum(1 for mot in MOTS_CONTEXTE_INFORMATIF if mot in texte_lower)
    if mots_informatifs >= 2:  # Si au moins deux mots indiquent un contexte informatif
        return False
    
    # 4. Vérifier si la phrase commence par des mots typiques d'explication
    premiers_mots = texte_lower.split()[:3]  # Prendre les 3 premiers mots
    if any(mot in premiers_mots for mot in ["car", "parce", "puisque", "c'est", "le"]):
        # Si la phrase commence par ces mots, c'est probablement une explication et non une demande
        return False
    
    # 5. Compteur de mots d'aide
    compteur_mots_aide = sum(1 for mot in MOTS_AIDE if f" {mot} " in f" {texte_lower} " or 
                             texte_lower.startswith(f"{mot} ") or texte_lower.endswith(f" {mot}"))
    
    # 6. Analyse des formes interrogatives (plus susceptibles d'être des demandes d'aide)
    est_question = "?" in texte or any(texte_lower.startswith(mot) for mot in 
                                      ["comment", "pourquoi", "est-ce", "est ce", "quelqu'un", 
                                       "qui", "quand", "où", "ou"])
    
    # Décision finale basée sur plusieurs facteurs
    if est_question and compteur_mots_aide >= 1:
        return True
    elif compteur_mots_aide >= 2:  # Exiger au moins deux mots d'aide distincts si ce n'est pas une question
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
        contenu = message.content
        user_id = message.author.id
        
        # Vérifier si c'est une demande d'aide
        if contient_demande_aide(contenu):
            current_time = time.time()
            
            # Vérifier si l'utilisateur a déjà reçu une réponse dans les 2 dernières minutes
            if user_id not in last_response_time or (current_time - last_response_time[user_id]) >= 120:
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
