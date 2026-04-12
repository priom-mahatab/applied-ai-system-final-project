# Reflection: Profile Pair Comparisons

## Pair 1: High-Energy Pop vs Chill Lofi
High-Energy Pop returns songs like Sunrise City and Gym Hero, while Chill Lofi returns Library Rain and Midnight Coding. This shift makes sense because the first profile asks for high energy and pop, but the second asks for chill lofi with lower energy. In plain terms, one profile sounds like a workout playlist and the other sounds like study music.

## Pair 2: High-Energy Pop vs Conflicting Pop Sad
Both profiles still show pop songs near the top, but Conflicting Pop Sad pulls in Gym Hero and even Storm Runner because the mood "sad" does not match many songs in the dataset. This is why Gym Hero can keep showing up for people who wanted happy pop or related pop vibes: it gets strong points from genre and very close energy, even when mood is off. The model is basically saying, "I could not find your mood, so I used energy and genre to fill the gap."

## Pair 3: Deep Intense Rock vs Mood Overpowers Genre
Deep Intense Rock puts Storm Runner first, but Mood Overpowers Genre puts chill songs like Midnight Coding and Library Rain first. That change makes sense because mood has a strong weight, so asking for chill can beat a genre preference like metal if energy is reasonably close. In everyday terms, vibe can overpower genre in this scoring setup.

## Pair 4: Genre Synonym Typo vs Mood Synonym Mismatch
Genre Synonym Typo still finds City Cipher because the mood confident matches, but it loses genre points due to "hip-hop" not exactly matching "hip hop." Mood Synonym Mismatch also loses a key match because "sad" is not the same label as existing moods like moody or reflective. Both cases show the same pattern: tiny wording differences create big recommendation changes.

## Pair 5: Empty Categorical vs Missing Fields
These two profiles produced almost the same top songs, including Velvet Static and Dust Road Radio. That makes sense because missing fields fall back to defaults and behave similarly to blank genre and mood entries. When that happens, energy drives most of the ranking and results become generic.

## Pair 6: Impossible Classical Aggressive vs Deep Intense Rock
Impossible Classical Aggressive puts Iron Horizon first and Moonlit Sonata Rework second, while Deep Intense Rock strongly prefers Storm Runner. This makes sense because the impossible profile mixes two hard-to-combine preferences, so the model picks whichever song wins one major category plus energy. The rock profile is more coherent, so results look cleaner and more consistent.
