# time-skewed-Fourier

An animated Fourier-style drawing tool built with Python and matplotlib. A chain of rotating arms traces a pattern over time; when the endpoint returns to its starting position, the completed pattern and its coordinates are saved to disk.

## How It Works

Each arm in the chain is described by one value from each array in `config.json`:

| Property  | Meaning                                                  |
| --------- | -------------------------------------------------------- |
| `angles`  | Starting angle of the arm, in degrees                    |
| `lengths` | Length of the arm                                        |
| `speeds`  | Degrees the arm rotates per frame; negative is clockwise |

On each animation frame, the script advances every arm by its speed, draws the connected arm chain in orange, and adds the chain endpoint to the black trail. When the endpoint reaches the trail's starting point again, the animation stops and writes the output files.

## Setup

Requires Python 3.8 or newer.

```bash
pip install -r requirements.txt
```

Create the output directory before running the animation:

```bash
mkdir output
```

`config.json` is intentionally **not** committed to this GitHub repository. Create it locally by running:

```bash
python random_val.py
```

This command creates `config.json` with the required structure and example random values.

## Running

Run the animation with the current configuration:

```bash
python fourier.py
```

Generate a new random configuration (or create `config.json` if it does not exist):

```bash
python random_val.py
```

`random_val.py` overwrites `config.json`, so save any configuration you want to keep before running it.

## Configuration

Edit `config.json` to change the animation. Each matching index across the three arrays describes one arm:

```json
{
  "angles":  [315, 160, 284],
  "lengths": [  1,   2, 1.1],
  "speeds":  [  0,  -1,   2]
}
```

- **Add an arm:** append one value to each array.
- **Remove an arm:** delete one matching value from each array.
- If the arrays have different lengths, the shortest array determines how many arms are used.

### Tips

- A `speed` of `0` keeps an arm stationary, acting as a fixed offset.
- Larger `lengths` make an arm contribute more strongly to the shape.
- Positive and negative speeds rotate in opposite directions and can create more complex patterns.
- Speeds with a shared factor usually close the loop sooner.

## Output

When the pattern completes a full cycle, two files are written to `output/`:

| File                        | Contents                                      |
| --------------------------- | --------------------------------------------- |
| `output/Ending_Pattern.png` | Screenshot of the completed pattern           |
| `output/pattern_points.txt` | Trail coordinates, one `x, y` pair per line   |

## Project Structure

```text
fourier.py        # Runs the animation and saves completed patterns
random_val.py     # Generates a random local config.json file
config.json       # Local editable arm configuration (not in the repo)
requirements.txt  # Python dependencies
output/           # Generated output files
```
