from daltonlens import simulate
import PIL
from PIL import Image
import numpy as np
from tkinter import Tk, filedialog
import datetime

# Create a Tkinter root window
root = Tk()
root.withdraw()

# Open a file dialog to choose an image
image_path = filedialog.askopenfilename()

# Open the image and convert it to RGB
original_image = Image.open(image_path).convert('RGB')
im = np.asarray(original_image)

# Create a simulator using the Viénot 1999 algorithm.
# simulator = simulate.Simulator_Vienot1999()

# Create a simulator using the Machado 2009 algorithm.
# simulator = simulate.Simulator_Machado2009()

# Create a simulator using the Brettel 1997 algorithm.
simulator = simulate.Simulator_Brettel1997()

# Create a simulator using the Vischeck algorithm.
# simulator = simulate.Simulator_Vischeck()

# Automatically selects the best algorithm for the given deficiency and severity.
# simulator = simulate.Simulator_AutoSelect()

# Apply the simulator to the input image to get simulations of different types of CVD
protan_im = simulator.simulate_cvd(im, simulate.Deficiency.PROTAN, severity=0.8)
deutan_im = simulator.simulate_cvd(im, simulate.Deficiency.DEUTAN, severity=0.8)
tritan_im = simulator.simulate_cvd(im, simulate.Deficiency.TRITAN, severity=0.8)

# Convert the numpy array back to a PIL Image object for each simulation
protan_im = Image.fromarray(protan_im)
deutan_im = Image.fromarray(deutan_im)
tritan_im = Image.fromarray(tritan_im)

# Get the current date and time
current_datetime = datetime.datetime.now()
datetime_string = current_datetime.strftime("%Y%m%d_%H%M%S")

# Save the simulated images
protan_im.save(f"protan_image_{datetime_string}.jpg")
deutan_im.save(f"deutan_image_{datetime_string}.jpg")
tritan_im.save(f"tritan_image_{datetime_string}.jpg")

# Convert the original image to grayscale and save it
bw_original = original_image.convert('L')
bw_original.save(f"bw_image_{datetime_string}.jpg")
