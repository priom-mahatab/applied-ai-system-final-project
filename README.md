# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world platforms like Spotify and YouTube usually use hybrid recommenders that combine collaborative filtering (patterns from similar users) with content-based filtering (item features like genre, mood, and audio traits), then rank results by predicted satisfaction. In this simulation, we prioritize a **content-based** approach because it is transparent and easy to test: each song is scored by how closely its features match a user taste profile, and the top-scoring songs are recommended.

Our finalized Algorithm Recipe is:

1. Read the user preferences and one song from the CSV.
2. Give points for an exact **genre** match.
3. Give slightly more points for an exact **mood** match, since mood often describes the listener’s immediate vibe.
4. Add smaller points for audio features that are close to the user’s targets, such as `energy`, `tempo_bpm`, `valence`, `danceability`, and `acousticness`.
5. Add a small bonus when the user likes acoustic music and the song has high acousticness.
6. Sum the points, rank all songs by score, and return the top 5 recommendations.

This balance keeps genre important without letting it overpower everything else. A song that matches the mood and energy well should still be able to rank above a song that only matches the genre.

Potential bias note: this system might over-prioritize genre if the genre weight is too high, which could cause it to ignore great songs that better match the user’s mood or energy. Because the catalog is also small, underrepresented genres or moods may appear less often in the final recommendations.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Output Sample

![Terminal output sample](images/Screenshot%202026-04-11%20at%207.30.46%E2%80%AFPM.png)

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

I tested a range of user profiles, including standard profiles (`High-Energy Pop`, `Chill Lofi`, `Deep Intense Rock`) and adversarial profiles (`Conflicting Pop Sad`, `Genre Synonym Typo`, `Mood Synonym Mismatch`, `Empty Categorical`, `Missing Fields`, and out-of-range energy values).

Key observations from experiments:

- Clear profiles gave intuitive results: `High-Energy Pop` surfaced songs like **Sunrise City**, while `Chill Lofi` surfaced **Library Rain** and **Midnight Coding**.
- Conflicting preferences revealed tradeoffs: in `Conflicting Pop Sad`, mood matching often failed but songs like **Gym Hero** still ranked high because genre and energy were strong.
- Text sensitivity mattered: `hip-hop` did not match `hip hop`, so genre points were lost even when user intent was basically the same.
- Missing or blank fields (`Missing Fields`, `Empty Categorical`) produced very similar outputs, showing fallback behavior driven mostly by default energy.
- Invalid input behavior was exposed: non-numeric energy (for example, `"very high"`) raised a `ValueError`.

These tests helped verify where the model behaves well and where it is brittle.

---

## Limitations and Risks

This recommender has several limitations and risks:

- Small catalog risk: with only 18 songs, recommendations can repeat and may not reflect broad real-world tastes.
- Exact-label risk: genre and mood use exact text matching, so small wording changes (like `hip-hop` vs `hip hop`) can unfairly reduce score.
- Energy-dominance risk: high energy closeness can push songs upward even when other preferences are weak, which can cause repeated songs like **Gym Hero** to appear across multiple profiles.
- Cold-start/default risk: users with missing preferences are funneled into generic mid-energy recommendations rather than personalized results.
- Input robustness risk: invalid energy strings can crash scoring unless handled upstream.

Because of these limits, this model should be treated as a transparent classroom simulation, not a production recommendation system.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

