from music21 import *

s = stream.Stream()
s.append(meter.TimeSignature('3/4'))
s.append(note.Note('C4'))
s.append(note.Note('E4'))
s.append(note.Note('G4'))
s.show()