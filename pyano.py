import os
import configparser
import random
from mido import MidiFile
from datetime import datetime

from mido.messages.messages import Message
from mido.midifiles.meta import MetaMessage
from mido.midifiles.tracks import MidiTrack

class Pyano:
    def __init__(self, midi_file, file_name = 'file', min=70, max=110, range=10):
        self.midi_file = midi_file
        self.file_name = os.path.basename(midi_file.filename)
        self.min = min
        self.max = max
        self.range = range
        self.output_text = ""

    # Correct velocity function
    def correct_velocity(self):
        for i, track in enumerate(midi_file.tracks):
            for msg in track:
                if msg.type == "note_on":
                    msg.velocity = int(msg.velocity + self.range * random.uniform(-1,1))
                    if msg.velocity > self.max:
                        msg.velocity = self.max
                    if msg.velocity < self.min:
                        msg.velocity = self.min

    # Midi to text function
    def midi_to_text(self):
        # Get path
        for i,track in enumerate(self.midi_file.tracks):
            self.output_text += f"Track {i}: {track.name}\n"
            # print(f"Track {i}: {track.name}\n")
            for msg in track:
                self.output_text += str(msg) + "\n"
    
    # Add pedal to the midi file
    def add_pedal(self):
        # calculate time pass in midi
        time_pass = 0
        beat_per_bar = 0
        pedal_track = MidiTrack()
        pedal_track.name = "pedal"

        # Trace the midi to find the information of midi length and beat
        for track in self.midi_file.tracks:
            if time_pass == 0:
                for msg in track:
                    if msg.type == "time_signature":
                        beat_per_bar = msg.numerator
                    if msg.type == "note_on" or msg.type == "note_off" \
                            or msg.type == "control_change":
                        time_pass += msg.time
        
        # Add pedal with interval to new track.
        time_pass_pedal = 0
        interval = self.midi_file.ticks_per_beat * beat_per_bar
        while time_pass_pedal < time_pass:
            # Add pedal off and pedal all before and after this note
            pedal_msg_off = Message("control_change", 
                                    channel = 2, control = 64, 
                                    value = 0, time = interval-1)
            pedal_msg_on = Message("control_change", 
                                    channel = 2, control = 64, 
                                    value = 100, time = 1)

            pedal_track.append(pedal_msg_off)
            pedal_track.append(pedal_msg_on)
            time_pass_pedal += interval
        eot = MetaMessage('end_of_track', time=0)
        pedal_track.append(eot)
        self.midi_file.tracks.append(pedal_track)

    # simplify the left hand to only press the chord
    def simplify_left_hand(self):
        pass
        
    # Generate the file base on name of input_file and output_folder
    def write_output_midi(self, output_folder):
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        file_output = output_folder + "enhanced_" + self.file_name
        self.midi_file.save(file_output)

    
    def write_output_text(self, output_folder):
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        file_output = output_folder + self.file_name.replace(".mid", ".txt")

        f = open(file_output,"w")
        f.write(self.output_text)
        f.close()

# main call
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    input_file = config['file']['input-file']
    output_folder = config['file']['output-folder']
    midi_file = MidiFile(input_file)
    min = int(config['threshold']['min'])
    max = int(config['threshold']['max'])
    random_range = int(config['threshold']['random-range'])
    to_write_midi = False

    pyano = Pyano(midi_file, min, max, random_range)
    
    if config['feature'].getboolean('add-pedal'):
        pyano.add_pedal()
        to_write_midi = True

    if config['feature'].getboolean('simplify-left-hand'):
        to_write_midi = True

    if config['feature'].getboolean('apply-threshold'):
        to_write_midi = True
        pyano.correct_velocity()

    if config['feature'].getboolean('midi-to-text'):
        pyano.midi_to_text()
        pyano.write_output_text(output_folder)
    
    if to_write_midi:
        pyano.write_output_midi(output_folder)