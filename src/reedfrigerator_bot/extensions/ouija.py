"""Webpage that lets banned people send emoji-only messages in the #ouija channel"""

from __future__ import annotations

from os import environ

import arc
import emoji
from aiohttp import web

from ..ttldict import TTLDict
from .web import jinja_env, routes

plugin = arc.GatewayPlugin(__name__)


channel = environ["OUIJA_CHANNEL"]

messages = TTLDict()


@routes.get("/ouija")
async def ouija(_: web.Request) -> web.Response:
    template = jinja_env.get_template("ouija.html.jinja2")
    return web.Response(body=template.render(), content_type="text/html")


@routes.post("/ouija")
async def ouija_post(request: web.Request) -> web.Response:
    message = (await request.post())["message"]

    if len(message) == 0 or len(message) > 50:
        return web.Response(status=400, body="Invalid size")

    if not emoji.purely_emoji(message):
        return web.Response(status=400, body="Message must only contain emoji.")

    if messages.get(message):
        return web.Response(status=429, body="Message is ratelimited. Try sending something else")

    messages.set(message, True, 60*5)

    await plugin.client.rest.create_message(
        channel,
        message
        + "\n-# Talk after you die: [Emojia](https://reedfrigerator.lacklab.net/ouija)",
    )

    return web.Response(body="Message sent.", content_type="text/html", status=201)


@arc.loader()
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader()
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
