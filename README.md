# ParaCTF - An IRL Paragliding CTF game

## Rules
These are classical ctf rules applied to (real) paragliding. A game is set with flags (sort-of-competition-turnpoints : cylinders centered on a point with a certain radius). Teams join a game, Pilots join a Team. Once a team member enters a flag zone, he/her captures it for his/her team. The flags can be retaken by another team, depending on the scoring model in place for the current game. 

A scoring system is attached to the game to calculate the scores and flag statuses (same principle as if a "Race to goal" or "Elapsed time" scoring system is attached to a competition task).

The game page screenshot:
![play_screen](doc_images/play.png)

## Models
### Games

Models are sort of competition tasks with only the turnpoints (without times nor teams, nor scoring system defined). This was meant to save interesting tasks (tactical positions) for future games.

Game model editor
![play_screen](doc_images/editor.png)

### CTF

CTF (called ***igames*** in the code, url and some other places) are Game instances on a Game Model. Teams can be added.
CTF are planned for 3 hours for now, but that's already a variable somewhere

CTF setup, team creation:
![play_screen](doc_images/game.png)


### Teams
Teams are made of members. No limit on the number of Teams / Igame. They're defined by name & color, that will be reflected on the flag once they capture one.

### Team Members + location History
Mostly explicit. These are the pilots. Not that each one receive a unique password when joining a game, that will act as a vlaidation key for updating his/her position.


### Scoring systems
#### Introduction
Scoring systems are finally the core of the game and are abstracted for evolution. For now 2 implementations (trad/degress) are available.
In general, implementing a scoring system requires to implement 2 functions:
- score_latest_update > get a quick latest update for the client's view to update (especially on Flags' statuses)
- score_igame > Get teams's final score (or at least the latest ones)

Note there is a parent scoring class that implements a bunch of helpful methods, for instance checking if a pilot's GPS location is within a flag cylinder.
  
#### trad
The last team member in a flag will give the flag to his or her team, and store pilot's altitude in the flag. Anohter pilot can take over this flag only if his/her altitude is above the previous one.

1pt/sec once for each captured flag for a team, as long as the flag belongs to them

#### degress
Almost the same rule, but once the last pilot of a team leaves the flag, the stored altitude will decrease by 1 meter every second (the goal is to give more chance to recapture, or simply take into account the flying condition that may change during the game (for instance cloud base getting lower)

The same 1pt/sec for each captured flag for a team, as long as the flag belongs to them.

#### More ideas:
- ***getthemall***: once a lag is captured, it can't be recaptured. Score only reflects the number of flags
- ***firstbetter***: Gives bonus to the first team capturing a flag (i.e. equivalent of 10 min capture time, so 600pts using the *trad* method f the same scoring applies)
- ***degresslimit***: A flag stay captured for a while once the last pilot leaves it, but only for a certain time. Then it must be recapture to score again. Scoring coule even be even progressive with a 1/n function during/after that time limit (real scoring systems love such degressive counting). It's a sort of an extesnion for the *degress* system.
- ***groupmode***: at least N pilots must capture a flag simultaneously (or within a defined time range) to capture it... 

### Thoughts and ideas
Even though very close to a real competition task, here the game machanics are a bit different and may offer a bit of fun to the players. Group flying is not primarily a goal for such a game, despite the "Team" notion, but could easily be more important with a new scoring model tkaing such variable into account.
However, the game may encourage pilots to enjoy average flying condition and help them stay/play into the air. Also Team Member must communicate with each other and must think about tactics while being in the air. That raises both security concerns but may also improves it by doing a bit-of-multitasking while flying. These are finally very similar to a *normal* competition too.

## Development 

### Front
JS/ajax code + Leaflet. position & altitude taken from the navigator.geolocation.getCurrentPosition() builtin method.
Dedicated pages for each step (landing page/editor/igame creation/play) with ***a lot*** of code redundancy there.

### Back
A flask/python backend, using SQLAlchemy as ORM over a SQLITE3 file DB. Sounds OK but would also require a bit of cleaning and ordering.
Basically :
- an app.py flask receiving requests and dispatching to a sort-of-controller
- a game.py controller
- a models.py model code
- a game.db sqlite3 DB file. So far it seems to be efficient with a couple of thousands locations histories

### Running it
NGINX configured for serving
- the static web/ directory on an exposed static/ directory in the URL
- the api through an RP mapping to the flask app running in another process.

This works fine.

### Note
Most of the code was produced by ChatGPT.

### TODO
- The front part needs a big redesign / code refactoring. PR welcome.
    - Redo left menu with unifed Look&Feel
    - a bit of code refactoring for the map view which is almost duplicated between the different pages.
- CTF Creation : new params to take into account (time to play, scoring method...)
- maybe lock on Igames once they started, and an explicit start button
- position caching (+timestamp) when server (or data network !) is unavailable for a while
- client's data is very much trusted, for pure game data but also for the technical stuff. As i'm not an expert in SQLalchemy but that raises a couple of security issues to me.
- Improve Member auto-naming
- Dockerfile to facilitate the deployments for the backend
