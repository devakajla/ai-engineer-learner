# Video map review

Timestamps come from auto-captions (Hindi), so they are **approximate (±1 min)**. Check each segment once and fix `videos.yaml` if it starts or ends in the wrong place. Playlist: DSA Patterns (126 videos). Skipped: roadmap, vlog and announcement videos.

## 13-complexity-and-patterns
- Intro: Ep 6 `oFwHwCkSoGw` (whole video, Big-O).

## 14-two-pointers
| Exercise | Video | Range | Check |
| --- | --- | --- | --- |
| intro | Ep 3 `Fu7LD_mIo00` | 0:00–14:00 | pattern + flow chart |
| 01, 02 Two Sum | Ep 3 | 15:00–47:30 | brute -> hashmap -> two pointers |
| 03 Remove duplicates | Ep 4 `PvyEr3CeKzE` | 3:00–end | |
| 04 Merge sorted | Ep 5 `nPdxCoVHC90` | 9:00–24:30 | merge is taught as a step of squares |
| 05 Squares | Ep 5 | 2:30–end | includes the merge part |
| 06 3Sum | Ep 7 `rM9EthMlXnw` | 2:00–33:30 | |
| 07 3Sum closest | Ep 7 | 33:30–end | |
| 08 Triplet sum smaller | Ep 8 `ljJJcYql6Bc` | 4:00–17:30 | |
| 09 Sort colors | Ep 8 | 18:00–end | |
Revision: Ep 9 `n7v0SokbF4I` (linked in lesson Summary).
Not used (no exercise yet): own exercises 10–18 have no video.

## 15 Sliding window (approximate, verify)

- Ep 11 `DL8LSXUsfWE`: max sum of size k about 2:00-42:00; smallest subarray with sum >= target about 42:00-end.
- Ep 12 `v4pIgiBQMh8`: the split between k-distinct (5:00-40:00), fruit baskets (40:00-50:00) and no-repeat (50:00-end) is a guess from sparse captions.
- Ep 13 `2HZ12B2ZPAQ`: whole video used for character replacement; the description mentions two questions, the captions show one.
- Ep 16 `9wc8HZH_sh4`: whole video is minimum window substring.

## Lessons 17 to 21: guessed splits (please verify)

- 17 hashmap: Ep 42 split into 4 parts (120-900, 900-2100, 2100-2940, 2940-3962) is a guess.
- 18 stack: Ep 39 split into 3 parts (120-900, 900-1900, 1900-3447) is a guess.
- 19 kadane: Ep 22 (300-1500, 1500-2180) and Ep 24 (1800-2294) are guesses.
- 20 intervals: intro uses Ep 31 0-1500, exercise 01 uses 1500-2889. Eps 32 to 35 are mapped to one problem each from captions; Ep 33 (intersection) and Ep 34 (meeting rooms I) are inferred.
- 21 binary search: Ep 48 split at 1500 (01 vs 02) and Ep 56 split at 2900 (10 vs 11) are guesses. Eps 49 to 55 are mapped whole-video to one problem each.

## Lessons 23 to 29 (Level 4): lower confidence

Level 4 video mapping used video titles, descriptions and a few caption skims. It did **not** use full transcripts like Level 3. Most segments cover a whole video (`start: 0`, `end: full length`). Some videos teach several problems (for example Ep 90 DFS and BFS, Ep 93 cycle detection, Ep 94 topological sort used for two exercises), and the split points were guessed. Please open each video once and tighten `start` and `end` in `videos.yaml`.

Not mapped (no video, own problems): lesson 30 (checkpoint), lesson 29 exercises 03 to 06, 09 to 11, 14 and the greedy exercises that are not in Ep 122 (Ep 122 is used as a whole video for 01 and 02). Lesson 28 exercises 12 to 16 have no video. Lesson 27 exercises 04, 05, 07, 12 to 17 have no video.
