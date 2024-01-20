# ParaCTF - A IRL Paragliding CTF game

## Rules
### Games models

Models are sort of competition tasks with turnpoint without times nor teams. This was meant to save interesting tasks for replay.

### CTF

CTF (called ***igames*** in the code, url and some other places) are Game instances on a Game Model. Teams can be added.
CTF are planned for 3 hours for now, but that's already a varible somewhere

### Teams
Teams are made of members. No limit on the number of Teams / Igame

### Team Members
Mostly explicit.

### Scoring systems
#### Introduction
Scoring systems are abstracted for evolution. For now 2 are available.
In general, implementing a scoring system requires to implement 2 function:
- score_latest_update > get a quick latest update for the client's view to update (especially on Flags' statuses)
- score_igame > Get teams's final score (or at least the latest ones)

#### trad
The last team member in a flag will give the flag to his or her team, and store pilot's altitude in the flag. Anohter pilot can take over this flag only if his/her altitude is above the previous one.
1pt / s once for each captured flag for a team, as long as the flag belongs to them

#### degress
Almost the same rule, but once the last pilot of a team leaves the flag, the stored altitude will decrease by 1 meter every second (the goal is to give more chance to recapture, o rsimply take into account flying condition that may change during the game, for instance cloud base getting lower)
Same 1pt/s for each captured flag for a team, as long as the flag belongs to them.


## Development 

### Front
JS/ajax code + Leaflet. position & altitude taken from the navigator.geolocation.getCurrentPosition() builtin method.
Dedicated pages for each step (landing page/editor/igame creation/play) with ***a lot*** of code redundancy there.

### Back
A flask/python backend, using SQLAlchemy as ORM. Sounds OK but would also require a bit of cleaning and ordering.
Basically :
- an app.py flask receiving requests and dispatching to a sort-of-controller
- a game.py controller
- a models.py model code

### Running it
NGINX configured for serving
- the static web/ directory on an exposed static/ directory in the URL
- the api through an RP mapping to the flask app running in another process.

This works fine.


### Note
Most of the code was produced by ChatGPT.

### TODO
- The front part needs a big redesign / code refactoring. PR welcome.
- CTF Creation : new params to take into account (time to play, scoring method...)
- maybe lock on Igames once they started, and an explicit start button
- position caching (+timestamp) when server (or data network !) is unavailable for a while
- client's data is very much trusted, for pure game data but also for the technical stuff. As i'm not an expert in SQLalchemy but that raises a couple of security issues to me.
- Improve Member auto-naming