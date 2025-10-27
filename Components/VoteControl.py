from .Views.ControlPanel import ControlView
from .Views.PublicPanel import PublicPanel, JoinButton, VotePanel
from .TemplateRenderer import TemplateRenderer
import discord
from discord import File
from random import shuffle
from asyncio import create_task, gather


default_tiers = ["Maid", "S", "A", "B", "C", "D", "E"]

class VoteControl:
    channel: dict[int, "VoteControl"] = {} # Dictionary to store active VoteControl instances by channel ID
    def __init__(self, channel: discord.TextChannel, host: discord.User):
        VoteControl.channel[channel.id] = self
        self.publicPanel: PublicPanel = PublicPanel()
        self.controlPanel: ControlView = ControlView()
        
        self.PublicChannel = channel
        self.Host = host
        self.renderer = None # For removing old instances since garbage collection is weird
        self.renderer: TemplateRenderer = TemplateRenderer(show_preview=False, tiers=default_tiers)
        
        #Games Properties
        self.Participants = set([334528593323622402]) # Set to store user IDs of participants
        self.status = "Waiting for participants"
        self.Votes: dict[int, VoteHandler] = {}  # Dictionary to store votes {user_id: VoteHandler}
        self.ParticipantArray = []


    async def start(self):
        """BUTTONS SECTION"""
        # Add a button to start the vote in the control panel
        startVoteButton = discord.ui.Button(label="Start Vote", style=discord.ButtonStyle.success)
        startVoteButton.callback = self.on_start_vote
        self.controlPanel.add_item(startVoteButton)
        # Add a button to check participants in the control panel
        checkParticipantsButton = discord.ui.Button(label="Participants", style=discord.ButtonStyle.secondary)
        checkParticipantsButton.callback = self.on_check_participants
        self.controlPanel.add_item(checkParticipantsButton)
        # Add a join button to the public panel
        self.publicPanel.add_item(JoinButton(callback=self.on_join_button_click))
        
        """MESSAGES SECTION"""
        # Send the control panel to the host via DM
        self.PrivateMessage = await self.Host.send(
            embed=self.controlPanel.embed,
            view=self.controlPanel)
        # Send the public panel to the designated channel
        self.PublicMessage = await self.PublicChannel.send(
            embed=self.publicPanel.embed,
            view=self.publicPanel)
    
    def remove(self):
        del VoteControl.channel[self.PublicChannel.id]
        del self.renderer
        del self
    
    async def update_tierboard(self):
        # Render the tierboard image
        img_buf = self.renderer.render()
        discord_file = File(fp=img_buf, filename="tierboard.png")
        
        # Update the public message with the new tierboard image
        self.publicPanel.embed.title = "Tier List Voting - Current Standings"
        self.publicPanel.embed.description = "The current tier list standings based on votes so far."
        self.publicPanel.embed.color = 0x00ffff  # Change embed color to cyan
        self.publicPanel.embed.set_footer(text="Current Tier List")
        self.publicPanel.embed.set_image(url="attachment://tierboard.png")
        await self.boardMessage.edit(embed=self.publicPanel.embed, attachments=[discord_file])
    
    async def on_join_button_click(self, interaction: discord.Interaction):
        if interaction.user.id in self.Participants:
            self.Participants.remove(interaction.user.id)
            create_task(interaction.response.send_message("You have successfully resigned from the tier list voting!", ephemeral=True))
        else:
            self.Participants.add(interaction.user.id)
            create_task(interaction.response.send_message("You have successfully joined the tier list voting!", ephemeral=True))


        self.controlPanel.embed.description = f"Use the buttons below to control the registration process.\nCurrent Status: {self.status}\nParticipants: {len(self.Participants)}"
        create_task(self.PrivateMessage.edit(embed=self.controlPanel.embed))
        
        self.publicPanel.embed.set_participant_count(len(self.Participants))
        create_task(self.PublicMessage.edit(embed=self.publicPanel.embed))
    
    async def on_check_participants(self, interaction: discord.Interaction):
        if not self.Participants:
            await interaction.response.send_message("No participants have joined yet.", ephemeral=True)
            return
        
        parts = "\n".join([f"- <@{pid}>" for pid in self.Participants])
        await interaction.response.send_message(f"Current participants:\n{parts}", ephemeral=True)
    
    async def on_start_vote(self, interaction: discord.Interaction):
        if len(self.Participants) < 2:
            await interaction.response.send_message("At least two participants are required to start the vote.", ephemeral=True)
            return
        
        self.controlPanel.clear_items()

        nextButton = discord.ui.Button(label="Next Vote", style=discord.ButtonStyle.success)
        nextButton.callback = self.on_next_vote
        self.controlPanel.add_item(nextButton)
        

        self.status = "Voting in progress..."
        self.controlPanel.embed.description = f"Use the buttons below to control the registration process.\nCurrent Status: {self.status}\nParticipants: {len(self.Participants)}"
        
        await self.PrivateMessage.edit(embed=self.controlPanel.embed, view=self.controlPanel)
        
        self.publicPanel.clear_items()
        self.publicPanel.embed.color = 0x0000ff  # Change embed color to blue
        await self.PublicMessage.edit(view=self.publicPanel, embed=self.publicPanel.embed)
        self.publicPanel.stop()
                
        self.ParticipantArray = list(self.Participants)
        shuffle(self.ParticipantArray)  # Randomize voting order
        
        await self.start_vote(interaction)

        create_task(interaction.response.send_message("Voting has started!", ephemeral=True))

    async def on_next_vote(self, interaction: discord.Interaction):
        # print(self.ParticipantArray)
        await interaction.response.defer(ephemeral=True)
        if self.votePanel.stage_user.id not in self.Votes:
            self.Votes[self.votePanel.stage_user.id] = VoteHandler(self.votePanel.stage_user, default_tiers)
        
        #Update tierboard before moving to next vote
        self.renderer.add_item(
                                self.votePanel.stage_user.avatar.url if self.votePanel.stage_user.avatar else self.votePanel.stage_user.default_avatar.url,
                                self.Votes[self.votePanel.stage_user.id].calc_results()
                                )
        create_task(self.update_tierboard())
        
        #Move to next participant
        participant_ID = self.ParticipantArray.pop(0)
        participant = self.PublicMessage.guild.get_member(participant_ID)
        
        self.votePanel.set_stage_user(participant)
        self.votePanel.create_vote_buttons(
            cast_vote=self.cast_vote
        )
        
        self.votePanel.set_footer(text="Voted: 0")
        
        if len(self.ParticipantArray) < 1:
            self.controlPanel.clear_items()
            FinalizeButton = discord.ui.Button(label="End Vote", style=discord.ButtonStyle.danger)
            FinalizeButton.callback = self.on_end_vote
            self.controlPanel.add_item(FinalizeButton)
            create_task(self.PrivateMessage.edit(embed=self.controlPanel.embed, view=self.controlPanel))
            
        edittask = create_task(self.PublicMessage.edit(
            embed=self.votePanel,
            view=self.votePanel
        ))
                
        #Initialize VoteHandler for the next participant
        if participant_ID not in self.Votes:
            self.Votes[participant_ID] = VoteHandler(self.votePanel.stage_user, default_tiers)

        create_task(interaction.followup.send(f"Now voting for {participant.name}.", ephemeral=True))

    async def start_vote(self, interaction: discord.Interaction):
        participant_ID = self.ParticipantArray.pop(0)
        participant = self.PublicMessage.guild.get_member(participant_ID)

        self.votePanel = VotePanel(tiers=default_tiers)
        self.votePanel.set_stage_user(participant)
        self.votePanel.create_vote_buttons(
            cast_vote=self.cast_vote
        )
        self.votePanel.set_footer(text="Voted: 0")
        
        self.boardMessage = self.PublicMessage
        
        self.PublicMessage = await self.PublicChannel.send(
            embed=self.votePanel,
            view=self.votePanel
        )
        
        create_task(self.update_tierboard())
    
    async def on_end_vote(self, interaction: discord.Interaction):
        self.controlPanel.clear_items()
        self.status = "Voting completed."
        self.controlPanel.stop()
        tasks = [self.PrivateMessage.edit(embed=self.controlPanel.embed, view=self.controlPanel),
                 self.PublicMessage.delete(),
                 self.boardMessage.delete()
                 ]
        
        self.publicPanel.embed.title = "Tier List Voting - Final Results"
        self.publicPanel.embed.description = "The final tier list standings based on votes."
        self.publicPanel.embed.color = 0xffd700  # Change embed color to gold
        self.publicPanel.embed.set_footer(text="Final Tier List")
        self.publicPanel.embed.set_image(url="attachment://tierboard.png")
        
        self.renderer.add_item(
                                self.votePanel.stage_user.avatar.url if self.votePanel.stage_user.avatar else self.votePanel.stage_user.default_avatar.url,
                                self.Votes[self.votePanel.stage_user.id].calc_results()
                                )
        
        img = self.renderer.render()
        discord_file = File(fp=img, filename="tierboard.png")

        create_task(self.PublicChannel.send(
            embed=self.publicPanel.embed,
            file=discord_file
        ))

        await gather(*tasks)
        
        self.remove()

    async def cast_vote(self, interaction: discord.Interaction, tier: str):
        if self.votePanel.stage_user.id not in self.Votes:
            self.Votes[self.votePanel.stage_user.id] = VoteHandler(self.votePanel.stage_user, default_tiers)

        self.Votes[self.votePanel.stage_user.id].Tiers[interaction.user.id] = tier
        self.votePanel.set_footer(text=f"Voted: {len(self.Votes[self.votePanel.stage_user.id].Tiers)}")
        create_task(self.PublicMessage.edit(embed=self.votePanel))
    
class VoteHandler:
    def __init__(self, user: discord.User, tiers: list[str] = []):
        self.User = user
        self.Tiers: dict[int, str] = dict()  # Dictionary to store votes {caster_id: tier}
        self.TiersList = tiers  # List of possible tiers
    
    def calc_results(self) -> str:
        scores = []
        
        for tier in self.TiersList:
            count = sum(1 for t in self.Tiers.values() if t == tier)
            scores.append(count)
        
        if max(scores) == 0:
            return self.TiersList[-1]  # No votes cast, default to lowest tier
        
        for i, score in enumerate(scores):
            if score == max(scores):
                return self.TiersList[i]
            else:
                scores[i+1] += score*0.8  # Weighted scoring for tiebreakers
                scores[i] = 0
        
        return self.TiersList[-1]  # Fallback to lowest tier(just in case)