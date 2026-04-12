"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def print_recommendations(profile_name: str, recommendations: list[tuple]) -> None:
    """Print recommendation results for a single user profile."""
    print("\n" + "=" * 64)
    print(f"PROFILE: {profile_name}")
    print("=" * 64)

    if not recommendations:
        print("No recommendations available.")
        return

    for rank, rec in enumerate(recommendations, start=1):
        song, score, explanation = rec
        reasons = [r.strip() for r in explanation.split(";") if r.strip()]

        print(f"\n{rank}. {song['title']}")
        print(f"   Final Score : {score:.2f}")
        print("   Reasons:")
        for reason in reasons:
            print(f"   - {reason}")


def main() -> None:
    songs = load_songs("data/songs.csv") 

    user_profiles = {
        "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.88},
        "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.38},
        "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.92},
        "Conflicting Pop Sad": {"genre": "pop", "mood": "sad", "energy": 0.90},
        "Impossible Classical Aggressive": {"genre": "classical", "mood": "aggressive", "energy": 0.97},
        "Mood Overpowers Genre": {"genre": "metal", "mood": "chill", "energy": 0.55},
        "Genre Synonym Typo": {"genre": "hip-hop", "mood": "confident", "energy": 0.75},
        "Mood Synonym Mismatch": {"genre": "indie pop", "mood": "sad", "energy": 0.40},
        "Empty Categorical": {"genre": "", "mood": "", "energy": 0.50},
        "Missing Fields": {},
        "Out Of Range Low Energy": {"genre": "rock", "mood": "intense", "energy": -2.0},
        "Out Of Range High Energy": {"genre": "lofi", "mood": "chill", "energy": 9.0},
        "NaN Energy": {"genre": "pop", "mood": "happy", "energy": float("nan")},
        "Infinite Energy": {"genre": "pop", "mood": "happy", "energy": float("inf")},
        "Non Numeric Energy": {"genre": "pop", "mood": "happy", "energy": "very high"},
    }

    run_all_profiles = True

    if run_all_profiles:
        print("\n" + "=" * 64)
        print("RUNNING TOP 5 RECOMMENDATIONS FOR ALL PROFILES")
        print("=" * 64)
        for profile_name, user_prefs in user_profiles.items():
            try:
                recommendations = recommend_songs(user_prefs, songs, k=5)
                print_recommendations(profile_name, recommendations)
            except Exception as exc:
                print("\n" + "=" * 64)
                print(f"PROFILE: {profile_name}")
                print("=" * 64)
                print(f"Error while scoring this profile: {type(exc).__name__}: {exc}")
        print("\n" + "=" * 64)
        return

    # Choose one profile when run_all_profiles is False.
    profile_name = "High-Energy Pop"
    user_prefs = user_profiles[profile_name]
    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(profile_name, recommendations)
    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
