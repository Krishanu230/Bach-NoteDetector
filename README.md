# Bach-NoteDetector
Install the dependencies using:
`pip install -r requirements.txt`

Run it on wav files by providing the path of the audio file and the config:
`python bach.py -af=test/test1/melody-2.wav -c=mel2.config`

The image file contains detected note onsets vs loudness graph.
Inspired from: https://holometer.fnal.gov/GH_FFT.pdf
