# Preface

First dedicated project for a 2d emulation of laser light physics using mirrors and laser pointers

# Abilities

This project offers multiple realistic features like laser light reflection and color mixing. It can be used to simulate real-life scenarios with accuracy up to an angle of 0.1 degrees.

Due to the nature of this project, being coded heavily using OOP it allows for very easy extensibility and the addition of new features like refraction and lamps can easily be done (future plans)

# How to use

On running main.py you will be greeted with this screen <br/>
![start_screen](https://github.com/user-attachments/assets/41f722e9-abde-4944-ad97-62b6ff90c905)

The buttons on the bottom left are the available objects you can place on the screen. Pressing these buttons will create an object of that type on the screen. 
The buttons from left to right are:
- Pointer
- Poly Mirror
- Plane Mirror <br/>
![image](https://github.com/user-attachments/assets/a3efb587-6be5-4d31-854b-4ebc27768c71)

In this case, I created a pointer and a mirror on the screen. <br/>
![image](https://github.com/user-attachments/assets/16128985-5c18-476c-9f40-15f603250f3e)

## Selecting Objects

To select an object, hold down the select_object key `default: S` and left-click on an object, This will select the object and create a white outline around it. This means that you can now change the position and behavior of this object.
Clicking again while pressing the select_object key will deselect the currently selected object.

![image](https://github.com/user-attachments/assets/3d3783ad-f725-4687-a07f-b3559ca1a99d)

While an object is selected, 3 textboxes with info about the objects will be shown on the top left of the screen.

![image](https://github.com/user-attachments/assets/c4942aca-7ffa-41d1-b468-c4050c450dd0)

To precisely set the position or rotation of the selected objects, type in a value in these textboxes and hit `Enter`, this will change the object's state.

## Transforming Objects

To transform an object, select an object and then hold down the transform_object key `default: T` and do the following:
* Moving an object <br/>
    Left-click anywhere on the screen and the selected object will be moved to the current position of the mouse pointer.
    Holding down the left-click will make the selected object follow the mouse pointer as it moves.
* Rotating an object <br/>
    Use the right and left arrow keys to rotate the selected object.
* Enlarging or shrinking an object <br/>
    Use the up and down arrow keys to rotate the selected objects.

![image](https://github.com/user-attachments/assets/98d8deb8-9809-4f0c-bc3b-f348ecf3f3ab)

## Custom options for objects

To view the custom options for an object, select the object, hold down the custom_object key `default: C`, and do the following:

* Pointers <br/>
    A slider will appear on the right side of the screen. Clicking on the slider will select the corresponding color.
    Clicking and dragging on the slider will allow for a precise selection of colors.

    The color determines the color of the selected laser pointer. <br/>

    ![image](https://github.com/user-attachments/assets/ef208699-e5a6-4d97-a1a0-6876dedeec73)


* Poly Mirror <br/>
    Blue buttons will be visible, which you can click and drag to move the respective vertices around.
    Right-clicking on the screen will create a new vertice on the nearest edge to the mouse pointer on the selected polygon.

    The red dot represents the anchor of the shape, around which the shape will be rotated and moved. <br/>
    
    ![image](https://github.com/user-attachments/assets/371256df-90bb-4b69-9624-2032b01ea8cb)


## Running the simulation

Pressing the green play button at the bottom right will simulate the build, and you can view how the setup works. <br/>

![image](https://github.com/user-attachments/assets/ab11622b-9789-44a5-85d9-71f8826f9972)

The light button on the top right determines whether the 'shaders' are toggled on or off, pressing this button will toggle the 'shader' feature (Bloom).

The pause button on the bottom right will open the build screen.

## Saving the build

Pressing the `escape` key will open the options menu with the following options. <br/>

![image](https://github.com/user-attachments/assets/636f832f-d535-47a5-862d-63957cca036c)

The button next to the "SAVES" button saves the current build.

Pressing the "BACK" option will return you to the build.

## Manipulating saves

Pressing the "SAVES" option will open the saves screen where each available save will be listed. <br/>

![image](https://github.com/user-attachments/assets/adafa3ef-dfea-48b2-90af-5b5f64e41f81)

Clicking on the name of the save will open the corresponding save, and clicking on the dustbin button will delete the corresponding save.

To create a new save, enter the name of the desired save into the textbox (only alphanumerics and _ ) and press the '+' button

# Closing Notes

This project can be used for solving physics problems based on reflection of light or just to mess around with. This was just a fun project I decided to work on.
Any bug reports or suggestions are welcome.
