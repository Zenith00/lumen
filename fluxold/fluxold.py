import discord
from fluxold import discordadapter, event as ev
from fluxold.discordadapter import DiscordEvats
import typing as ty

class BotEvats(DiscordEvats):
    pass

EVAT = BotEvats

class Flux(discord.Client):

    def __init__(self, *args, **kwargs):
        super(Flux, self).__init__(*args, **kwargs)
        self.driver = ev.Driver()


    def command_refinery(self, ev: ev.Event) -> ty.Tuple[ev.Event]:
        pass

    async def on_ready(self):
        print("ready!")
        self.driver.register_adapter(discordadapter.DiscordEventAdapter(client=self))






f = Flux()


class FluxCommand:
    pass
