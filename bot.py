import discord
import json
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Cargar el archivo JSON con las licencias y los registros de verificación
with open(os.path.join(os.path.dirname(__file__), 'config.json'), encoding='utf-8') as f:
    agentes = json.load(f)["content"]

# Cargar el archivo JSON que contiene los números de licencia ya verificados
verificados_path = os.path.join(os.path.dirname(__file__), 'verificados.json')

# Si el archivo no existe, crear uno nuevo
if not os.path.exists(verificados_path):
    with open(verificados_path, 'w', encoding='utf-8') as vf:
        json.dump({"verificados": []}, vf)

# Cargar los números de licencia ya verificados
with open(verificados_path, encoding='utf-8') as vf:
    verificados = json.load(vf)["verificados"]

# Configurar los intents necesarios
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Crear la instancia del bot
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot {client.user} conectado')

@client.event
async def on_member_join(member):
    await member.send("¡Bienvenido al servidor! Por favor, proporciona tu número de licencia FIFA para verificar tu identidad:")

    def check(m):
        return m.author == member and isinstance(m.channel, discord.DMChannel)

    try:
        msg = await client.wait_for('message', check=check, timeout=300)
        licencia_proporcionada = msg.content.strip()

        if licencia_proporcionada in verificados:
            await member.send("Este número de licencia ya ha sido utilizado. Se ha notificado a los administradores para revisar tu caso.")
            return

        agente_verificado = None
        for agente in agentes:
            if agente["licenseNumber"] == licencia_proporcionada:
                agente_verificado = agente
                break

        if agente_verificado:
            role = discord.utils.get(member.guild.roles, name="Agente FIFA")
            if role:
                await member.add_roles(role)
            await member.send(f"¡Gracias, {agente_verificado['firstName']}! Se ha verificado que eres un Agente FIFA.")
            
            # Registrar el número de licencia como verificado
            verificados.append(licencia_proporcionada)
            with open(verificados_path, 'w', encoding='utf-8') as vf:
                json.dump({"verificados": verificados}, vf)
        else:
            await member.send("No se ha podido verificar que eres un Agente FIFA. Serás removido del servidor.")
            await member.kick(reason="No se verificó como Agente FIFA")
    except discord.errors.Forbidden:
        print(f"No se pudo enviar un mensaje a {member.name}.")
    except discord.errors.HTTPException:
        print("Algo salió mal al intentar verificar al nuevo miembro.")
    except discord.errors.TimeoutError:
        await member.kick(reason="No proporcionó número de licencia a tiempo")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Aquí va el código para manejar las búsquedas de agentes FIFA
    if message.content.startswith('!buscar'):
        partes = message.content.split(maxsplit=2)
        
        if len(partes) < 3:
            await message.channel.send("Formato incorrecto. Usa: !buscar <tipo> <valor>")
            return
        
        tipo = partes[1]
        valor = partes[2].lower()

        # Usar un conjunto para asegurar la unicidad de los agentes
        resultados = set()
        nombres_completos = set()

        if tipo.lower() == "licencia":
            for agente in agentes:
                if agente["licenseNumber"].lower() == valor:
                    resultados.add(agente)
        elif tipo.lower() == "id":
            for agente in agentes:
                if agente["fifaId"].lower() == valor:
                    resultados.add(agente)
        elif tipo.lower() == "nombre":
            for agente in agentes:
                nombre_completo = (agente["firstName"].lower() + " " + agente["lastName"].lower())
                if valor in nombre_completo and nombre_completo not in nombres_completos:
                    resultados.add(agente)
                    nombres_completos.add(nombre_completo)

        if resultados:
            respuesta = "\n\n".join([
                f"Nombre: {agente['firstName']} {agente['lastName']}\nLicencia: {agente['licenseNumber']}\nFIFA ID: {agente['fifaId']}\nEstado: {agente['licenseStatus']}\nAutorizado para menores: {agente['authorisedMinors']}" 
                for agente in resultados
            ])

            if len(respuesta) > 2000:
                for i in range(0, len(respuesta), 2000):
                    await message.channel.send(respuesta[i:i+2000])
            else:
                await message.channel.send(respuesta)
        else:
            await message.channel.send("No se encontraron resultados.")

# Obtener el token de Discord de una variable de entorno
token = os.getenv('DISCORD_TOKEN')

if token is None:
    raise ValueError("El token de Discord no está configurado en las variables de entorno.")

# Ejecutar el bot de Discord
client.run(token)
