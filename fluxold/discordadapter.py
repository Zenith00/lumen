from __future__ import annotations

import typing as ty

if ty.TYPE_CHECKING:
    import discord

import sys
import traceback
import io
import datetime
from fluxold import event
import aenum
import functools


class DiscordEvats(event.EventAttribute):
    DISCORD = aenum.auto()
    CONNECTION = aenum.auto()
    RESUME = aenum.auto()
    ERROR = aenum.auto()
    CLIENT = aenum.auto()

    ADD = aenum.auto()
    REMOVE = aenum.auto()
    RAW = aenum.auto()
    UPDATE = aenum.auto()

    MESSAGE = aenum.auto()

    TYPING = aenum.auto()

    REACTION = aenum.auto()
    CLEAR = aenum.auto()

    CHANNEL = aenum.auto()
    PRIVATE = aenum.auto()
    GUILD = aenum.auto()
    INTEGRATION = aenum.auto()

    WEBHOOK = aenum.auto()

    PIN = aenum.auto()

    KICK = aenum.auto()
    BAN = aenum.auto()

    MEMBER = aenum.auto()
    USER = aenum.auto()

    ROLE = aenum.auto()
    EMOJI = aenum.auto()

    AVAILABLE = aenum.auto()

    RELATIONSHIP = aenum.auto()
    GROUP = aenum.auto()
    VOICE = aenum.auto()


EVAT = DiscordEvats


