# Types of CVD Simulator App

This Python script uses the daltonlens library to simulate different types of color vision deficiencies (CVD) on an input image. The app provides a user-friendly way to visualize how images appear to individuals with various forms of color blindness.

## Features

- Opens a file dialog for easy image selection
- Simulates three types of color vision deficiencies:
  - Protanopia (red-blind)
  - Deuteranopia (green-blind)
  - Tritanopia (blue-blind)
- Saves simulated images with timestamps
- Creates a grayscale version of the original image
- Utilizes the Brettel 1997 algorithm for simulation (easily changeable to other algorithms)

## Dependencies

- daltonlens
- PIL (Python Imaging Library)
- numpy
- tkinter

## Usage

1. Run the script
2. Select an image file through the opened file dialog
3. The script will process the image and save four new images:
   - Protanopia simulation
   - Deuteranopia simulation
   - Tritanopia simulation
   - Grayscale version of the original image

All output images are saved with a timestamp in the filename.

## Customization

The script currently uses the Brettel 1997 algorithm for CVD simulation. You can easily switch to other algorithms by uncommenting the desired simulator:

```python
# simulator = simulate.Simulator_Vienot1999()
# simulator = simulate.Simulator_Machado2009()
simulator = simulate.Simulator_Brettel1997()
# simulator = simulate.Simulator_Vischeck()
# simulator = simulate.Simulator_AutoSelect()
```

You can also adjust the severity of the color vision deficiency by changing the `severity` parameter (range 0.0 to 1.0):

```python
severity=0.8
```

## Output

The script generates four output images:
1. `protan_image_[timestamp].jpg`: Simulates protanopia
2. `deutan_image_[timestamp].jpg`: Simulates deuteranopia
3. `tritan_image_[timestamp].jpg`: Simulates tritanopia
4. `bw_image_[timestamp].jpg`: Grayscale version of the original image

## Note

This tool is intended for educational and design purposes. It provides an approximation of how images may appear to individuals with color vision deficiencies, but may not be 100% accurate for all individuals due to the varying nature of color blindness.
