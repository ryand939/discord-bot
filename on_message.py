from random import randrange

# the bot sometimes does random things even if the user doesnt enter a command

# main entry point of file
async def handle_on_message(message):
    await donut_hypeman(message)
    # specific to daercord message events
    if message.guild.name == "daercord":
        await fart_debuff(message)




# reacts 🔥 to my friends message if it is in all caps
async def donut_hypeman(message):
    # all caps message 
    friendID = 210544305163468800   #DonutSandwich01#0707
    if message.author.id == friendID and message.content == message.content.upper() and message.content != "":
        await message.add_reaction('🔥')


# checks if the user has the fart role and reacts 💩 in 1/10 chance
async def fart_debuff(message):
    fartRoleID = 632691885538017328
    if message.author.get_role(fartRoleID) != None and (randrange(10) + 1) == 1:
        await message.add_reaction('💩')
