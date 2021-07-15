import os
import configparser
import random
import glob
from types import new_class
from mido.midifiles.midifiles import print_byte
import numpy
from mido import MidiFile

from mido.messages.messages import Message
from mido.midifiles.meta import MetaMessage
from mido.midifiles.tracks import MidiTrack

class Pyano:
    def __init__(self, midi_file: MidiFile, min=70, max=110, range=10):
        self.midi_file = midi_file
        self.file_name = os.path.basename(midi_file.filename)
        self.min = min
        self.max = max
        self.range = range
        self.output_text = ""
        self.bassline_midi = MidiFile(ticks_per_beat=midi_file.ticks_per_beat)
        self.intervals = []
        self.time_pass = 0
        self.initialize = 1

    def prepare_internal_midi_info(self):
        if self.initialize == 1:
            # Initialize data
            # list of intervals
            # time of midi file
            # list of note, separate to each bars
            time_pass = 0
            time_pass_singature = 0
            #[timestamp, interval]
            measure_intervals = []

            # Trace the midi to find the information of midi length and beat
            for track in self.midi_file.tracks:
                if time_pass == 0:
                    for msg in track:
                        if msg.type == "time_signature":
                            time_pass_singature += msg.time
                            measure_interval = {"time": time_pass_singature, "interval":self.midi_file.ticks_per_beat * msg.numerator}
                            self.intervals.append(measure_interval)
                        if msg.type == "note_on" or msg.type == "note_off" \
                                or msg.type == "control_change":
                            time_pass += msg.time

            self.time_pass = time_pass
            self.initialize = 0

    # Correct velocity function
    def correct_velocity(self):
        for i, track in enumerate(self.midi_file.tracks):
            for msg in track:
                if msg.type == "note_on":
                    calculatedVelocity = int(msg.velocity + self.range * random.uniform(-1,1))
                    if calculatedVelocity > self.max:
                        msg.velocity = self.max
                    elif calculatedVelocity < self.min:
                        msg.velocity = self.min
                    else:
                        msg.velocity = calculatedVelocity

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
        pedal_track = MidiTrack()
        pedal_track.name = "pedal"
        time_pass_pedal = 0

        self.prepare_internal_midi_info()

        pedal_msg_on = Message("control_change", 
                        channel = 2, control = 64, 
                        value = 100, time = 0)
        pedal_track.append(pedal_msg_on)

        interval_index = 0
        while time_pass_pedal <= self.time_pass - self.intervals[interval_index]["interval"]:
            if interval_index < len(self.intervals) - 1:
                if time_pass_pedal == self.intervals[interval_index + 1]["time"]:
                    interval_index = interval_index + 1 

            # Add pedal off and pedal all before and after this note
            pedal_msg_off = Message("control_change", 
                                    channel = 2, control = 64, 
                                    value = 0, time = self.intervals[interval_index]["interval"]-1)
            pedal_msg_on = Message("control_change", 
                                    channel = 2, control = 64, 
                                    value = 100, time = 1)

            pedal_track.append(pedal_msg_off)
            pedal_track.append(pedal_msg_on)
            
            time_pass_pedal += self.intervals[interval_index]["interval"]

        # Off pedal at the end of the song
        pedal_msg_off = Message("control_change", 
                        channel = 2, control = 64, 
                        value = 0, time = self.intervals[interval_index]["interval"] - 1)
        pedal_track.append(pedal_msg_off)

        eot = MetaMessage('end_of_track', time=0)
        pedal_track.append(eot)
        self.midi_file.tracks.append(pedal_track)

    # simplify the left hand to only press the chord
    def simplify_left_hand(self):
        pass

    # Create bassline
    def export_bassline(self):
        # Copy information from midi file to bass midi
        meta_track = MidiTrack()
        self.prepare_internal_midi_info()
        current_time = 0
        
        # The first track contain the midi information
        for msg in self.midi_file.tracks[0]:
            meta_track.append(msg)        
        self.bassline_midi.tracks.append(meta_track)

        # The bassline base on track 1
        current_interval = 0
        interval_index = 0
        note_list = []
        note_interval = {"notes":[], "interval":0}
        for msg in self.midi_file.tracks[1]:
            # Add bassline here
            if interval_index < len(self.intervals) - 1:
                if current_time == self.intervals[interval_index + 1]["time"]:
                    interval_index = interval_index + 1
            
            if current_interval < self.intervals[interval_index]["interval"]:
                if msg.type == "note_on":
                    note_interval["notes"].append(msg.note)
                    note_interval["interval"] = self.intervals[interval_index]["interval"]
            else:
                note_list.append(note_interval.copy())
                note_interval["notes"] = []
                current_interval = 0

            current_interval += msg.time
            current_time += msg.time 
        
        # Find min of note to make the bass for each measure
        # bass_list  data is {bass note, interval of that note}
        bass_list = []
        for notes in note_list:
            # print(notes)
            if len(notes["notes"]) > 0:
                bass_list.append(
                    {"note":numpy.min(notes["notes"]),
                    "interval":notes["interval"]})
            else:
                # the value -1 is empty note
                # This mean this measure do not have any bass note
                bass_list.append(
                    {"note":-1,
                    "interval":notes["interval"]})
        
        # add the bass_list to midi
        bass_track = MidiTrack()

        bass_interval = 0
        for i,note in enumerate(bass_list):
            if note["note"] == -1:
                bass_interval += note["interval"]
                if i == len(bass_list) - 1:
                    msg_off = Message("note_off", channel = 0, note=note["note"], velocity=64, time=bass_interval)
            else:
                bass_interval = note["interval"]
                msg_on = Message("note_on", channel = 0, note=note["note"], velocity=64, time=0)
                if i < len(bass_list) - 1 and bass_list[i + 1]["note"] != -1:
                    msg_off = Message("note_off", channel = 0, note=note["note"], velocity=64, time=bass_interval)
            bass_track.append(msg_on)
            bass_track.append(msg_off)
        self.bassline_midi.tracks.append(bass_track)   
        
    # Generate the file base on name of input_file and output_folder
    def write_output_midi(self, output_folder, file_name, midi_file):
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        file_output = output_folder + file_name
        midi_file.save(file_output)

    
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
    input_folder = config['file']['input-folder']
    output_folder = config['file']['output-folder']
    min = int(config['threshold']['min'])
    max = int(config['threshold']['max']) 
    random_range = int(config['threshold']['random-range'])

    for input_file in glob.glob(input_folder + "/*.mid"):
        midi_file = MidiFile(input_file)
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

        if config['feature'].getboolean('export-bassline'):
            pyano.export_bassline()
            pyano.write_output_midi(output_folder, "Bass_" + pyano.file_name, pyano.bassline_midi)
        
        if to_write_midi:
            pyano.write_output_midi(output_folder, "Enhance_" + pyano.file_name, pyano.midi_file)