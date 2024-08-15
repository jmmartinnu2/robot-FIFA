import discord
import json
import os
from dotenv import load_dotenv
import streamlit as st

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Configurar Streamlit
st.title("Bot FIFA")
st.write("Interfaz para controlar y monitorear el bot de Discord.")

# Cargar el archivo JSON con las licencias usando una ruta relativa
with open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8') as f:
    agentes = json.load(f)["content"]

# Mostrar información básica o logs en Streamlit
st.write("Número de agentes cargados:", len(agentes))

# Configurar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True

# Crear la instancia del bot
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    st.write(f'Bot {client.user} conectado')
    print(f'Bot {client.user} conectado')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!buscar'):
        partes = message.content.split(maxsplit=2)
        
        if len(partes) < 3:
            await message.channel.send("Formato incorrecto. Usa: !buscar <tipo> <valor>")
            return
        
        tipo = partes[1]
        valor = partes[2].lower()

        resultados = []

        if tipo.lower() == "licencia":
            resultados = [agente for agente in agentes if agente["licenseNumber"].lower() == valor]
        elif tipo.lower() == "id":
            resultados = [agente for agente in agentes if agente["fifaId"].lower() == valor]
        elif tipo.lower() == "nombre":
            resultados = [agente for agente in agentes if valor in (agente["firstName"].lower() + " " + agente["lastName"].lower())]

        if resultados:
            respuesta = "\n\n".join([f"Nombre: {agente['firstName']} {agente['lastName']}\nLicencia: {agente['licenseNumber']}\nFIFA ID: {agente['fifaId']}\nEstado: {agente['licenseStatus']}\nAutorizado para menores: {agente['authorisedMinors']}" for agente in resultados])
        else:
            respuesta = "No se encontraron resultados."

        await message.channel.send(respuesta)

# Obtener el token de una variable de entorno
token = os.getenv('DISCORD_TOKEN')

if token is None:
    st.error("El token de Discord no está configurado en las variables de entorno.")
    raise ValueError("El token de Discord no está configurado en las variables de entorno.")

# Ejecutar el bot de Discord
client.run(token)
