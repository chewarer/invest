#!/usr/bin/env python

import click
import asyncio
from functools import wraps


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@click.group(name='stocks')
def group_stocks():
    """Stocks commands"""


@click.group(name='idea')
def group_ideas():
    """Ideas commands"""


@click.group()
def entire_groups():
    """Command line interface"""


entire_groups.add_command(group_stocks)
entire_groups.add_command(group_ideas)


@group_stocks.command()
@coro
@click.option('-d', '--date', default='2020-12-31', type=str, help='Date for parse')
async def get_stocks(date):
    """Get stock quotes from Moscow Exchange ISS server"""
    from backend.tasks.iss_stock_quotes import get_for_date
    await get_for_date(date)


@group_stocks.command()
@coro
@click.option('-f', '--date_from', default='2020-12-31', type=str, help='Start date')
@click.option('-t', '--date_to', default='2020-12-31', type=str, help='End date')
async def get_stocks_between(date_from, date_to):
    """Get stock quotes from Moscow Exchange ISS server between dates"""
    from backend.tasks.iss_stock_quotes import get_shares_between
    await get_shares_between(date_from=date_from, date_to=date_to)


@group_ideas.command()
@coro
@click.option('-l', '--limit', default=20, type=int, help='Limit for parse')
async def tinkoff(limit):
    """Get ideas from Tinkoff"""
    from backend.scrappers.tinkoff import parse_ideas
    await parse_ideas(limit)


@group_ideas.command()
@coro
@click.option('-l', '--limit', default=20, type=int, help='Limit for parse')
@click.option('-o', '--offset', default=0, type=int, help='Offset for parse')
async def bks(limit, offset):
    """Get ideas from BKS"""
    from backend.scrappers.bks import parse_ideas
    await parse_ideas(limit, offset)


if __name__ == '__main__':
    entire_groups()