class DiscordEventAdapter(event.EventAdapter):
    def __init__(self, client: discord.Client, ):
        super(DiscordEventAdapter, self).__init__(source=client)

    # def register_event(self) -> ty.Callable[[ty.Callable], ...]:
    #     def source_wrapper(func):
    #         return self.source.event(func)
    # 
    #     return source_wrapper

    def eventize_deco_factory(self, driver, evats: ty.Tuple[EVAT]):
        def eventize_deco(func: ty.Callable[..., ty.Awaitable[dict]]):
            @functools.wraps(func)
            async def event_wrapper(*args, **kwargs) -> None:
                adapt_result = await func(*args, **kwargs)
                if adapt_result is not None:
                    ev = event.Event(set(evats), kwargs=adapt_result)
                    print(ev)
                    await driver.submit(ev)

            print(f"registering {func.__name__}")
            print(f"{event_wrapper.__name__}")
            return self.source.event(event_wrapper)

        return eventize_deco

    def register(self, driver: event.Driver):
        print("Registering...")

        @self.eventize_deco_factory(driver, evats=[EVAT.CONNECTION, EVAT.ADD])
        async def on_connect():
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.CONNECTION, EVAT.REMOVE])
        async def on_disconnect():
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.RESUME])
        async def on_resumed():
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.ERROR])
        async def on_error(event_method: str, *args, **kwargs):
            traceback_catch = io.StringIO()
            traceback.print_exc(traceback_catch)

            exception_message = 'Ignoring exception in {}'.format(event_method)
            traceback_message = traceback_catch.getvalue()

            print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
            print(traceback_catch.getvalue(), file=sys.stderr, flush=True)

            return {"exception_message": exception_message, "traceback_message": traceback_message, **kwargs}

        @self.eventize_deco_factory(driver, evats=[EVAT.TYPING])
        async def on_typing(channel: discord.abc.Messageable, user: ty.Union[discord.User, discord.Member], when: datetime.datetime):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.MESSAGE, EVAT.ADD])
        async def on_message(message: discord.Message):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.MESSAGE, EVAT.REMOVE])
        async def on_message_delete(message: discord.Message):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.MESSAGE, EVAT.REMOVE, EVAT.RAW])
        async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
            if payload.cached_message:
                return None
            return locals()

        async def on_raw_bulk_message_delete(payload: discord.RawBulkMessageDeleteEvent):
            for message_id, cached_message in zip(payload.message_ids, payload.cached_messages):
                raw_delete = discord.RawMessageDeleteEvent(
                    {"id"        : message_id,
                     "channel_id": payload.channel_id,
                     "guild_id"  : payload.guild_id}
                )
                raw_delete.cached_message = cached_message
                await on_raw_message_delete(raw_delete)

        @self.eventize_deco_factory(driver, evats=[EVAT.MESSAGE, EVAT.UPDATE])
        async def on_message_edit(before: discord.Message, after: discord.Message):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.MESSAGE, EVAT.UPDATE, EVAT.RAW])
        async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.REACTION, EVAT.ADD])
        async def on_reaction_add(reaction: discord.Reaction, user: ty.Union[discord.User, discord.Member]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.REACTION, EVAT.ADD, EVAT.RAW])
        async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):  # todo: aggressive reproduction
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.REACTION, EVAT.REMOVE])
        async def on_reaction_remove(reaction: discord.Reaction, user: ty.Union[discord.User, discord.Member]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.REACTION, EVAT.REMOVE, EVAT.RAW])
        async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.REACTION, EVAT.CLEAR])
        async def on_reaction_clear(message: discord.Message, reaction: ty.List[discord.Reaction]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.MESSAGE, EVAT.CLEAR, EVAT.RAW])
        async def on_raw_reaction_clear(payload: discord.RawReactionClearEvent):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.PRIVATE, EVAT.CHANNEL, EVAT.REMOVE])
        async def on_private_channel_delete(channel: discord.abc.PrivateChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.PRIVATE, EVAT.CHANNEL, EVAT.ADD])
        async def on_private_channel_create(channel: discord.abc.PrivateChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.PRIVATE, EVAT.CHANNEL, EVAT.UPDATE])
        async def on_private_channel_update(before: discord.GroupChannel, after: discord.GroupChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.PRIVATE, EVAT.CHANNEL, EVAT.PIN, EVAT.REMOVE])
        async def on_private_channel_pins_update(channel: discord.abc.PrivateChannel, last_pin: ty.Optional[datetime.datetime]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.CHANNEL, EVAT.REMOVE])
        async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.CHANNEL, EVAT.ADD])
        async def on_guild_channel_create(channel: discord.abc.GuildChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.CHANNEL, EVAT.UPDATE])
        async def on_guild_channel_update(before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.CHANNEL, EVAT.PIN, EVAT.UPDATE])
        async def on_guild_channel_pins_update(channel: discord.abc.GuildChannel, last_pin: ty.Optional[datetime.datetime]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.INTEGRATION, EVAT.REMOVE])
        async def on_guild_integrations_update(guild: discord.Guild):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.WEBHOOK, EVAT.UPDATE])
        async def on_webhooks_update(channel: discord.abc.GuildChannel):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.MEMBER, EVAT.ADD])
        async def on_member_join(member: discord.Member):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.MEMBER, EVAT.REMOVE])
        async def on_member_remove(member: discord.Member):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.MEMBER, EVAT.UPDATE])
        async def on_member_update(before: discord.Member, after: discord.Member):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.USER, EVAT.UPDATE])
        async def on_user_update(before: discord.User, after: discord.User):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.CLIENT, EVAT.GUILD, EVAT.ADD])
        async def on_guild_join(guild: discord.Guild):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.CLIENT, EVAT.GUILD, EVAT.REMOVE])
        async def on_guild_remove(guild: discord.Guild):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.UPDATE])
        async def on_guild_update(before: discord.Guild, after: discord.Guild):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.ROLE, EVAT.ADD])
        async def on_guild_role_create(role: discord.Role):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.ROLE, EVAT.REMOVE])
        async def on_guild_role_delete(role: discord.Role):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.ROLE, EVAT.UPDATE])
        async def on_guild_role_update(before: discord.Role, after: discord.Role):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.EMOJI, EVAT.UPDATE])
        async def on_guild_emojis_update(guild: discord.Guild, before: ty.List[discord.Emoji], after: ty.List[discord.Emoji]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.AVAILABLE, EVAT.ADD])
        async def on_guild_available(guild: discord.Guild):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.AVAILABLE, EVAT.REMOVE])
        async def on_guild_unavailable(guild: discord.Guild):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.VOICE, EVAT.UPDATE])
        async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.BAN, EVAT.ADD])
        async def on_member_ban(guild: discord.Guild, user: ty.Union[discord.User, discord.Member]):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GUILD, EVAT.BAN, EVAT.REMOVE])
        async def on_member_unban(guild: discord.Guild, user: discord.User):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GROUP, EVAT.ADD])
        async def on_group_join(channel: discord.GroupChannel, user: discord.User):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.GROUP, EVAT.REMOVE])
        async def on_group_remove(channel: discord.GroupChannel, user: discord.User):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.RELATIONSHIP, EVAT.ADD])
        async def on_relationship_add(relationship: discord.Relationship):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.RELATIONSHIP, EVAT.REMOVE])
        async def on_relationship_remove(relationship: discord.Relationship):
            return locals()

        @self.eventize_deco_factory(driver, evats=[EVAT.RELATIONSHIP, EVAT.UPDATE])
        async def on_relationship_update(before: discord.Relationship, after: discord.Relationship):
            return locals()
