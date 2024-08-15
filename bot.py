import discord
import json
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Cargar el archivo JSON con las licencias usando una ruta relativa
with open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8') as f:
    agentes = json.load(f)["content"]

# Configurar los intents necesarios
intents = discord.Intents.default()
intents.message_content = True

# Crear la instancia del bot
client = discord.Client(intents=intents)

@client.event
async def on_ready():
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

        # Usar un conjunto para eliminar duplicados
        resultados = set()

        if tipo.lower() == "licencia":
            resultados = {agente for agente in agentes if agente["licenseNumber"].lower() == valor}
        elif tipo.lower() == "id":
            resultados = {agente for agente in agentes if agente["fifaId"].lower() == valor}
        elif tipo.lower() == "nombre":
            resultados = {agente for agente in agentes if valor in (agente["firstName"].lower() + " " + agente["lastName"].lower())}

        if resultados:
            respuesta = "\n\n".join([f"Nombre: {agente['firstName']} {agente['lastName']}\nLicencia: {agente['licenseNumber']}\nFIFA ID: {agente['fifaId']}\nEstado: {agente['licenseStatus']}\nAutorizado para menores: {agente['authorisedMinors']}" for agente in resultados])

            # Verificar si la respuesta es demasiado larga
            if len(respuesta) > 2000:
                for i in range(0, len(respuesta), 2000):  # Dividir si la respuesta es larga
                    await message.channel.send(respuesta[i:i+2000])
            else:
                await message.channel.send(respuesta)  # Enviar todo en un solo mensaje si no es demasiado largo
        else:
            await message.channel.send("No se encontraron resultados.")

# Obtener el token de Discord de una variable de entorno
token = os.getenv('DISCORD_TOKEN')

if token es None:
    raise ValueError("El token de Discord no está configurado en las variables de entorno.")

# Ejecutar el bot de Discord
client.run(token)
