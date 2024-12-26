# Launchpad_Mini_X

## Description
Launchpad_Mini_X is an Ableton MIDI Remote Script to enhance the functionality of the Launchpad Mini MK3 by implementing Session and Mixer modes similar to those found on the Launchpad X. 

This script allows the Session button to toggle between Session and Mixer modes. In Mixer Mode, the Scene Launch buttons control Ableton Live mixer functions: Volume, Pan, Send A, Send B, Stop Clip, Mute, Solo, and Record Arm (from top to bottom).

For more information on how the Mixer mode works, refer to the [Launchpad X manual](https://downloads.novationmusic.com/novation/launchpad-mk3/launchpad-x)

## Compatibility
This script works with **Ableton Live 12** and the **Launchpad Mini MK3 2.0.1 firmware**.

_Note: The script may work with different versions, but compatibility beyond the specified versions is not guaranteed or supported._

## Installation
Clone this repo or download the files and copy them into a subdirectory named 'Launchpad_Mini_X' within your Ableton MIDI Remote Scripts directory. For the correct directory location, refer this Ableton's [article](https://help.ableton.com/hc/en-us/articles/209072009-Installing-third-party-remote-scripts)

Example path: `\<Ableton's Midi Remote Scripts Directory>\Launchpad_Mini_X`

After installation, 'Launchpad Mini X' will appear in Ableton's MIDI settings as a new control surface. Configure other settings (Input, Output, I/O Ports) according to Novation's setup guide.

## Usage
- Use the Session button to switch between Session and Mixer modes. 
- In Mixer mode, use the Scene Launch buttons to access Volume, Pan, Send A, Send B, Stop Clip, Mute, Solo, and Record Arm for your session view.

## Known Issues
I found that the current Launchpad Mini MK3 firmware (2.0.1) has a bug related to MIDI channels used for receiving color/position data from the DAW. I reported the issue to Novation and may be resolved in a future firmware update. Note that a firmware fix could potentially break this script, and will need an update.

## Support
While active development is not planned beyond personal use, suggestions and comments are welcome.

## Authors and acknowledgment
I based this script on decompiled versions of Ableton's scripts for the Launchpad Mini MK3 and X.

Special thanks to Julien Bayle for decompiling and sharing Ableton's scripts on [GitHub](https://github.com/gluon/) (it was a nice shortcut).

## License
This project is not licensed.