import discord
from datetime import datetime
import sheetd
import os
from dotenv import load_dotenv

load_dotenv()
bot = discord.Bot()
TOKEN = os.getenv("TOKEN")

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} is online and ready!")


@bot.slash_command(name="add_account", description="Add a new game account to the database")
async def add_account(
    ctx: discord.ApplicationContext,
    login_type: str,
    username: str,
    password: str,
    shiny: int,
    shiny_bg: int,
    legendary: int,
    shiny_legendary: int,
    hundo: int,
    level50: int,
    pokecoins: int,
    pokemon_storage: int,
    bag_space: int
): 
    await ctx.respond("Adding Account Please Wait ",ephemeral=True)
    asheet = sheetd.get_account_sheet()
    index = sheetd.index()
    asheet.append_row([
        index, login_type, username, password, shiny, shiny_bg, legendary,
        shiny_legendary, hundo, level50, pokecoins, pokemon_storage, bag_space
    ])
    embed = discord.Embed(title="✅ Account Added", color=discord.Color.og_blurple())
    embed.add_field(name="Login type", value=login_type, inline=True)
    embed.add_field(name="Username", value=username, inline=True)
    embed.add_field(name="Password", value=password, inline=True)
    embed.add_field(name="Shiny", value=shiny, inline=True)
    embed.add_field(name="Legendary", value=legendary, inline=True)
    embed.add_field(name="Shiny Legendary", value=shiny_legendary, inline=True)
    embed.add_field(name="Hundo", value=hundo, inline=True)
    embed.add_field(name="Level 50", value=level50, inline=True)
    embed.add_field(name="Pokecoins", value=pokecoins, inline=True)
    embed.add_field(name="Storage", value=pokemon_storage, inline=True)
    embed.add_field(name="Bag Space", value=bag_space, inline=True)
    embed.set_author(name=str(ctx.author))
    embed.timestamp = datetime.now()
    await ctx.respond(embed=embed)


@bot.slash_command(name="add_device", description="Add a new device to the sheet")
async def add_device(
    ctx: discord.ApplicationContext,
    device_name: str,
    status: bool
):
    await ctx.respond("Adding Device Please Wait  ",ephemeral=True)
    dsheet = sheetd.get_device_sheet()
    did = sheetd.dindx()
    dsheet.append_row([did, device_name, status])
    embed = discord.Embed(title="✅ Device Added", color=discord.Color.brand_green())
    embed.add_field(name="Device ID", value=did, inline=True)
    embed.add_field(name="Device Name", value=device_name, inline=True)
    embed.add_field(name="Free?", value=str(status), inline=True)
    embed.set_author(name=str(ctx.author))
    embed.timestamp = datetime.now()
    await ctx.respond(embed=embed)


@bot.slash_command(name="start_grind", description="Start a grind session")
async def start_grind(
    ctx: discord.ApplicationContext,
    account_id: str,
    device_id: str,
    grind_type: str
):
    await ctx.respond("⏳ Processing...", ephemeral=True)
    device_status = sheetd.dstatus(device_id)
    account_status = sheetd.astatus(account_id)

    if device_status is True:
        if account_status == "FREE":
            sid = sheetd.sess_id()
            ses_sheet = sheetd.get_session_sheet()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ses_sheet.append_row([sid, account_id, device_id, grind_type, now])
            print(f"Session Started{sid} with account ID {account_id}and device is {device_id} Grind type from uSer is {grind_type} and started at {now}")

            sheetd.update_account_sheet(account_id)
            sheetd.update_device_sheet(device_id)

            embed = discord.Embed(title="🔥 Grind Started", color=discord.Color.orange())
            embed.add_field(name="Session ID", value=sid, inline=True)
            embed.add_field(name="Account ID", value=account_id, inline=True)
            embed.add_field(name="Device ID", value=device_id, inline=True)
            embed.add_field(name="Grind Type", value=grind_type.capitalize(), inline=True)
            await ctx.respond(embed=embed)

        elif account_status == "CD" or account_status=="COOLDOWN":
            await ctx.respond("⚠️ Account is under cooldown.")

        elif account_status == "INUSE":
            await ctx.respond("⚠️ Account is currently in use.")

        else:
            await ctx.respond("❌ Unknown account status.")

    else:
        await ctx.respond("❌ Device is currently in use.")


