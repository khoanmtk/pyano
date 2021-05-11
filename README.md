# pyano

Humanize the MIDI sound, then we could input it to DAW and create realistic piano sound

How the tool make MIDI sound better ?
1. It add sustain pedal to each bar of the song.
2. It make the velocity of note not too high or not too low
3. It randomize the velocity to same as human

Todo:
- Add simplify left hand feature, change the lefthand arpeggio to:
  - Only press chord for each bar.
  - Or some common arpeggio pattern.
  > Purpose of this feature is create the simpler piano arrangment for someone.

## Getting Started

### 1. Install Dependencies

This tool use mido to handle with midi file
If you have not install mido then you need to call this command to install mido
```
pip install mido
``` 

### 2. Update setting file

Need to edit the config.ini and control the tool
```
  [file]
  input-file: put the midi file path here
  output-folder: put output folder here

  [threshold]
  min: the mimimum velocity
  max: the maximum velocity
  random-range: the random range when randomize the velocity

  [feature]
  add-pedal: yes or no to add pedal
  simplify-left-hand: yes or no to change the left hand to only play chord
  apply-threshold: yes or no to edit velocity
  midi-to-text: yes or no to output the txt information of the midi file
```

### 3. Run the tool

```
python pyano.py
``` 