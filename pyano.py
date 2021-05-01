import os
import configparser
from mido import MidiFile, tempo2bpm
from datetime import datetime

# Prepare input and output file path
def prepare_path(file_in):  
    # input and output folder
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    file_midi_read = file_dir +  "\\Input\\" + file_in
    file_output = file_dir + "\\Output\\" + "updated_" + file_in
    return (file_midi_read,file_output)

# Change velocity function
def change_note_velocity(file_name):
    file_in, file_out = prepare_path(file_name)
    midi_file = MidiFile(file_in)
    
    for i, track in enumerate(midi_file.tracks):
        for msg in track:
            if msg.type == "note_on":
                msg.velocity = 100
    midi_file.save(file_out)
    return

# Midi to text function
def midi_to_text(file_name):
    # Get path
    file_midi_read, file_output = prepare_path(file_name)

    # Get Date time for output file
    # now = datetime.now()
    # dt_string = now.strftime("%d%m%y_%H%M%S")

    file_text_output = file_output[:-4] + ".txt"

    output_text = ""
    midi_file = MidiFile(file_midi_read)
    for i,track in enumerate(midi_file.tracks):
        output_text += f"Track {i}: {track.name}\n"
        # print(f"Track {i}: {track.name}\n")
        for msg in track:
            output_text += str(msg) + "\n"
            # output_text += "Receive message type: " + msg.type + "\n"
            # if msg.type=="set_tempo":
            #     output_text += "tempo: " + str(tempo2bpm(msg.tempo)) + "\n"
            #     output_text += "type: " + str(msg.type) + "\n"
            # if msg.type=="note_on":
            #     output_text += "note on:" + str(msg.note)
            #     output_text += " velocity:" + str(msg.velocity) + "\n"
            # if msg.type=="note_off":
            #     output_text += "note off:" + str(msg.note) + "\n"

    f = open(file_text_output,"w")
    f.write(output_text)
    f.close()
    return

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    print(config['file']['input-file'])
    print(config['file']['output-folder'])
    # midi_to_text("MoonRiver-with sustain.mid")
    # midi_to_text("MoonRiver-without sustain.mid")
    # midi_to_text("updated_MoonRiver-with sustain.mid")
    # change_note_velocity("MoonRiver-with sustain.mid")
