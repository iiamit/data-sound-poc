#!/usr/bin/env	python

import struct
import math
import os.path
import sys
import getopt

def to_sound(infile, outfile):
	sampleFreq = 8000
	denominator = 8
	frequencies = (262, 294, 330, 350, 392, 440, 494, 523, 587, 659, 698, 784, 880, 988, 1047, 1175)
	
	size = os.path.getsize(infile)
	
	fmt = FormatChunk()
	fmt.size = 0x10
	fmt.formatTag = 1
	fmt.channels = 1
	fmt.bitsPerSample = 16
	fmt.samplesPerSec = sampleFreq
	fmt.avgBytesPerSec = fmt.samplesPerSec * fmt.bitsPerSample / 8
	fmt.blockAlign = 4
	
	amplitude = 3000
	length = (3*denominator + size) * fmt.samplesPerSec  / denominator * fmt.channels * fmt.bitsPerSample / 8
	
	infh = open(infile, "rb")
	fh = open(outfile, "wb")
	
	format = GlobalFormat()
	format.size = length
	
	fh.write(format.as_bin())
	fh.write(fmt.as_bin())
	
	dataId = 0x61746164
	fh.write(struct.pack("I", dataId))
	
	dataLength = length - 12 - 16 - 12
	fh.write(struct.pack("I", dataLength))
	
	frequency = 440
	period = 2*math.pi/(fmt.samplesPerSec/float(frequency))
	samples = []
	for i in xrange(0, 3*fmt.samplesPerSec):
		sample = amplitude * (1 + math.sin(period*float(i)))
		samples.append(int(sample))
		fh.write(struct.pack("h", int(sample)))
		fh.flush()
		
	halfByteSampleLength = fmt.samplesPerSec / denominator
	
	j = 0
	while True:
		data = infh.read(1)
		if data == "":
			break
			
		(m,) = struct.unpack("B", data)
		
		a = m & 0xF
		b = m >> 4
	
		for halfbyte in (a,b):
			frequency = frequencies[halfbyte]
			period = 2*math.pi/(fmt.samplesPerSec/float(frequency))
			for i in xrange(0, halfByteSampleLength):
				sample = amplitude * (1 + math.sin(period*float(i)))
				fh.write(struct.pack("h", int(sample)))
				fh.flush()
			j += 1
			
	infh.close()
	fh.close()

class GlobalFormat(object):

	def __init__(self):
		self.id = 0x46464952 # RIFF
		self.size = 0
		self.type = 0x45564157 # WAVE
		
	def as_bin(self):
		return struct.pack("III", self.id, self.size, self.type)
		
class FormatChunk(object):

	def __init__(self):
		self.id = 0x20746d66
		self.size = 0
		self.formatTag = 0
		self.channels = 0
		self.bitsPerSample = 0
		self.samplesPerSec = 0
		self.avgBytesPerSec = 0
		self.blockAlign = 4
		
	def as_bin(self):
		return struct.pack("IIhHIIHH", self.id, self.size, self.formatTag, self.channels, \
			self.samplesPerSec, self.avgBytesPerSec, self.blockAlign, self.bitsPerSample)

def usage(argv0):
		print "usage: %s [-h] -i <input filename> -o <output filename>"
		
def main(argc, argv):
	
	try:
		
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:", ["help", "infile=", "outfile="])
		
	except getopt.GetoptError, err:
		
		usage(argv[0])
		print str(err)
		return 1
	
	infile = ""
	outfile = ""
	for o,a in opts:
		if o in ("-h", "--help"):
			usage(argv[0])
			return 1
		if o in ("-i", "--infile"):
			infile = a
		if o in ("-o", "--outfile"):
			outfile = a
	if (infile == "") or (outfile == ""):
		usage(argv[0])
		return 1
	else:
		to_sound(infile, outfile)
		
#

if (__name__ == "__main__"):
	sys.exit(main(len(sys.argv), sys.argv))