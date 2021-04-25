import os
from mido import MidiFile, tempo2bpm
from datetime import datetime

def change_note_velocity(midi_file):
    print("change velocity done")


def midi_to_text(file_name):
    # Input the file name, then use it to parse to text file
    # file_midi_read = input("Enter midi file name: ")
    file_midi_read = file_name
    if file_midi_read.find(".mid") == -1:
        file_midi_read = file_midi_read + ".mid"

    # Get Date time for output file
    now = datetime.now()
    dt_string = now.strftime("%d%m%y_%H%M%S")
    file_text_output = "MidiToText" + dt_string + ".txt"
    print(file_text_output)

    # Add path to file_midi_read,file_text_output
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    file_midi_read = file_dir +  "\\Input\\" + file_midi_read
    file_text_output = file_dir + "\\Output\\" + file_text_output

    output_text = ""
    midi_file = MidiFile(file_midi_read)
    for i,track in enumerate(midi_file.tracks):
        output_text += f"Track {i}: {track.name}\n")
        print(f"Track {i}: {track.name}\n")
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
    midi_to_text("loanhquanh.mid")