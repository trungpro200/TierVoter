import discord
from typing import Callable
from asyncio import create_task

class PublicPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        self.embed = RegisterEmbed()
        self.message: discord.Message = None
        
class JoinButton(discord.ui.Button):
    def __init__(self, callback: Callable[[discord.Interaction], None] = None):
        super().__init__(label="Join", style=discord.ButtonStyle.primary, id=36)
        self.Participants = set()  # Set to store user IDs of participants
        self.callback = callback

class RegisterEmbed(discord.Embed):
    def __init__(self):
        super().__init__(title="Tier List Voting Registration", 
                         description="Click the button below to participate in the tierlist!\nTotal Participants: 0", 
                         color=0x00ff00
                         )
        self.set_footer(text="Powered by Raumanium")
    
    def set_participant_count(self, count: int):
        self.description = f"Click the button below to participate in the tierlist!\nTotal Participants: {count}"

class VotePanel(discord.ui.View, discord.Embed):
    def __init__(self, tiers: list[str] = ["S", "A", "B", "C", "D", "E", "Maid", "No Life"]):
        discord.ui.View.__init__(self, timeout=None)
        discord.Embed.__init__(self, title="Tier List Voting", 
                               description="The voting has begun! Stay tuned for results.", 
                               color=0x0000ff
                               )
        self.set_footer(text="Voted: 0")
        self.stage_user: discord.User = None
        self.TIERS = tiers
    
    def set_stage_user(self, user: discord.User):
        self.title = f"Voting for {user.name}'s tier"
        self.stage_user = user
        
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        if hasattr(self, 'avatar_excepts') and user.id in self.avatar_excepts:
            avatar_url = self.avatar_excepts[user.id]

        self.set_image(url=avatar_url)

    def create_vote_buttons(self, cast_vote: Callable[[discord.Interaction, int, str], None] = None):
        self.clear_items()
        for i, tier in enumerate(self.TIERS):
            if self.stage_user.id == 1126495387683926036 and tier != 'Maid': # This one is a maid
                continue
            vote_button = VoteButton(label=tier, stage_user=self.stage_user, cast_vote=cast_vote, id=100 + i)
            self.add_item(vote_button)
    
    def add_avatar_exception(self, excepts: dict[int, str]):
        self.avatar_excepts = excepts

class VoteButton(discord.ui.Button):
    def __init__(self, label: str, stage_user: discord.User, cast_vote: Callable[[discord.Interaction, int, str], None] = None, id: int = None):
        super().__init__(label=label, style=discord.ButtonStyle.primary, id=id)
        self.cast_vote = cast_vote
        self.stage_user = stage_user
        self.view: VotePanel

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if self.view.stage_user.id == interaction.user.id:
            create_task(interaction.followup.send("You cannot vote for yourself!", ephemeral=True))
            return
        
        if self.cast_vote:
            create_task(self.cast_vote(interaction, self.label))
            return

