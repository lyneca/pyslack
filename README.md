
Rules of the Game
=================

Conspiracy can be played in a variety of formats and media, with any group of people that can all contact eachother for a period of time.
This readme describes how to play with the slack bot.

Each player needs to eliminate one other player.
This chain of targets forms a complete circle. 
Players can attempt to eliminate each other at any time.
This process is referred to as capping or tagging.

If you cap the correct person, they are eliminated, of course.
If you cap the wrong person, they are not eliminated, and you are!

At the start of the game you are told the person who can cap you. 
This person is referred to as your Kappa. (think capper)
Ideally you do not want them to know that they can cap you.
In order to progress you will need to swap information with someone.
In this game you can use a command called KSWAP to do this.
As you gain more information you may be able to figure out who your actual target is.

The last two players in the game tend to effectively be equal first, but ways of breaking the draw can be fun.
In this game the game only ends when one player is left.
Therefore the last two players will both be able to cap eachother.
A full list of rankings are provided at the end to acknowledge everyone's efforts.


Using this bot as a player
==========================

When a game has not started there are two commands that can be used:
 * SIGN UP
 * SIGN DOWN
 * LIST

These do what they seem to do.
LIST lists players who are signed up.

When a game has started, all the players who have SIGNed UP are given their kappa.
The following commands then become usable:
 * CAP <target>
 * KSWAP <target> [delayed|cancel|direct]
 * LIST
 * RESIGN

CAP is used to cap a target, i.e. attempt to eliminated them.
KSWAP is used to prove to someone who your kappa is, and has three possible flags:
 * delayed (default option) waits until they also tell you info before you tell them anything.
 * cancel removes this offer if the transfer hasn't already been made
 * direct doesn't wait, and immediately tells them who your kappa is
LIST lists players in the game and says which have been eliminated.
RESIGN eliminates you from the game without looking like you failed a CAP.


Using this bot as an admin
==========================

Some operational commands exist that only a hard-coded list of players can use.

While a game hasn't begun:
 * START - starts a game from the list of players signed up
 * LOAD - loads a game from local .dat files
 * TERMINATE - shuts down the program safely

When a game is being played:
 * SAVE - writes files that can be used to LOAD later (does not end the game, also these files will be overwritteen every time someone is eliminated)
 * END - ends current game early, with no fanfare to victors.

Commands should be added in the future to manage admin rights.
