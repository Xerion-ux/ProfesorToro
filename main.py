import discord
from discord import app_commands
import requests
import random
import time
import os

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("No se encontró el TOKEN")

GUILD_ID = 1280336369969004620
COOLDOWN = 5

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
user_cooldowns = {}

def buscar_imagen(tag: str = None):
    base_url = "https://danbooru.donmai.us/posts.json"
    params = {"limit": 100}
    if tag:
        params["tags"] = tag

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error al buscar imagen: {e}")
        return None

    if not data:
        return None

    # Filtrar solo posts con file_url
    posts_con_imagen = [post for post in data if post.get("file_url")]
    if not posts_con_imagen:
        return None

    post = random.choice(posts_con_imagen)
    return post.get("file_url")

@tree.command(
    name="image",
    description="Buscar imagen en Danbooru (tag opcional)",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(tag="Tag opcional")
async def image(interaction: discord.Interaction, tag: str = None):
    user_id = interaction.user.id
    now = time.time()

    if user_id in user_cooldowns and now - user_cooldowns[user_id] < COOLDOWN:
        await interaction.response.send_message(
            f"Espera {COOLDOWN}s entre usos ⏱", ephemeral=True
        )
        return

    user_cooldowns[user_id] = now

    if not interaction.channel.is_nsfw():
        await interaction.response.send_message(
            "Solo en canales NSFW 🔞", ephemeral=True
        )
        return

    await interaction.response.defer()
    img_url = buscar_imagen(tag)
    if not img_url:
        await interaction.followup.send("No encontré resultados 😢")
        return

    # Crear embed con la imagen
    embed = discord.Embed(
        title="Imagen de Danbooru",
        description=f"Tag: `{tag}`" if tag else "Tag: aleatorio",
        color=discord.Color.random()
    )
    embed.set_image(url=img_url)
    await interaction.followup.send(embed=embed)

@client.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    await tree.sync(guild=guild)
    print(f"Conectado como {client.user}")

client.run(TOKEN)
