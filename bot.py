import discord
import json

# Cargar el archivo JSON con las licencias usando codificación utf-8
with open(r'C:\Users\jmmar\Desktop\Bot-Agente\config.json', encoding='utf-8') as f:
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

client.run('MTI3MzU0MjcxODUyMTM0ODEwNw.GUB4KK.a3XfMwBT7Bl9Wj1W9n9qkMLEhPMYMDkavGi0cU')
