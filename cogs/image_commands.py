from discord.ext import commands
import discord
import function_helper
import random
import PIL
from PIL import Image, ImageOps, ImageFont, ImageDraw
from os import listdir
from os.path import isfile, join

wrong_channel_text='The command you sent is not authorized for use in this channel.'
welcome_footer='HusekrBot welcomes you!'
huskerbot_footer="Generated by HuskerBot"
ref_dict = {"backblock": ["Block in the back", "OFF: 10 yards\nDEF: 10 yards", ""],
            'blindside': ['Blindside Block', 'OFF: 15 yards\nDEF: 15 yards', 'https://i.imgur.com/dyWMN7p.gif'],
            'bs': ['Bull shit', 'Referee still gets paid for that horrible call','https://i.imgur.com/0nQGIZs.gif'],
            'lowblock': ['Blocking below the waist', 'OFF: 15 yards\nDEF: 15 yards and an automatic first down', 'https://i.imgur.com/46aDB8t.gif'],
            "chop": ["Chop block", "OFF: 15 yards\nDEF: 15 yards, automatic first down", "https://i.imgur.com/46aDB8t.gif"],
            "clip": ["Clipping", "OFF: 15 yards\nDEF: 15 yards, automatic first down", "https://i.imgur.com/46aDB8t.gif"],
            "delay": ["Delay of Game", "OFF: 5 yards", ""],
            'encroachment': ['Encroachment', 'DEF: 5 yards', 'https://i.imgur.com/4ekGPs4.gif'],
            'facemask': ['Face mask', 'OFF: Personal foul, 15 yards\nDEF: Personal foul, 15 yards from the end spot of the play, automatic first down', 'https://i.imgur.com/xzsJ8MB.gif'],
            'false': ['False start', 'OFF: 5 yards', 'https://i.imgur.com/i9ZyMpn.gif'],
            "grounding": ["Intentional Grounding", "OFF: 10 yards or spot foul", ""],
            'hands2face': ['Hands to the face', 'OFF: Personal foul, 15 yards\nDEF: Personal foul, 15 yards, automatic first down', 'https://i.imgur.com/DNw5Qsq.gif'],
            'hold': ['Holding', 'OFF: 10 yards from the line of scrimmage and replay the down.\nDEF: 10 yards', 'https://i.imgur.com/iPUNHJi.gif'],
            "horsecollar": ["Horse-collar Tackle", "OFF: 15 yards\nDEF: 15 yards, automatic first down", ""],
            'hornsdown': ['Horns Down', 'Tuck Fexas', 'https://i.imgur.com/w8ACfmn.gif'],
            "illform": ["Illegal Formation", "OFF: 5 yards\nDEF: 5 yards", ""],
            'illfwd': ['Illegal forward pass', 'OFF: 5 yards from the spot of the foul and a loss of down', 'https://i.imgur.com/4CuuTDH.gif'],
            'illmotion': ['Illegal shift', 'OFF: 5 yards', 'https://i.imgur.com/RDhSuUw.gif'],
            'inelrec': ['Inelligible receiver downfield', 'OFF: 5 yards', 'https://i.imgur.com/hIfsc5D.gif'],
            "offside": ["Offsides", "OFF: 5 yards\nDEF: 5 yards", ""],
            'persfoul': ['Personal foul', 'OFF: 15 yards\nDEF: 15 yards from the end spot of the play, automatic first down', 'https://i.imgur.com/dyWMN7p.gif'],
            'pi': ['Pass interference', 'OFF: 15 yards\nDEF: Lesser of either 15 yards or the spot of the foul, and an automatic first down (ball placed at the 2 yard line if penalty occurs in the endzone)', 'https://i.imgur.com/w1Tglj4.gif'],
            'ruffkick': ['Roughing/Running into the kicker', 'DEF: (running) 5 yards, (roughing, personal foul) 15 yards and automatic first down ', 'https://i.imgur.com/UuTBUJv.gif'],
            'ruffpass': ['Roughing the passer', 'DEF: 15 yards and an automatic first down (from the end of the play if pass is completed)', 'https://i.imgur.com/XqPE1Pf.gif'],
            'safety': ['Safety', 'DEF: 2 points and possession, opponent free kicks from their own 20 yard line', 'https://i.imgur.com/Y8pKXaH.gif'],
            "sideline": ["Sideline Infraction", "OFF: first infraction is 5 yards, second infraction is 15 yards\nDEF: first infraction is 5 yards, second infraction is 15 yards", ""],
            "sub": ["Substitution Infraction", "OFF: 5 yards\nDEF: 5 yards", ""],
            'targeting': ['Targeting', 'OFF/DEF: 15 yard penalty, ejection ', 'https://i.imgur.com/qOsjBCB.gif'],
            'td': ['Touchdown', 'OFF: 6 points', 'https://i.imgur.com/UJ0AC5k.mp4'],
            'unsport': ['Unsportsmanlike', 'OFF: 15 yards\nDEF: 15 yards', 'https://i.imgur.com/6Cy9UE4.gif']
            }
