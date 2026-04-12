# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

Answer:  
This recommender generates a ranked top-5 list of songs from a small catalog based on a user's preferred genre, preferred mood, and target energy level. It assumes users can express their taste with those three inputs and that exact labels are meaningful enough to compare. This project is for classroom exploration, not for deployment to real production users.

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

Answer:  
The model looks at each song's genre, mood, and energy, then compares those to the user's genre, mood, and energy target. Songs earn points for matching genre and mood, and they earn additional points when the song's energy is close to the user target. After every song gets a total score, the model sorts songs from highest to lowest and returns the top results with short reason text. Compared to the starter version, we implemented real scoring logic, ranking, and explanations instead of returning songs in original order.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

Answer:  
The catalog has 18 songs in `songs.csv`. It includes genres like pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip hop, classical, reggae, metal, folk, techno, r&b, and country, and moods such as happy, chill, intense, focused, reflective, aggressive, nostalgic, and more. For these experiments, we did not add or remove rows from the dataset. Because the catalog is small, it misses many parts of real music taste such as language preferences, niche subgenres, and context like activity or time of day.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

Answer:  
The recommender works best for users with clear, consistent preferences, like "High-Energy Pop" and "Chill Lofi." In those cases, the top songs usually align with both the requested mood and genre while staying close to the energy target. The scoring behavior is easy to understand because the explanation text shows which parts contributed points. During testing, those profiles produced top recommendations that matched intuition and felt musically coherent.

---

## 6. Limitations and Bias 

One weakness we found is that the recommender relies on exact text matches for genre and mood, so small wording differences can hurt results. For example, a user who enters "hip-hop" may miss genre match points because the dataset label is "hip hop." We also observed that when a user picks extreme or invalid energy values, the energy score often drops to zero and the model falls back to a narrow set of categorical matches. This can create a filter bubble where recommendations repeat similar labels rather than exploring musically similar songs across categories.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

Answer:  
I tested multiple profiles, including High-Energy Pop, Chill Lofi, Deep Intense Rock, Conflicting Pop Sad, Impossible Classical Aggressive, Mood Overpowers Genre, Genre Synonym Typo, Mood Synonym Mismatch, Empty Categorical, and Missing Fields. I looked for whether top songs matched the requested genre and mood, and whether energy closeness pushed songs up or down in expected ways. One surprise was how often songs like "Gym Hero" still appeared for users who asked for happy pop, because its very high energy score can keep it competitive even when mood does not match. Another surprise was that small wording differences like "hip-hop" versus "hip hop" changed results a lot because exact text matching removes genre points. I also compared empty or missing preferences to normal profiles and found that both defaulted to similar mid-energy recommendations.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Answer:  
The next improvement would be adding more user preferences, such as tempo range, acousticness preference, and whether the user wants familiar songs or discovery. I would also improve explanations by showing the top two or three reasons a song ranked highly in plain language and highlighting any tradeoff (for example, great energy match but mood mismatch). To reduce repetitive top results, I would add a small diversity rule so the top 5 is not dominated by near-duplicate vibes from one narrow slice of the catalog. For more complex tastes, I would support weighted preferences (like 70% chill and 30% energetic) and allow multiple moods or genres in one profile.

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

Answer:  
I learned that even a simple recommender can feel useful, but small design choices in scoring have a huge impact on who gets good recommendations. One unexpected discovery was how often songs like "Gym Hero" could still appear for profiles that did not fully match, mostly because strong energy alignment can keep a song competitive. This project changed how I think about music apps by showing that recommendations are not just about taste; they are also about how labels, defaults, and weighting decisions shape what users keep seeing. It also made me appreciate that transparent explanations are important so people can understand why a recommendation appeared.
