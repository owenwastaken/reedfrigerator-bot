"""Webpage that lets banned people send emoji-only messages in the #ouija channel"""

from __future__ import annotations

from .web import routes, jinja_env

import hikari as hk
import arc
from aiohttp import web
import emoji

from ..ttldict import TTLDict

plugin = arc.GatewayPlugin(__name__)


messages = TTLDict()


@routes.get("/ouija")
async def ouija(_: web.Request) -> web.Response:
    template = jinja_env.get_template("ouija.html.jinja2")
    return web.Response(body=template.render(), content_type="text/html")

@routes.post("/ouija")
async def ouija_post(request: web.Request) -> web.Response:
    message = (await request.post())["message"]

    if len(message) == 0:
        return web.Response(status=400)

    for char in message:
        if not emoji.is_emoji(char):
            return web.Response(status=400)

    if messages.get(message):
        return web.Response(status=429)

    messages.set(message, True, 60)

    await plugin.client.rest.create_message(1211715120812527616, message + "\n-# Talk after you die: [Ouija-Reed](https://reedfrigerator.lacklab.net/ouija)")

    return web.Response(body="Message sent.", content_type="text/html", status=201)


@arc.loader()
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)

@arc.unloader()
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
