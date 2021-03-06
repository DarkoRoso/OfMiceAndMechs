# OfMiceAndMechs
a to-be prototype for a game

* [install and run](INSTALL.md)
* [screenshots](VISUALS.md)
* [news (latest: "commit 1203-1302")](NEWS.md)
* [credits](CREDITS.md)

discord: https://discord.gg/uUMWHbS

## state of the game

Quite some work was done on the game so far. It has a playtime of 11 minutes for a near optimal run at the time of writing ([how to beat the game](HOWTO.md)), actual playtime should be magnitudes longer. You have beaten the game when you see "good job. credits". I try to get playtesters to play the game and meanwhile fix the bugs und broken features. This sadly means now real playtime extension for quite some time and no significant progress with the story board.

At this stage it would really be useful to get help from whoever is reading this. If you notice bugs or have suggestions, please open an issue or contact me by mail. If you want to contribute, please start a pull request or contact me by mail. If you are unsure about something or want to contribute or just want to say hello write a quick mail.

mail:
marxmustermann@riseup.net

I will start to use branches with a dev branch with a lot if crashes and aim to keep the master somewhat stable, so you don't have to suffer through each crash i produce. I did hower start again to move code to maser more often.

The detailed state of the game follows:

* The game looks good enough for me and the mechanics work most of the time, too.
* The cutscenes need more work but they are ok for now, too.
* there is a lot of storytelling (in relation to other content)
* Minigames like fireing the ovens or driving the mechs trough walls are fun for me
* crashes do happen but not constantly
* The game feels like a game (a boring one, but like a game)
* a save/load system exists and loading works most of the time
* The game offers a challenge, but still is somewhat uneventfull

A change of tactics was done. I disregard the normal mode for now and try to do a fresh start regarding gameplay and tutorial. I try now to write the game so that i personally like playing the game. For now this means randomized puzzles. I set up a new area containing very little to test these gamplay concept and if this works i will try to reintegrate the area and ideas into the main mech.

I think the biggest issue is that the main game mechanic is not working or is not clearly visible. This is gaining control (over npcs), controlling npcs and exercising power to gain power. The negation of this is also missing. This is loosing power by inefficent use of power or by not defending your position. The puzzles are not clearly visible, too. This is kind of intended, but everything has to be more obvious.

To highlighten the puzzles a malicous implant is introduced as a story device. To make puzzles more testable the gameplay will be a series of minigames with alternate paths to allow progress if a minigame is unsolvable. The minigames are randomly generated and it is possible that they are generated unsolvable to keep the challenge up.

Development speed depends on Code quality, so it is a important issue. It is a pretty big issue and grows with every change done on the code, so this issue will probably never be solved. But it seems like code quality will improve if i keep a pattern of doing a round of new features and a round of code cleanup. Since code qualtiy cannot be too good it seems more reasonable to skip a feature adding round than skipping a cleanup round.