flag_dict = {
    'alabama': 'https://i.imgur.com/uHXPo4n.png',
    'colorado': 'https://i.imgur.com/If6MPtT.jpg',
    'illinois': 'https://i.imgur.com/MxMaS3e.jpg',
    'indiana': 'https://i.imgur.com/uc0Q8Z0.jpg',
    'iowa': 'https://i.imgur.com/xoeCOwp.png',
    'iowa_state': 'https://i.imgur.com/w9vg0QX.jpg',
    'kansas': 'https://i.imgur.com/BL4jQfx.png',
    'kstate': 'https://i.imgur.com/qtxrPn7.png',
    'maryland': 'https://i.imgur.com/G6RX8Oz.jpg',
    'miami': 'https://i.imgur.com/MInQMLb.jpg',
    'michigan': 'https://i.imgur.com/XWEDsFf.jpg',
    'michigan_state': 'https://i.imgur.com/90a9g3v.jpg',
    'minnesota': 'https://i.imgur.com/54mF0sK.jpg',
    'nebraska': 'https://i.imgur.com/q2em9Qw.jpg',
    'northern_illinois': 'https://i.imgur.com/HpmAoIh.jpg',
    'northwestern': 'https://i.imgur.com/WG4kFP6.jpg',
    'notredame': 'https://i.imgur.com/Ofoaz7U.png',
    'ohio_state': 'https://i.imgur.com/8QwoYgm.jpg',
    'penn_state': 'https://i.imgur.com/JkQuMXf.jpg',
    'purdue': 'https://i.imgur.com/8SYhZKc.jpg',
    'rutgers': 'https://i.imgur.com/lyng39h.jpg',
    'south_alabama': 'https://i.imgur.com/BOH5reA.jpg',
    'stanford': 'https://giant.gfycat.com/PassionateRepentantCoelacanth.gif',
    'texas': 'https://i.imgur.com/rB2Rduq.jpg',
    'ttu': 'https://i.imgur.com/lpOSpH7.png',
    'tulane': 'https://gfycat.com/braveanotherdodobird',
    'usc': 'https://i.imgur.com/GrA4M0X.png',
    'wisconsin': 'https://giant.gfycat.com/PolishedFeminineBeardedcollie.gif',
    'creighton': 'https://i.imgur.com/OxVze61.png'}

async def sendImage(title: str, url: str):
    embed = discord.Embed(title=title, color=0xFF0000)
    embed.set_image(url=url)
    return embed


