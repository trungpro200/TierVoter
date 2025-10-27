import discord
from .PublicPanel import PublicPanel


# TIERS = ["S", "A", "B", "C", "D", "E", "Maid", "No Life"] # for vote view(used later)

class COMPONENT_IDS:
    START_VOTE = 50
    NEXT_VOTE = 51


desc_template = "Use the buttons below to control the registration process.\nCurrent Status: {}\nParticipants: {}"

class ControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.status = "Waiting for participants..."
        self.message: discord.Message = None
        self.embed = ControlEmbed()

class ControlEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="Control Panel", 
                         description=desc_template.format("Waiting for participants...", 0),
                         color=0x0000ff    
                         )
        self.set_footer(text="Powered by Raumanium")
    
    def set_stage_user(self, user: discord.User):
        self.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)
        self.set_footer(text=f"Voting for: {user.name}")
