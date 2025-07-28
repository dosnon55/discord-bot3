# et.py (أو اسم ملف البوت الأساسي)
import os
from keep_alive import keep_alive  # استيراد keep_alive

import discord
from discord.ext import commands
from discord import app_commands
import json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

config_file = "config.json"

if not os.path.exists(config_file):
    with open(config_file, "w") as f:
        json.dump({}, f)

def load_config():
    with open(config_file, "r") as f:
        return json.load(f)

def save_config(data):
    with open(config_file, "w") as f:
        json.dump(data, f, indent=4)

class OperationsModal(discord.ui.Modal, title="تقرير مركز العمليات"):
    time = discord.ui.TextInput(label="الوقت", placeholder="مثال: 9:30 مساءً")
    fort = discord.ui.TextInput(label="الحصن", placeholder="اسم الموقع")
    units = discord.ui.TextInput(label="الوحدات", style=discord.TextStyle.paragraph, placeholder="اكتب الوحدات تحت بعض")
    reports_count = discord.ui.TextInput(label="عدد البلاغات", placeholder="مثال: 3 بلاغات")

    async def on_submit(self, interaction: discord.Interaction):
        config = load_config()
        guild_id = str(interaction.guild.id)
        room_id = config.get(guild_id, {}).get("operations_room")

        if not room_id:
            await interaction.response.send_message("⚠️ لم يتم تحديد روم العمليات بعد.", ephemeral=True)
            return

        embed = discord.Embed(title="📋 تقرير مركز العمليات", color=0x3498db)
        embed.add_field(name="🕓 الوقت", value=self.time.value, inline=False)
        embed.add_field(name="🏰 الحصن", value=self.fort.value, inline=False)
        embed.add_field(name="🚓 الوحدات", value=self.units.value, inline=False)
        embed.add_field(name="📊 عدد البلاغات", value=self.reports_count.value, inline=False)
        embed.set_footer(text=f"تم الإرسال بواسطة: {interaction.user.display_name}")

        channel = bot.get_channel(int(room_id))
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال تقرير العمليات بنجاح.", ephemeral=True)

class EMSModalShort(discord.ui.Modal, title="تقرير الإسعاف - مختصر"):
    name = discord.ui.TextInput(label="اسم الحالة")
    national_id = discord.ui.TextInput(label="الهوية الوطنية")
    location = discord.ui.TextInput(label="الموقع")
    case_type = discord.ui.TextInput(label="نوع الحالة")
    description = discord.ui.TextInput(label="وصف الحالة", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        config = load_config()
        guild_id = str(interaction.guild.id)
        room_id = config.get(guild_id, {}).get("ems_room")

        if not room_id:
            await interaction.response.send_message("⚠️ لم يتم تحديد روم الإسعاف بعد.", ephemeral=True)
            return

        embed = discord.Embed(title="🚑 تقرير الإسعاف", color=0x2ecc71)
        embed.add_field(name="👤 اسم الحالة", value=self.name.value, inline=False)
        embed.add_field(name="🆔 الهوية الوطنية", value=self.national_id.value, inline=False)
        embed.add_field(name="📍 الموقع", value=self.location.value, inline=False)
        embed.add_field(name="🩺 نوع الحالة", value=self.case_type.value, inline=False)
        embed.add_field(name="📝 وصف الحالة", value=self.description.value, inline=False)
        embed.set_footer(text=f"تم الإرسال بواسطة: {interaction.user.display_name}")

        channel = bot.get_channel(int(room_id))
        await channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال تقرير الإسعاف بنجاح.", ephemeral=True)

class ReportButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 تقرير العمليات", style=discord.ButtonStyle.primary, custom_id="report_operations")
    async def operations_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(OperationsModal())

    @discord.ui.button(label="🚑 تقرير الإسعاف", style=discord.ButtonStyle.success, custom_id="report_ems")
    async def ems_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EMSModalShort())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم تشغيل البوت. الأوامر المتزامنة: {len(synced)}")
    except Exception as e:
        print(f"❌ خطأ في التزامن: {e}")
    bot.add_view(ReportButtons())

@bot.tree.command(name="تقرير", description="إرسال أزرار التقارير")
async def send_buttons(interaction: discord.Interaction):
    await interaction.response.send_message("اختر نوع التقرير:", view=ReportButtons())

@bot.tree.command(name="تحديد_روم_العمليات", description="حدد روم تقارير مركز العمليات")
@app_commands.describe(room="الروم الذي تُرسل إليه تقارير العمليات")
async def set_operations_room(interaction: discord.Interaction, room: discord.TextChannel):
    config = load_config()
    guild_id = str(interaction.guild.id)
    config.setdefault(guild_id, {})["operations_room"] = str(room.id)
    save_config(config)
    await interaction.response.send_message(f"✅ تم حفظ روم تقارير العمليات: {room.mention}", ephemeral=True)

@bot.tree.command(name="تحديد_روم_الإسعاف", description="حدد روم تقارير الإسعاف")
@app_commands.describe(room="الروم الذي تُرسل إليه تقارير الإسعاف")
async def set_ems_room(interaction: discord.Interaction, room: discord.TextChannel):
    config = load_config()
    guild_id = str(interaction.guild.id)
    config.setdefault(guild_id, {})["ems_room"] = str(room.id)
    save_config(config)
    await interaction.response.send_message(f"✅ تم حفظ روم تقارير الإسعاف: {room.mention}", ephemeral=True)

# تشغيل keep_alive لخادم Flask
keep_alive()

# تشغيل البوت باستخدام متغير البيئة TOKEN
bot.run(os.getenv("TOKEN"))
