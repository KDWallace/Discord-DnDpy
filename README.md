# Discord-DnDpy
A Discord Bot for use in D&D. Generates images for custom player stats in the style of monster manual entries as well as an image generator for NLRMEv2 10000 wild magic surge effects with interactable buttons

The player card has several customisable options using the discord slash command. Everything is optional and will be randomly generated without input
 - Name
 - Species
 - Alignment
 - Number of dice to use in stat generation (eg: if 5 dice are used, 5d6 are rolled and the top 3 values are used. Default is standard array of 15,14,13,12,10,8)
 - Stat Override
 - Stat prioritisation order (How should the stats be ordered from highest to lowest?)

The wild magic surge generates a card in a similar style taking a random choice from the d10000 table provided by the NLRMEv2 which can be hidden. This also creates 3 discord interactable buttons with each generation:
- "Reroll" will create a new card
- "Roll Cure" rolls from the d100 table of cures and will generate a new image with said curing condition
- "Docs Download" will provide the user with the PDF of the original NLRMEv2
