#!/usr/bin/env	python

import struct
import math
import os.path
import numpy.numarray
import numpy.fft
import getopt
import sys

def read_and_unpack(fh, format):
	size = struct.calcsize(format)
	return struct.unpack(format, fh.read(size))
	
def get_maxfrequency(samples, norm, maxAcceptable = 1200):
	samplesArr = numpy.numarray.array(samples)
	transformedSamples = numpy.fft.fft(samplesArr)
	
	maxFreq = 0
	maxI = 0
	for i, freq in enumerate(transformedSamples):
		j = int(norm * i)
		a = math.sqrt(freq.real**2 + freq.imag**2)
		if a > maxFreq and i > 0 and j < maxAcceptable:
			maxFreq = a
			maxI = j
			
	return maxI
	
def get_closest_index(frequencies, freq):
	minDist = ()
	minI = -1
	for i, cmp in enumerate(frequencies):
		dist = abs(freq - cmp)
		if dist < minDist:
			minDist = dist
			minI = i
	return minI

def to_data(infile, outfile):
	#filename = "message.wav"
	sourceSampleFreq = 8000
	denominator = 8
	frequencies = (262, 294, 330, 350, 392, 440, 494, 523, 587, 659, 698, 784, 880, 988, 1047, 1175)
	
	fh = open(infile, "rb") # infile was filename
	
	(id, size, type) = read_and_unpack(fh, "III")
	
	(id, size, formatTag, channels, samplesPerSec, \
	bytesPerSec, blockAlign, bitsPerSample) = read_and_unpack(fh, "IIhHIIHH")
	
	# skip data chunk header
	fh.read(4)
	
	# read length
	(length,) = read_and_unpack(fh, "I")
	
	syncToneLength = 3*samplesPerSec
	syncSamples = []
	for i in xrange(0, syncToneLength):
		(sample,) = read_and_unpack(fh, "h")
		syncSamples.append(sample)
	
	syncFreq = get_maxfrequency(syncSamples, 1.0/3.0)
	if syncFreq != 440:
		print "Invalid sync beep: %d" % (syncFreq,)
		exit(0)
	
	halfByteSampleLength = samplesPerSec / denominator
	j = 0
	buffer = ""
	while True:
		try:
			halfByte = []
			for w in xrange(0,2):
				samples = []
				for i in xrange(0, halfByteSampleLength):
					(sample,) = read_and_unpack(fh, "h")
					samples.append(sample)
					
				freq = get_maxfrequency(samples, samplesPerSec / float(halfByteSampleLength))
				v = get_closest_index(frequencies, freq)
				halfByte.append(v)
				
			fullbyte = halfByte[0] | (halfByte[1] << 4)
			buffer += chr(fullbyte)
			
			j += 1
		except:
			break
	
	ofh = open (outfile, 'w')
	ofh.write(buffer)
	ofh.close()
	fh.close()

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
		to_data(infile, outfile)
		
#

if (__name__ == "__main__"):
	sys.exit(main(len(sys.argv), sys.argv))
