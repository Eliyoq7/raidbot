import os
import nextcord
from nextcord.ext import commands
import asyncio

# Load token from Railway environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

# Safety settings
MAX_MESSAGES = 50000000000000000000000000000000
SAFE_DELAY = 0.0000001  # ~5 msgs/sec safe

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)


# --- Modal Class ---
class SpamModal(nextcord.ui.Modal):
    def __init__(self, channel: nextcord.TextChannel):
        super().__init__("Spam Command")

        self.channel = channel
        self.msg_input = nextcord.ui.TextInput(
            label="Message",
            placeholder="Enter the message to spam",
            required=True,
            max_length=200
        )
        self.amount_input = nextcord.ui.TextInput(
            label="Amount (max 50)",
            placeholder="Enter number of times",
            required=True
        )

        self.add_item(self.msg_input)
        self.add_item(self.amount_input)

    async def callback(self, interaction: nextcord.Interaction):
        try:
            amount = int(self.amount_input.value)
        except ValueError:
            await interaction.response.send_message("⚠️ Amount must be a number.", ephemeral=True)
            return

        if amount > MAX_MESSAGES:
            await interaction.response.send_message(
                f"⚠️ Max allowed is {MAX_MESSAGES} messages.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"🚀 Spamming `{self.msg_input.value}` {amount}x in {self.channel.mention}",
            ephemeral=True
        )

        for _ in range(amount):
            await self.channel.send(self.msg_input.value)
            await asyncio.sleep(SAFE_DELAY)

        await interaction.followup.send("✅ Done!", ephemeral=True)


# --- Global Slash Command ---
@bot.slash_command(description="Open spam modal (global)")
async def spam(interaction: nextcord.Interaction, channel: nextcord.TextChannel = None):
    """Opens a modal to spam messages in a channel."""
    target_channel = channel or interaction.channel
    modal = SpamModal(target_channel)
    await interaction.response.send_modal(modal)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


bot.run(TOKEN)
