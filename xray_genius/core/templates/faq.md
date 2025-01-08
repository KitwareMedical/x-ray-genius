# How to Use X-ray Genius

This document describes the user interface for the X-ray Genius application, with some example settings and tips for use. The current release illustrates the X-ray system as a standard fluoroscope, which is used in intraoperative and interventional procedures. However, the system can also be used to simulate standard clinical X-ray protocols, as described in the documentation.

Two sample CT datasets are provided in this demonstration version of the software. Note that these images are relatively low-resolution CTs, which may result in some aliasing artifacts in the simulated X-rays. Higher-resolution CTs will produce more detailed simulations and higher-quality results.

---

## 1. Rotation (Rainbow)

**Purpose:** Adjust the rotational orientation of the X-ray system around the subject.

### How to Use
- Use the dial to set the desired rotation angle, measured in degrees.
- Enable **'Add Rotation Randomization'** to introduce random variation within a defined range for generating variability in the view. Random values for this parameter will be chosen from a Gaussian distribution around the mean value specified by the dial and the standard deviation specified in the box.

### Example Use
- For **AP Pelvis views** (e.g., Test Protocol 1), set rotation to **0°** for a standard frontal view.
- Randomize with a standard deviation of **2.5°** to simulate a reasonable level of clinical variance, such as would typically be observed around a proscribed radiographic view.

---

## 2. Tilt (Head/Foot)

**Purpose:** Adjust the tilt angle of the X-ray system toward the subject’s head or feet.

### How to Use
- Use the dial to define the tilt angle in degrees.
- Enable **'Add Tilt Randomization'** to allow randomized tilt adjustments. Random values for this parameter will be chosen from a Gaussian distribution around the mean value specified by the dial and the standard deviation specified in the box.

### Example Use
- Set tilt to **13°** toward the head for moderate pelvic inlet views, such as would be used for planning and executing total hip replacement and other pelvic procedures.

---

## 3. Translation

### Push/Pull
**Purpose:** Adjust the X-ray position along one horizontal axis. For standard, unrotated clinical CT images, this parameter controls moving left and right in the patient coordinate space, where zero is at the center of the image coordinate system.

#### How to Use
- Set the value in **cm** to translate the X-ray source and detector away from the center of the image using the slider.
- Randomize the positional value by checking **"Randomize"** and specifying the standard deviation (in cm) around the specified value to introduce random variations in positioning.

#### Example Use
- In the **Hip CT dataset**, set Push/Pull to **0 cm** for AP Pelvis views to ensure both hip joints are within the field of view.

### Raise/Lower
**Purpose:** Adjust the vertical position of the X-ray system relative to the center of the CT image.

#### How to Use
- Set the value in **cm** to translate the X-ray source and detector away from the center of the image using the slider.
- Randomize the positional value by checking **"Randomize"** and specifying the standard deviation (in cm) around the specified value to introduce random variations in positioning.

#### Example Use
- In the **Hip CT sample dataset**, raise the system to **36.5 cm** for typical standing X-ray simulations.

### Foot/Head
**Purpose:** Translates the system along a second horizontal axis. For standard, unrotated clinical CT images, this axis corresponds to the longitudinal axis of the patient.

#### How to Use
- Set the value in **cm** to translate the X-ray source and detector away from the center of the image using the slider.
- Randomize the positional value by checking **"Randomize"** and specifying the standard deviation (in cm) around the specified value to introduce random variations in positioning.

#### Example Use
- For the **Hip CT sample dataset**, center the pelvis in the field of view by setting Foot/Head to **-8.4 cm**.

---

## 4. Number of Samples

**Purpose:** Specifies the number of images to generate when randomization is enabled.

### How to Use
- Enter the desired number of samples to generate in the input field. Higher sample counts (e.g., **10**) are used for variability analysis; a single sample (e.g., **1**) is used for precision tests.

### Example Use
- For edge case testing, set the number of samples to **10**, with the means and standard deviations of the imaging pose parameters set to values that capture normal variability expected for imaging.

---

## 5. Source-to-Detector Distance

**Purpose:** Defines the distance between the X-ray source and the detector.

### How to Use
- Input the desired distance in **millimeters (mm)**.
- Typical configurations include **1000 mm** for standard C-arm setups and larger values for orthographic projections.

### Example Use
- Adjust the distance to **500 mm** to simulate high parallax or **10000 mm** for near-orthographic views.

---

## 6. Detector Diameter

**Purpose:** Sets the diameter of the detector field of view.

### How to Use
- Input the detector diameter in **millimeters (mm)**. This demonstration version only supports square detectors. To simulate a rectangular detector geometry, specify the diameter as the larger of the two detector side lengths and crop the resulting image (cropping not supported in this application).
- Common fluoroscope detector sizes include:
  - **228.6 mm** (9-inch C-arm)
  - **304.8 mm** (12-inch C-arm)
  - General radiography commonly uses panel sizes such as **14 x 17 inches** and **17 x 17 inches** (431 mm x 431 mm).

### Example Use
- Use **228.6 mm** for lateral spine views common in surgeries such as spinal fusions and deformity corrections.
- Use a **431 mm** panel size for clinical X-ray applications such as spine, pelvis, chest, or abdominal imaging.
