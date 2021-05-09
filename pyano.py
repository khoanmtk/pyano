import os
import configparser
from mido import MidiFile, tempo2bpm
from datetime import datetime

class Pyano:
    def __init__(self, midi_file, file_name = 'file', min=70, max=110, range=10):
        self.midi_file = midi_file
        self.file_name = os.path.basename(midi_file.filename)
        self.min = min
        self.max = max
        self.range = range
        self.output_text = ""
        #midi_file = MidiFile(file_name

    # Correct velocity function
    def correct_velocity(self):
        for i, track in enumerate(midi_file.tracks):
            for msg in track:
                if msg.type == "note_on":
                    msg.velocity = 100

    # Midi to text function
    def midi_to_text(self):
        # Get path
        midi_file = MidiFile(input_file)

        for i,track in enumerate(midi_file.tracks):
            self.output_text += f"Track {i}: {track.name}\n"
            # print(f"Track {i}: {track.name}\n")
            for msg in track:
                self.output_text += str(msg) + "\n"
    
    # Add pedal to the midi file
    def add_pedal(self):
        pass

    # simplify the left hand to only press the chord
    def simplify_left_hand(self):
        pass
        
    # Generate the file base on name of input_file and output_folder
    def write_output_midi(self, output_folder):
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        file_output = output_folder + 'enhanced_' + self.file_name

        f = open(file_output,"w")
        f.write(self.output_text)
        f.close()
    
    def write_output_text(self, output_folder):
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        file_output = output_folder + self.file_name.replace('.mid', '.txt')
        self.midi_file.save(file_output)

# main call
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    input_file = config['file']['input-file']
    output_folder = config['file']['output-folder']
    midi_file = MidiFile(input_file)
    min = config['threshold']['min']
    max = config['threshold']['max']
    random_range = config['threshold']['random-range']
    to_write_midi = False

    pyano = Pyano(midi_file, min, max, random_range)

    if config['feature'].getboolean('midi-to-text'):
        pyano.midi_to_text()
        pyano.write_output_text(output_folder)
    
    if config['feature'].getboolean('add-pedal'):
        to_write_midi = True

    if config['feature'].getboolean('simplify-left-hand'):
        to_write_midi = True

    if config['feature'].getboolean('apply-threshold'):
        to_write_midi = True
        pyano.correct_velocity()
    
    if to_write_midi:
        pyano.write_output_midi(output_folder)
    