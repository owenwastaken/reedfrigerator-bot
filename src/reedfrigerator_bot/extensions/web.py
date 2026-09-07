"""Web server core"""
from __future__ import annotations

__all__ = "routes", "jinja_env"

import asyncio

import aiohttp_cors
import hikari as hk
import arc
from aiohttp import web
from jinja2 import PackageLoader, Environment

plugin = arc.GatewayPlugin(__name__)

jinja_env = Environment(
    loader=PackageLoader("reedfrigerator_bot", "templates/"),
    trim_blocks=True, lstrip_blocks=True, auto_reload=True
)

routes = web.RouteTableDef()


@routes.get("/")
async def index(request: web.Request) -> web.Response:
    template = jinja_env.get_template("iis8.html")
    return web.Response(body=template.render(), content_type="text/html")


@plugin.listen(hk.StartedEvent)
async def start_webserver(_: hk.StartedEvent) -> None:
    """Start webserver"""

    async def on_prepare(_request, response):
        response.headers["Server"] = "Microsoft-IIS/8.0"

    app = web.Application()
    app.add_routes(routes)
    app.on_response_prepare(on_prepare)

    cors = aiohttp_cors.setup(app, defaults={
        "https://reedfrigerator.lacklab.net": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
    })

    for route in app.router.routes():
        cors.add(route)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()

    await asyncio.Event().wait()


@arc.loader()
def loader(client: arc.GatewayClient) -> None:
    client.add_plugin(plugin)


@arc.unloader()
def unloader(client: arc.GatewayClient) -> None:
    client.remove_plugin(plugin)
