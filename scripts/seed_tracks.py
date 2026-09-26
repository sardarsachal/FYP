"""
Seed list of real tracks for the NextTrack enrichment pipeline.

This is *not* the dataset. It is only a fixed list of (artist, title, genre)
queries. Every actual metadata value used for scoring — tempo, mood, year,
popularity — is fetched from external services (MusicBrainz, AcousticBrainz,
Last.fm) by scripts/enrich_dataset.py. The seed exists so the resulting
dataset is *reproducible*: unlike live charts (which change daily), this fixed
query set produces the same catalogue every run, which matters for a
repeatable evaluation.

`genre` is drawn from the same controlled vocabulary as the original curated
dataset so the UI, tests, and scoring stay consistent:
    ambient, country, edm, folk, hiphop, jazz, lofi, pop, rock, synthpop

Well-known catalogue tracks are chosen deliberately because they have the best
AcousticBrainz coverage (community-submitted audio analysis skews to popular
music). Where a track is missing from AcousticBrainz, the pipeline falls back
to a per-genre default, so coverage gaps are never fatal.
"""

# (artist, title, genre)
SEED_TRACKS: list[tuple[str, str, str]] = [
    # ---- rock ----
    ("Radiohead", "Creep", "rock"),
    ("Nirvana", "Smells Like Teen Spirit", "rock"),
    ("Queen", "Bohemian Rhapsody", "rock"),
    ("The Killers", "Mr. Brightside", "rock"),
    ("Foo Fighters", "Everlong", "rock"),
    ("Arctic Monkeys", "Do I Wanna Know?", "rock"),
    ("Red Hot Chili Peppers", "Californication", "rock"),
    ("The White Stripes", "Seven Nation Army", "rock"),
    ("Coldplay", "Yellow", "rock"),
    ("Muse", "Uprising", "rock"),
    ("Kings of Leon", "Sex on Fire", "rock"),
    ("Green Day", "Boulevard of Broken Dreams", "rock"),

    # ---- pop ----
    ("Michael Jackson", "Billie Jean", "pop"),
    ("Dua Lipa", "Don't Start Now", "pop"),
    ("Taylor Swift", "Shake It Off", "pop"),
    ("Ed Sheeran", "Shape of You", "pop"),
    ("Adele", "Rolling in the Deep", "pop"),
    ("Katy Perry", "Firework", "pop"),
    ("Bruno Mars", "Uptown Funk", "pop"),
    ("Lady Gaga", "Bad Romance", "pop"),
    ("The Weeknd", "Blinding Lights", "pop"),
    ("Rihanna", "Umbrella", "pop"),
    ("Maroon 5", "This Love", "pop"),
    ("Justin Timberlake", "Can't Stop the Feeling!", "pop"),

    # ---- edm / electronic ----
    ("Daft Punk", "One More Time", "edm"),
    ("Avicii", "Levels", "edm"),
    ("Calvin Harris", "Summer", "edm"),
    ("Swedish House Mafia", "Don't You Worry Child", "edm"),
    ("David Guetta", "Titanium", "edm"),
    ("Deadmau5", "Strobe", "edm"),
    ("Zedd", "Clarity", "edm"),
    ("Skrillex", "Bangarang", "edm"),
    ("The Chemical Brothers", "Galvanize", "edm"),
    ("Fatboy Slim", "Right Here, Right Now", "edm"),

    # ---- hiphop ----
    ("Eminem", "Lose Yourself", "hiphop"),
    ("Kanye West", "Stronger", "hiphop"),
    ("Kendrick Lamar", "HUMBLE.", "hiphop"),
    ("Dr. Dre", "Still D.R.E.", "hiphop"),
    ("Jay-Z", "99 Problems", "hiphop"),
    ("Drake", "Hotline Bling", "hiphop"),
    ("Notorious B.I.G.", "Juicy", "hiphop"),
    ("Snoop Dogg", "Drop It Like It's Hot", "hiphop"),
    ("50 Cent", "In Da Club", "hiphop"),
    ("OutKast", "Hey Ya!", "hiphop"),

    # ---- jazz ----
    ("Miles Davis", "So What", "jazz"),
    ("Dave Brubeck", "Take Five", "jazz"),
    ("John Coltrane", "Blue Train", "jazz"),
    ("Louis Armstrong", "What a Wonderful World", "jazz"),
    ("Nina Simone", "Feeling Good", "jazz"),
    ("Herbie Hancock", "Cantaloupe Island", "jazz"),
    ("Bill Evans", "Waltz for Debby", "jazz"),
    ("Chet Baker", "My Funny Valentine", "jazz"),

    # ---- folk ----
    ("Bob Dylan", "Blowin' in the Wind", "folk"),
    ("Simon & Garfunkel", "The Sound of Silence", "folk"),
    ("Mumford & Sons", "Little Lion Man", "folk"),
    ("Fleet Foxes", "White Winter Hymnal", "folk"),
    ("Bon Iver", "Skinny Love", "folk"),
    ("The Lumineers", "Ho Hey", "folk"),
    ("José González", "Heartbeats", "folk"),
    ("Nick Drake", "Pink Moon", "folk"),

    # ---- country ----
    ("Johnny Cash", "Ring of Fire", "country"),
    ("Dolly Parton", "Jolene", "country"),
    ("Willie Nelson", "On the Road Again", "country"),
    ("Kacey Musgraves", "Rainbow", "country"),
    ("Chris Stapleton", "Tennessee Whiskey", "country"),
    ("Shania Twain", "Man! I Feel Like a Woman!", "country"),
    ("Keith Urban", "Somebody Like You", "country"),
    ("Carrie Underwood", "Before He Cheats", "country"),

    # ---- synthpop ----
    ("Depeche Mode", "Enjoy the Silence", "synthpop"),
    ("New Order", "Blue Monday", "synthpop"),
    ("a-ha", "Take On Me", "synthpop"),
    ("Pet Shop Boys", "West End Girls", "synthpop"),
    ("CHVRCHES", "The Mother We Share", "synthpop"),
    ("M83", "Midnight City", "synthpop"),
    ("Tears for Fears", "Everybody Wants to Rule the World", "synthpop"),
    ("Eurythmics", "Sweet Dreams (Are Made of This)", "synthpop"),

    # ---- ambient ----
    ("Brian Eno", "An Ending (Ascent)", "ambient"),
    ("Boards of Canada", "Roygbiv", "ambient"),
    ("Aphex Twin", "Xtal", "ambient"),
    ("Tycho", "A Walk", "ambient"),
    ("Bonobo", "Kong", "ambient"),
    ("Ólafur Arnalds", "Near Light", "ambient"),
    ("Moby", "Porcelain", "ambient"),
    ("Sigur Rós", "Hoppípolla", "ambient"),

    # ---- lofi / downtempo ----
    ("Nujabes", "Feather", "lofi"),
    ("J Dilla", "Time: The Donut of the Heart", "lofi"),
    ("Massive Attack", "Teardrop", "lofi"),
    ("Portishead", "Glory Box", "lofi"),
    ("Thievery Corporation", "Lebanese Blonde", "lofi"),
    ("Air", "La Femme d'Argent", "lofi"),
    ("Zero 7", "In the Waiting Line", "lofi"),
    ("DJ Shadow", "Midnight in a Perfect World", "lofi"),
]