class ImageCommands(commands.Cog, name="Image Commands"):
    def __init__(self, bot):
        self.bot = bot

    # Start image commands
    @commands.command(aliases=["rf",])
    async def randomflag(self, ctx):
        """ A random ass, badly made Nebraska flag. """

        # This keeps bot spam down to a minimal.
        await function_helper.check_command_channel(ctx.command, ctx.channel)
        if not function_helper.correct_channel:
            await ctx.send(wrong_channel_text)
            return

        flags = []
        with open("flags.txt") as f:
            for line in f:
                flags.append(line)
        f.close()

        random.shuffle(flags)
        await ctx.send(embed=await sendImage("Random Ass Nebraska Flag", random.choice(flags)))

    @commands.command(aliases=["cf",])
    async def crappyflag(self, ctx, state=""):
        """ Outputs crappy flag. The usage is $crappyflag <state>.

        The states are:
        creighton, alabama, colorado, illinois, indiana, iowa, iowa_state,
        maryland, miami, michigan, michigan_state, minnesota,
        northern_illinois, northwestern, notredame, ohio_state,
        penn_state, purdue, south_alabama, rutgers, stanford, texas, ttu,
        tulane, usc, wisconsin """

        # This keeps bot spam down to a minimal.
        await function_helper.check_command_channel(ctx.command, ctx.channel)
        if not function_helper.correct_channel:
            await ctx.send(wrong_channel_text)
            return

        if state:
            if state.lower() == "nebraska":
                await ctx.send(embed=await sendImage("Amazing Flag", flag_dict[state.lower()]))
            else:
                await ctx.send(embed=await sendImage("Crappy Flag", flag_dict[state.lower()]))
        else:
            random_state = random.choice(list(flag_dict.keys()))
            await ctx.send(embed=await sendImage("Crappy Flags", flag_dict[random_state]))

    @commands.command()
    async def ohyeah(self, ctx):
        """Oh yeah. It's all coming together."""
        await ctx.send(embed=await sendImage("If we have Frost, we have national championships.", "https://i.imgur.com/tdN5IEG.png"))

    @commands.command()
    async def crabfrost(self, ctx):
        """CELEBRATE"""
        await ctx.send(embed=await sendImage("🦀D🦀A🦀N🦀C🦀E🦀P🦀A🦀R🦀T🦀Y🦀", "https://thumbs.gfycat.com/FalseTestyDotterel-size_restricted.gif"))

    @commands.command(aliases=["dance",])
    async def danceparty(self, ctx):
        """Get on the floooooor!"""
        await ctx.send(embed=await sendImage("🕺💃👯‍♂️👯‍♀️", "https://thumbs.gfycat.com/GiddyOldfashionedBluebreastedkookaburra-size_restricted.gif"))

    @commands.command()
    async def fuckiowa(self, ctx):
        """Get on the floooooor!"""
        await ctx.send(embed=await sendImage("FUCK IOWA", "https://thumbs.gfycat.com/CanineEssentialGelding-size_restricted.gif"))

    @commands.command(aliases=["possum",])
    async def possums(self, ctx):
        """Possum Palace"""
        await ctx.send(embed=await sendImage("Possum", "https://i.imgur.com/UI3l2Xu.jpg"))

    @commands.command()
    async def pour(self, ctx):
        """Pour that koolaid baby"""
        await ctx.send(embed=await sendImage("OH YEAH!", "https://media.giphy.com/media/3d9rkLNvMXahgQVpM4/source.gif"))

    @commands.command()
    async def iowasux(self, ctx):
        """ Iowa has the worst corn. """
        await ctx.send(embed=await sendImage("IOWA SUX", "https://i.imgur.com/j7JDuGe.gif"))

    @commands.command()
    async def potatoes(self, ctx):
        """ Potatoes are love; potatoes are life. """
        authorized = False

        for r in ctx.author.roles:
            if r.id == 583842320575889423:
                authorized = True

        if authorized:
            await ctx.send(embed=await sendImage("Po-Tay-Toes", "https://i.imgur.com/Fzw6Gbh.gif"))
        else:
            await ctx.send('You are not a member of the glorious Potato Gang!')

    @commands.command()
    async def asparagus(self, ctx):
        """ I guess some people like asparagus. """
        authorized = False

        for r in ctx.author.roles:
            if r.id == 583842403341828115:
                authorized = True

        if authorized:
            await ctx.send(embed=await sendImage("Asparagan", "https://i.imgur.com/QskqFO0.gif"))
        else:
            await ctx.send('You are not a member of the glorious Asparagang!')

    @commands.command()
    async def flex(self, ctx):
        """ S T R O N K """
        await ctx.send(embed=await sendImage("FLEXXX", "https://i.imgur.com/92b9uFU.gif"))

    @commands.command()
    async def shrug(self, ctx):
        """ Who knows 😉 """
        await ctx.send(embed=await sendImage("🤷‍♀", "https://i.imgur.com/Yt63gGE.gif"))

    @commands.command()
    async def ohno(self, ctx):
        """ This is not ideal. """
        await ctx.send(embed=await sendImage("Big OOOOOOF", "https://i.imgur.com/f4P6jBO.png"))

    @commands.command()
    async def bigsexy(self, ctx):
        """ Give it to me Kool Aid man. """
        await ctx.send(embed=await sendImage("OOOHHH YEEAAAHHH", "https://i.imgur.com/UpKIx5I.png"))

    @commands.command()
    async def whoami(self, ctx):
        """ OH YEAH! """
        await ctx.send(embed=await sendImage("Who the F I am?", "https://i.imgur.com/jgvr8pd.gif"))

    @commands.command()
    async def thehit(self, ctx):
        """ The hardest clean hit ever. """
        await ctx.send(embed=await sendImage("CLEAN HIT (AT THE TIME)!", "https://i.imgur.com/mKRUPoD.gif"))

    @commands.command(aliases=['allluck','luck','al', 'whatusay'])
    async def uwot(self, ctx):
        """ EXCUSE ME WHAT? """
        await ctx.send(embed=await sendImage("What did you just say?!", "https://i.imgur.com/XpFWJp9.gif"))

    @commands.command()
    async def strut(self, ctx):
        """ Martinez struttin his stuff """
        await ctx.send(embed= await sendImage("Dat Strut", "https://media.giphy.com/media/iFrlakPVXLIj8bAqCc/giphy.gif"))

    @commands.command()
    async def bones(self, ctx):
        """ Throwing bones! """
        await ctx.send(embed=await sendImage("☠ Bones ☠", "https://i.imgur.com/0gcawNo.jpg"))

    @commands.command(aliases=['flip',])
    async def theflip(self, ctx):
        """ Frost doing frosty things """
        await ctx.send(embed=await sendImage("Too Cool", "https://media.giphy.com/media/lllup6g803SaeRUwiM/giphy.gif"))

    @commands.command()
    async def guzzle(self, ctx):
        """ Let the cup runeth over """
        await ctx.send(embed= await sendImage("Give it to me bb", "https://i.imgur.com/OW7rChr.gif"))

    @commands.command(aliases=["td",])
    async def touchdown(self, ctx):
        """ Let the cup runeth over """
        await ctx.send(embed= await sendImage("🏈🎈🏈🎈", "https://i.imgur.com/Wh4aLYo.gif"))

    @commands.command(aliases=["ref",])
    async def referee(self, ctx, call=None):
        """ HuskerBot will tell you about common referee calls. Usage is `$refereee <call>`.\n
        The calls are: blackblock, blindside, bs, lowblock, chip, clip, delay, encroachment, facemask, false, grounding, hands2face, hold, horsecollar, hornsdown, illform, illfwd, illmotion, offside, persfoul, pi, ruffkick, ruffpass, safety, sideline, sub, targeting, td, unsport  """

        if not call:
            await ctx.send("A penalty must be included. `$referee|ref <call>`. Check `$help referee` for more informaiton.")
            return

        # This keeps bot spam down to a minimal.
        await function_helper.check_command_channel(ctx.command, ctx.channel)
        if not function_helper.correct_channel:
            await ctx.send(wrong_channel_text)
            return

        call = call.lower()

        penalty_name = ref_dict[call][0]
        penalty_comment = ref_dict[call][1]
        penalty_url = ref_dict[call][2]

        embed = discord.Embed(title='HuskerBot Referee', color=0xff0000)
        embed.add_field(name='Referee Call', value=penalty_name, inline=False)
        embed.add_field(name='Description', value=penalty_comment, inline=False)
        embed.set_thumbnail(url=penalty_url)
        embed.set_footer(text="Referee calls " + huskerbot_footer)
        await ctx.send(embed=embed)

    @commands.command(aliases=["fg",])
    async def flag_gen(self, ctx):
        async def tint_image(src, color="#FFFFFF"):
            src.load()
            r, g, b, alpha = src.split()
            gray = ImageOps.grayscale(src)
            result = ImageOps.colorize(gray, (0, 0, 0, 0), color)
            result.putalpha(alpha)
            return result

        async def random_words(source: list):
            random.shuffle(source)

            titles = ["The Great Seal of", "The Commonwealth of", "Republic", "Great Seal of the State of", "Commonwealth of", "Seal of the State of", "State of", "Sigillum Republicae" ]
            return_string = titles[random.randint(0, len(titles)-1)]  # Calling out of range errors
            return_string += "\n{:>15}\n".format("of")
            return_string += "{} {}".format(source[0].strip(), source[1].strip())
            return return_string

        # Directory strings
        emojis_dir = "media/emojis"
        blank_flag = "media/raw/blank_flag.png"
        created_flag = "media/saved/{}_created_flag.png".format(str(ctx.author))

        # Get list of emojis, shuffle the list, pick random emoji, and create an Image.
        poop_files = [f for f in listdir(emojis_dir) if isfile(join(emojis_dir, f))]
        random.shuffle(poop_files)
        print("Poop: {}".format(poop_files[0]))
        img_poop_raw = Image.open("{}/{}".format(emojis_dir, poop_files[0]))
        sizes = img_poop_raw.width * 3, img_poop_raw.height * 3
        img_poop = img_poop_raw.resize(size=sizes, resample=PIL.Image.NEAREST)

        # Turn the blank flag into a random color.
        img_flag = Image.open(blank_flag)
        random_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        tinted_flag = await tint_image(img_flag, random_color)

        new_img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
        new_img.paste(tinted_flag, ((new_img.width - tinted_flag.width) // 2, (new_img.height - tinted_flag.height) // 2))
        new_img.paste(img_poop, ((new_img.width - img_poop.width) // 2, (new_img.height - img_poop.height) // 2), mask=img_poop)

        # Random list of words
        words = []
        with open("words.txt") as f:
            for word in f:
                words.append(word)
        f.close()

        draw = ImageDraw.Draw(new_img)
        font = ImageFont.truetype("media/font.ttf", 100)
        draw.text((new_img.width/6, new_img.height/3), await random_words(words), (255, 255, 255, 255), font=font)

        # Save and send
        new_img.save(created_flag)
        await ctx.send(file=discord.File(created_flag))
    # End image commands


def setup(bot):
    bot.add_cog(ImageCommands(bot))