from pydub import AudioSegment
import matplotlib.pyplot as plt
import numpy as np
import sys
from scipy.io.wavfile import read
import argparse
import configparser

parser = argparse.ArgumentParser()
config = configparser.ConfigParser()
parser.add_argument("-af", "--audioFile", help="Audio File Path")
parser.add_argument("-c", "--config", help="the path of the config file")
args = parser.parse_args()
fileName = args.audioFile
config.read(args.config)
c = config['DEFAULT']

#tweakable parameters
MIN_VOL = float(c.get('MIN_VOL', -30))  #minimum volume for loudness detection in dBFS
MIN_DEL = float(c.get('MIN_DEL', 1.5)) #minimum delta in volume value to count as a peak wrt prev block
MIN_GAP_MS = int(c.get('MIN_GAP_MS', 200))  #after detecting a peak, ignore any fluctuation in this gap window.
SEGMENT_MS = int(c.get('SEGMENT_MS', 50))   #discretize the audio in blocks to calculate volume per block, in ms.

MIN_FREQ_NUMBER = int(c.get('MIN_FREQ_NUMBER', 21)) #default:A0
MAX_FREQ_NUMBER = int(c.get('MAX_FREQ_NUMBER', 108)) #default:C8
NOTE_NAMES = 'C C# D D# E F F# G G# A A# B'.split()

#Inspired From: https://newt.phys.unsw.edu.au/jw/notes.html
def freq_to_number(f): return 69 + 12*np.log2(f/440.0)
def number_to_freq(n): return 440 * 2.0**((n-69)/12.0)
def note_name(n): return NOTE_NAMES[n % 12] + str(int(n/12 - 1))


#def note_to_fftbin(n): return number_to_freq(n)/FREQ_STEP
#imin = max(0, int(np.floor(note_to_fftbin(NOTE_MIN-1))))
#imax = min(SAMPLES_PER_FFT, int(np.ceil(note_to_fftbin(NOTE_MAX+1))))

#find onset by finding peaks in volume of the sample
#Could be improved my more noise reduction and curve smoothening
#But the fundamental problem is it will not detect all peaks.
#We can tune the variables like MIN_GAP_MS etc for a particular
#recording but it will fail to give all peaks.
#TODO: implement a better way of finding note onset by using
#fft to find peaks in the frequency domain not time.
def findOnsetByVolume(volume):
    onsets = []
    for i in range(1, len(volume)):
        if (volume[i] > MIN_VOL and (volume[i] - volume[i - 1]) > MIN_DEL):
            ms = i * SEGMENT_MS
            #ignore any peaks within the minimum gap window after one confirmed peak.
            if (len(onsets) == 0 or ms - onsets[len(onsets)-1] >= MIN_GAP_MS):
                onsets.append(ms)
    return onsets

def identifyNote(audioFrame, sampleRate):
    frameSize = len(audioFrame)
    framesPerFFT = 1   #number of frames to take avg in fft
    samplesPerFFT = frameSize*framesPerFFT
    freqStep = float(sampleRate)/samplesPerFFT

    imin = max(0, int(np.floor(number_to_freq(MIN_FREQ_NUMBER-1)/freqStep)))
    imax = min(samplesPerFFT, int(np.ceil(number_to_freq(MAX_FREQ_NUMBER+1)/freqStep)))

    hanningWindow = 0.5 * (1 - np.cos(np.linspace(0, 2*np.pi, samplesPerFFT, False)))
    buf = np.zeros(samplesPerFFT, dtype=np.float32)
    buf[-frameSize:] = audioFrame

    #FFT the the windowed buffer
    fft = np.fft.rfft(buf * hanningWindow)

    # Get frequency of maximum response in range
    freq = (np.abs(fft[imin:imax]).argmax() + imin) * freqStep

    # Get note number and nearest note
    n = freq_to_number(freq)
    n0 = int(round(n))
    return freq, n0

def main():
    audio = AudioSegment.from_file(fileName)
    audio = audio.high_pass_filter(100)
    volume = [segment.dBFS for segment in audio[::SEGMENT_MS]]
    onsets = findOnsetByVolume(volume)
    #actual_notes = [1.3, 1.75, 2.06, 2.4, 2.755, 3.04, 4.2, 4.5, 4.9, 5.1, 5.4, 5.8, 6.9, 7.3, 7.6, 7.89, 8.2, 8.5, 8.9, 9.29, 9.76, 10.09, 10.4, 10.8, 10.9, 11.4, 11.7, 12.29]
    print("Total Number of detected Notes: {:^5}".format(len(onsets)))
    print(onsets)
    sampleRate, audio = read(fileName)
    audio = audio[:, 0]
    length = audio.shape[0] / sampleRate
    notes = []
    for i in range(len(onsets)):
        start = int(onsets[i]*(sampleRate/1000))
        if (i==(len(onsets)-1)):
            end = len(audio)-1
        else:
            end = int(onsets[i+1]*(sampleRate/1000))
        fs = end-start
        audioFrame = audio[start:start+fs]
        f, n = identifyNote(audioFrame, sampleRate)
        notes.append(note_name(n))
        #print("i: {:^4} freq: {:>5} num: {:>5}".format(i,f, note_name(n)))

    print(notes)
    #for s in actual_notes:
        #plt.axvline(x=s, color='r', linewidth=0.5, linestyle="-")
    for ms in onsets:
        plt.axvline(x=(ms/1000), color='r', linewidth=0.5, linestyle="-")
    x_axis = np.arange(len(volume)) * (SEGMENT_MS / 1000)
    plt.plot(x_axis, volume)
    plt.grid(True)
    plt.show()
    #plt.savefig("OnsetDetection")

if __name__ == "__main__":
    main()
