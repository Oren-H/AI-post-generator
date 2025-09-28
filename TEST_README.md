# Image Generation Testing

## Test Script: `test_image_generation.py`

This script demonstrates and tests both image generation styles used in the AI Post Generator:

### Styles Tested

1. **Original (Sundial) Style** - `image_generation.py`
   - Dark theme with golden accents
   - Sundial logo integration
   - DejaVu Serif font

2. **Free Press Style** - `fp_post_generation.py`
   - Light theme with red accents
   - Clean typography
   - Bold text effects

### Running the Test

```bash
# Make sure you're in the project directory
cd /Users/orenhartstein/AI-post-generator

# Run the test script
python test_image_generation.py

# Or run it directly (if executable)
./test_image_generation.py
```

### What the Test Does

1. **Quote Length Testing**: Tests quotes of varying lengths to verify text wrapping
2. **Byline Format Testing**: Tests different byline formats and attributions
3. **Style Comparison**: Generates the same content in both styles for comparison
4. **Error Handling**: Gracefully handles missing fonts or other issues

### Output

- Creates a `test_output/` directory
- Generates multiple PNG files showing both styles
- Prints detailed progress and comparison information

### Test Cases

The script includes:
- 5 different quotes (short, medium, long, famous, tech-focused)
- 5 different byline formats (simple name, with titles, professions, anonymous)
- Both styles for each test case
- Total of ~20 generated images

### Requirements

- PIL/Pillow for image generation
- Font files (falls back to system defaults if custom fonts unavailable)
- Python 3.6+
