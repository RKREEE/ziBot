import asyncio
import datetime
import discord
import json
import os
import praw
import re

from cogs.errors.fun import DiceTooBig
from discord.ext import commands
from discord.errors import Forbidden
from dotenv import load_dotenv
from random import choice, randint
from typing import Optional

try:
    REDDIT_CLIENT_ID = os.environ["REDDIT_CLIENT_ID"]
except:
    load_dotenv()
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")

try:
    REDDIT_CLIENT_SECRET = os.environ["REDDIT_CLIENT_SECRET"]
except:
    load_dotenv()
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")

try:
    REDDIT_USER_AGENT = os.environ["REDDIT_USER_AGENT"]
except:
    load_dotenv()
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
)


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_redarmy(ctx):
        return ctx.guild.id == 747984453585993808

    @commands.command()
    @commands.cooldown(1, 5)
    async def flip(self, ctx):
        """Flip a coin."""
        coin_side = ["heads", "tails"]
        await ctx.send(f"{ctx.message.author.mention} {coin_side[randint(0, 1)]}")

    @flip.error
    async def flip_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            bot_msg = await ctx.send(f"{ctx.message.author.mention}, slowdown bud!")
            await asyncio.sleep(round(error.retry_after))
            await bot_msg.delete()

    @commands.command(usage="[dice size] [number of dice]", brief="Roll the dice.")
    @commands.cooldown(1, 5)
    async def roll(self, ctx, arg1: Optional[str] = 1, arg2: Optional[int] = None):
        """Roll the dice.\n\
           **Example**\n\
           ``>roll 2``\n``>roll d12 4``"""
        dice = []
        if arg1.startswith("d"):
            dice_size = int(arg1.split("d")[1])
            dice_number = arg2
            if not dice_number:
                dice_number = 1
        else:
            dice_size = 6
            dice_number = int(arg1)
        if dice_number > 100:
            raise DiceTooBig
        for i in range(dice_number):
            dice.append(int(randint(1, dice_size)))
        dice = ", ".join(str(i) for i in dice)
        await ctx.send(f"{ctx.message.author.mention} just rolled {dice}!")

    @roll.error
    async def roll_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            bot_msg = await ctx.send(
                f"{ctx.message.author.mention}," + " slowdown bud!"
            )
            await asyncio.sleep(round(error.retry_after))
            await bot_msg.delete()
        if isinstance(error, DiceTooBig):
            await ctx.send("You can only roll up to 100 dices!")

    @commands.command(aliases=["r", "sroll"], usage="(number of roll)")
    @commands.cooldown(1, 5)
    async def steveroll(self, ctx, pool):
        """Roll the dice in steve's style."""
        ignore_cooldown = [745481731133669476, 747984453585993808]
        if ctx.guild.id in ignore_cooldown:
            ctx.command.reset_cooldown(ctx)
        await ctx.send(
            f"{ctx.message.author.mention} just rolled {randint(0, int(pool))}"
        )

    @steveroll.error
    async def steveroll_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            bot_msg = await ctx.send(
                f"{ctx.message.author.mention}," + " slowdown bud!"
            )
            await asyncio.sleep(round(error.retry_after))
            await bot_msg.delete()

    @commands.command()
    async def meme(self, ctx):
        """Get memes from subreddit r/memes."""
        try:
            meme_channel = self.bot.get_channel(
                int(self.bot.config[str(ctx.message.guild.id)]["meme_ch"])
            )
        except KeyError:
            meme_channel = ctx

        meme_subreddits = ["memes", "funny"]
        reg_img = r".*/(i)\.redd\.it"

        if ctx.channel is not meme_channel and meme_channel is not ctx:
            async with ctx.typing():
                await ctx.send(f"Please do this command on {meme_channel.mention}")
                return
        async with meme_channel.typing():
            selected_subreddit = meme_subreddits[randint(0, len(meme_subreddits) - 1)]
            memes_submissions = reddit.subreddit(selected_subreddit).hot()
            post_to_pick = randint(1, 50)
            for i in range(0, post_to_pick):
                submission = next(x for x in memes_submissions if not x.stickied)
            if submission.over_18:
                return
            embed = discord.Embed(
                title=f"r/{selected_subreddit} " + f"- {submission.title}",
                colour=discord.Colour(0xFF4500),
            )
            embed.set_author(
                name="Reddit",
                icon_url="https://www.redditstatic.com/desktop2x/"
                + "img/favicon/android-icon-192x192.png",
            )
            match = re.search(reg_img, submission.url)
            embed.add_field(name="Upvotes", value=submission.score)
            embed.add_field(name="Comments", value=submission.num_comments)
            if match:
                embed.set_image(url=submission.url)
            else:
                await meme_channel.send(embed=embed)
                await meme_channel.send(submission.url)
                return
            await meme_channel.send(embed=embed)

    @commands.command(usage="(choice)", brief="Rock Paper Scissors with the bot.")
    @commands.cooldown(1, 5)
    async def rps(self, ctx, choice):
        """Rock Paper Scissors with the bot.\n\
           **Example**
           ``>rps rock``"""
        rps = ["rock", "paper", "scissors"]
        bot_choice = rps[randint(0, len(rps) - 1)]

        await ctx.send(
            f"You chose ***{choice.capitalize()}***."
            + f" I chose ***{bot_choice.capitalize()}***."
        )
        if bot_choice == choice:
            await ctx.send("It's a Tie!")
        elif bot_choice == rps[0]:

            def f(x):
                return {"paper": "Paper wins!", "scissors": "Rock wins!"}.get(
                    x, "Rock wins!"
                )

            result = f(choice)
        elif bot_choice == rps[1]:

            def f(x):
                return {"rock": "Paper wins!", "scissors": "Scissors wins!"}.get(
                    x, "Paper wins!"
                )

            result = f(choice)
        elif bot_choice == rps[2]:

            def f(x):
                return {"paper": "Scissors wins!", "rock": "Rock wins!"}.get(
                    x, "Scissors wins!"
                )

            result = f(choice)
        else:
            return
        if choice == "noob":
            result = "Noob wins!"
        await ctx.send(result)

    @commands.command(usage="[amount of ping]")
    async def pingme(self, ctx, amount: int = 1):
        """Ping yourself for no reason"""
        try:
            channel = self.bot.get_channel(
                int(self.bot.config[str(ctx.message.guild.id)]["pingme_ch"])
            )
        except KeyError:
            await ctx.send("This server doesn't have channel with type `pingme`")
            return
        msg = await ctx.send("Pinging...")
        for i in range(amount):
            await asyncio.sleep(3)
            if channel:
                try:
                    await channel.send(ctx.author.mention)
                except Forbidden:
                    await ctx.send(
                        "ziBot doesn't have permission to send message inside pingme channel!"
                    )
                    break
            else:
                await ctx.send("Channel with type `pingme` can't be found!")
                break
        await msg.delete()

    @commands.cooldown(1, 25, commands.BucketType.guild)
    @commands.command()
    async def findseed(self, ctx):
        """Test your luck in Minecraft."""
        ignore_cooldown = [745481731133669476, 747984453585993808]
        if ctx.guild.id in ignore_cooldown:
            ctx.command.reset_cooldown(ctx)

        rigged = {186713080841895936: 9000}

        if ctx.author.id in rigged:
            totalEyes = rigged[ctx.author.id]
        else:
            totalEyes = 0
            for i in range(12):
                randomness = randint(1, 10)
                if randomness <= 1:
                    totalEyes += 1
        await ctx.send(
            f"{ctx.message.author.mention} -> your seed is a {totalEyes} eye"
        )

    @findseed.error
    async def findseed_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            bot_msg = await ctx.send(f"{ctx.message.author.mention}, slowdown bud!")
            await asyncio.sleep(round(error.retry_after))
            await bot_msg.delete()

    @commands.cooldown(1, 25, commands.BucketType.guild)
    @commands.command(aliases=["vfindseed", "visualfindseed", "vfs"])
    async def findseedbutvisual(self, ctx):
        """Test your luck in Minecraft but visual."""
        ignore_cooldown = [745481731133669476, 747984453585993808]
        if ctx.guild.id in ignore_cooldown:
            ctx.command.reset_cooldown(ctx)

        rows = {
            0: [0, 0, 0],
            1: [0, 0, 0],
            2: [0, 0, 0],
            3: [0, 0, 0],
        }
        emojis = [
            "<:empty:754550188269633556>",
            "<:portal:754550231017979995>",
            "<:eye:754550267382333441>",
        ]
        portalframe = ""
        for r in range(4):
            for e in range(3):
                randomness = randint(1, 10)
                if randomness <= 1:
                    rows[r][e] = 1
        for i in range(4):
            if i == 0 or i == 3:
                portalframe += f" \{rows[i][0]}\{rows[i][1]}\{rows[i][2]}\n"
            else:
                if i == 2:
                    pass
                else:
                    for e in range(3):
                        portalframe += f"\{rows[i][e]}   \{rows[i+1][e]}\n"
        portalframe = portalframe.replace(" ", emojis[0])
        portalframe = portalframe.replace(r"\0", emojis[1])
        portalframe = portalframe.replace(r"\1", emojis[2])
        # print(portalframe)
        e = discord.Embed(
            title="findseed but visual",
            description=f"Your seed looks like: \n\n{portalframe}",
            color=discord.Colour(0x38665E),
        )
        e.set_author(
            name=f"{ctx.message.author.name}#{ctx.message.author.discriminator}",
            icon_url=ctx.message.author.avatar_url,
        )
        await ctx.send(embed=e)
        # await ctx.send(
        #     f"{ctx.message.author.mention} -> your seed is a {totalEyes} eye"
        # )

    @findseedbutvisual.error
    async def findseedbutvisual_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            bot_msg = await ctx.send(f"{ctx.message.author.mention}, slowdown bud!")
            await asyncio.sleep(round(error.retry_after))
            await bot_msg.delete()

    @commands.cooldown(1, 25, commands.BucketType.guild)
    @commands.command()
    async def findsleep(self, ctx):
        """See how long you sleep."""
        ignore_cooldown = [745481731133669476, 747984453585993808]
        if ctx.guild.id in ignore_cooldown:
            ctx.command.reset_cooldown(ctx)

        lessSleepMsg = [
            "gn, insomniac!",
            "counting sheep didn't work? try counting chloroform vials!",
            "try a glass of water",
            "some decaf coffee might do the trick!",
        ]

        moreSleepMsg = [
            "waaakeee uuuppp!",
            "are they dead or asleep? I can't tell.",
            "wake up, muffin head",
            "psst... coffeeee \\:D",
        ]

        sleepHrs = randint(0, 24)

        if sleepHrs == 0:
            await ctx.send(
                f"{ctx.author.mention} -> your sleep is 0 hours long - nice try \:D"
            )
        elif sleepHrs <= 5:
            if sleepHrs == 1:
                s = ""
            else:
                s = "s"
            await ctx.send(
                f"{ctx.author.mention} -> your sleep is {sleepHrs} hour{s} long - {lessSleepMsg[randint(0, len(lessSleepMsg) - 1)]}"
            )
        else:
            await ctx.send(
                f"{ctx.author.mention} -> your sleep is {sleepHrs} hours long - {moreSleepMsg[randint(0, len(moreSleepMsg) - 1)]}"
            )

    @findsleep.error
    async def findsleep_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            bot_msg = await ctx.send(f"{ctx.message.author.mention}, slowdown bud!")
            await asyncio.sleep(round(error.retry_after))
            await bot_msg.delete()

    @commands.command()
    @commands.check(is_redarmy)
    async def someone(self, ctx):
        """Summon random member."""
        await ctx.send(choice(ctx.guild.members).mention)

    @commands.command(aliases=["badjokes"])
    async def dadjokes(self, ctx):
        headers = {"accept": "application/json"}
        async with self.bot.session.get(
            "https://icanhazdadjoke.com/", headers=headers
        ) as req:
            dadjoke = json.loads(await req.text())["joke"]
        e = discord.Embed(title=dadjoke, color=discord.Colour(0xFEDE58))
        e.set_author(
            name="icanhazdadjoke",
            icon_url="https://raw.githubusercontent.com/null2264/null2264/master/epicface.png",
        )
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Fun(bot))
