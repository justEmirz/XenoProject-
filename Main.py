import discord
from discord.ext import commands, tasks
import random, string, datetime, asyncio

# === CONFIG ===
TOKEN = "MTM5MzgwODQ4MjIwMDg1MDUzNQ.GgIvSE.rrmF8A2ONtv_N68g1qnIwSreV_2E-2-LmGZ24w"
ADMIN_ROLE = "Admin"

EXPIRY_TIMES = {
    "free": 1,         # 1 day
    "trial3d": 3,
    "trial30d": 30,
    "permanent": None
}

keys = {}

XENOLITE_TEMPLATE = "xenolite_template.lua"  # your template file
XENOLITE_OUTPUT = "xenolite_generated.lua"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === UTILITY FUNCTIONS ===
def generate_key(key_type):
    rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    key = f"XENO-{key_type.upper()}-{rand}"
    expiry = datetime.datetime.utcnow() + datetime.timedelta(days=EXPIRY_TIMES[key_type]) if EXPIRY_TIMES[key_type] else None
    keys[key] = {"type": key_type, "expiry": expiry, "used": False}
    return key

def is_admin(ctx):
    return any(role.name == ADMIN_ROLE for role in ctx.author.roles)

# === COMMANDS ===
@bot.command()
async def genkey(ctx, key_type: str):
    if not is_admin(ctx):
        return await ctx.send("❌ You don't have permission.")
    if key_type not in EXPIRY_TIMES:
        return await ctx.send("❌ Invalid type. Use: free, trial3d, trial30d, permanent")
    key = generate_key(key_type)
    await ctx.author.send(f"✅ Generated key: **{key}** (Type: {key_type})")
    await ctx.send("🔑 Key sent to your DM!")

@bot.command()
async def listkeys(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        return await ctx.send("⚠️ This command only works in DM.")
    if not is_admin(ctx):
        return await ctx.send("❌ You don't have permission.")
    if not keys:
        return await ctx.send("No keys generated yet.")
    msg = "📋 **Generated Keys:**\n"
    for k,v in keys.items():
        status = "✅ Valid"
        if v["used"]:
            status = "❌ Used"
        elif v["expiry"] and datetime.datetime.utcnow() > v["expiry"]:
            status = "⌛ Expired"
        elif v["expiry"]:
            status = f"⏳ Expires: {v['expiry']}"
        else:
            status = "♾ Permanent"
        msg += f"🔑 {k} | Type: {v['type']} | {status}\n"
    await ctx.send(msg)

@bot.command()
async def redeem(ctx, key: str):
    if key not in keys:
        return await ctx.send("❌ Invalid key.")
    v = keys[key]
    if v["used"]:
        return await ctx.send("❌ This key has already been redeemed.")
    if v["expiry"] and datetime.datetime.utcnow() > v["expiry"]:
        return await ctx.send("⌛ This key has expired.")
    v["used"] = True
    await ctx.send(f"🎉 Success! You redeemed key: **{key}** (Type: {v['type']})")

@bot.command()
async def revoke(ctx, key: str):
    if not is_admin(ctx):
        return await ctx.send("❌ You don't have permission.")
    if key in keys:
        del keys[key]
        await ctx.send(f"✅ Key {key} revoked.")
    else:
        await ctx.send("❌ Key not found.")

# === AUTOMATIC FREE KEY GENERATION & SCRIPT UPDATE ===
@tasks.loop(hours=24)
async def daily_free_key_script():
    await bot.wait_until_ready()
    # Generate Free key
    key = generate_key("free")
    print(f"[INFO] Generated daily Free key: {key}")
    
    # Update XenoLite script
    with open(XENOLITE_TEMPLATE, "r") as f:
        content = f.read()
    content = content.replace("{FREE_KEY}", key)
    with open(XENOLITE_OUTPUT, "w") as f:
        f.write(content)
    
    # DM Free users (role not required)
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                try:
                    with open(XENOLITE_OUTPUT, "r") as f:
                        script_content = f.read()
                    await member.send(f"🎁 Your daily Free XenoLite script:\n```lua\n{script_content}\n```")
                except Exception as e:
                    print(f"[ERROR] Could not DM {member}: {e}")

daily_free_key_script.start()

# === RUN BOT ===
bot.run(TOKEN)