@bot.slash_command(name="stop_grind", description="Stop a grind session")
async def stop_grind(ctx: discord.ApplicationContext, session_id: str):
    await ctx.respond("Stoping Grind Please Wait ",ephemeral=True)
    asheet = sheetd.get_account_sheet()
    dsheet = sheetd.get_device_sheet()
    ses_sheet = sheetd.get_session_sheet()

    session_info = sheetd.get_session_info(ses_sheet, session_id)
    if not session_info:
        await ctx.respond(f"❌ Session ID `{session_id}` not found.")
        return

    account_id = session_info["account_id"]
    device_id = session_info["device_id"]
    grind_type = session_info["grind_type"].lower()

    values_to_update = {}

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        if grind_type == "xp":
            await ctx.respond("Please enter values for: shiny, shiny_bg, hundo (comma separated, e.g. 5,2,1)")
            msg = await bot.wait_for('message', check=check, timeout=120)
            print(f"Received input for XP grind: '{msg.content}'")  # Debug log
            try:
                parts = [x.strip() for x in msg.content.split(",")]
                print(f"Split parts: {parts}")  # Debug log
                if len(parts) != 3:
                    raise ValueError("Incorrect number of values")
                shiny, shiny_bg, hundo = map(int, parts)
                print(f"Parsed values: shiny={shiny}, shiny_bg={shiny_bg}, hundo={hundo}")  # Debug log
                values_to_update = {"shiny": shiny, "shiny_bg": shiny_bg, "hundo": hundo,"bsod":"TRUE"}
            except Exception as e:
                print(f"Error parsing input: {e}")  # Debug log
                await ctx.respond("⚠️ Invalid input format. Please enter exactly three numbers separated by commas, e.g. 5,2,1")
                return
        elif grind_type == "level-50":
            await ctx.respond("Enter `level50`:")
            msg = await bot.wait_for('message', check=check, timeout=120)
            level50 = int(msg.content.strip())
            values_to_update = {"level50": level50}
        elif grind_type== "raid":
            await ctx.respond("Enter  `Legendary`,`Shiny_legendary`,")
            msg= await bot.wait_for('message', check=check, timeout=120)
            print(f"Received input for XP grind: '{msg.content}'")  # Debug log
            try:
                parts = [x.strip() for x in msg.content.split(",")]
                print(f"Split parts: {parts}")  # Debug log
                if len(parts) != 2:
                    raise ValueError("Incorrect number of values")
                legendary, shiny_legendary = map(int, parts)
                print(f"Parsed values: legendary={legendary}, shiny_Legendary={shiny_legendary}")  # Debug log
                values_to_update = {"legendary": legendary, "shiny-legendary": shiny_legendary }
            except Exception as e:
                print(f"Error parsing input: {e}")  # Debug log
                await ctx.respond("⚠️ Invalid input format. Please enter exactly three numbers separated by commas, e.g. 5,2")
                return
        else:
            await ctx.respond(f"Unknown grind type `{grind_type}`.")
            return
    except Exception as e:
        print(f"Input error: {e}")
        await ctx.respond("⚠️ Invalid input format.")
        return

    if not sheetd.update_account_values(asheet, account_id, values_to_update):
        await ctx.respond("❌ Failed to update account stats.")
        return

    if not sheetd.set_account_cooldown(asheet, account_id):
        await ctx.respond("❌ Failed to set cooldown.")
        return

    if not sheetd.update_session_end(ses_sheet, session_id):
        await ctx.respond("❌ Failed to update session end time.")
        return

    if not sheetd.set_device_free(dsheet, device_id):
        await ctx.respond("❌ Failed to mark device as free.")
        return

    embed = discord.Embed(title="🛑 Grind Stopped", color=discord.Color.green())
    embed.add_field(name="Account ID", value=account_id, inline=True)
    embed.add_field(name="Device ID", value=device_id, inline=True)
    embed.add_field(name="Grind Type", value=grind_type.capitalize(), inline=True)
    embed.add_field(name="Cooldown", value="2 hours", inline=True)
    embed.timestamp = datetime.now()
    await ctx.respond(embed=embed)
#--------------------------------------------------------------------------------------#
@bot.slash_command(name="all_accounts", description="Display info for all accounts")
async def all_accounts(ctx: discord.ApplicationContext):
    await ctx.respond("GETTING ALL ACCOUNT INFO PLEASE WAIT ",ephemeral=True)
    data = sheetd.get_account_sheet().get_all_values()
    header = data[0]
    rows = data[1:]

    if not rows:
        await ctx.respond("⚠️ No account data found.")
        return

    await ctx.respond("📋 Sending account info...", ephemeral=True)

    for row in rows:
        embed = discord.Embed(title=f"Account ID: {row[0]}", color=discord.Color.teal())
        for i in range(1, len(row)):
            field_name = header[i]
            field_value = row[i] if row[i] else "N/A"
            embed.add_field(name=field_name, value=field_value, inline=False)
        await ctx.send(embed=embed)
@bot.slash_command(name="account_info", description="Get information about a specific account")
async def account_info(ctx: discord.ApplicationContext, account_id: str):
    await ctx.respond("Wait loading all account status")
    sheet = sheetd.get_account_sheet()
    all_data = sheet.get_all_values()
    headers = all_data[0]
    rows = all_data[1:]

    # Find matching row
    matched_row = None
    for row in rows:
        if row[0] == account_id:
            matched_row = row
            break

    if not matched_row:
        await ctx.respond(f"❌ Account ID `{account_id}` not found.")
        return

    # Create Embed
    embed = discord.Embed(title=f"🔍 Account Info: {account_id}", color=discord.Color.blurple())
    for i in range(1, len(headers)):
        field_name = headers[i]
        field_value = matched_row[i] if i < len(matched_row) else "N/A"
        embed.add_field(name=field_name, value=field_value or "N/A", inline=False)

    await ctx.respond(embed=embed)







print("✅ Starting the bot...")
bot.run(TOKEN)
