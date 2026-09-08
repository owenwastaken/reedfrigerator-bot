"""TODO"""

from __future__ import annotations

import asyncio
from os import environ, name
from pathlib import Path
from random import SystemRandom

import arc
import hikari as hk


token = environ["TOKEN"]

bot = hk.GatewayBot(
    token=token,
    # Disable intents - this bot doesn't need any
    intents=hk.Intents.NONE,
    # Disable cache - Not needed and just takes up more ram
    cache_settings=hk.impl.CacheSettings(components=hk.api.CacheComponents.NONE),
)

client = arc.GatewayClient(
    bot, integration_types=[hk.ApplicationIntegrationType.GUILD_INSTALL]
)

# Create cryptographically secure random number generator, backed by /dev/random
client.set_type_dependency(SystemRandom, SystemRandom())

client.load_extensions_from(
    Path(__file__).parent.joinpath("extensions"), recursive=True
)

if __name__ == "__main__":
    if name != "nt":
        from uvloop import new_event_loop

        loop = new_event_loop()
        asyncio.set_event_loop(loop)

    bot.run()
