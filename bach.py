from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np
import sys

if(len(sys.argv) != 2):
    print("invalid input")
    exit(0)
else:
    fileName = str(sys.argv[1])
    
audio = AudioSegment.from_file(fileName)
audio = audio.high_pass_filter(100)
SEGMENT_MS = 50
volume = [segment.dBFS for segment in audio[::SEGMENT_MS]]

actual_notes = [1.3, 1.75, 2.06, 2.4, 2.755, 3.04, 4.2, 4.5, 4.9, 5.1, 5.4, 5.8, 6.9, 7.3, 7.6, 7.89, 8.2, 8.5, 8.9, 9.29, 9.76, 10.09, 10.4, 10.8, 10.9, 11.4, 11.7, 12.29]
print("Total Number of actual Notes: {:^5}".format(len(actual_notes)))
for s in actual_notes:
    plt.axvline(x=s, color='r', linewidth=0.5, linestyle="-")
x_axis = np.arange(len(volume)) * (SEGMENT_MS / 1000)
plt.plot(x_axis, volume)
plt.savefig("OnsetDetection-melody2")