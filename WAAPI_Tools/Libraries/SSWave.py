# coding=utf-8
from __future__ import division, print_function, absolute_import
from pydub import AudioSegment
import numpy
import struct
import collections
from math import log
import requests, json

_ieee = False

# assumes file pointer is immediately
#  after the 'fmt ' id
def _read_fmt_chunk(fid):
    res = struct.unpack('<ihHIIHH',fid.read(20))
    size, comp, noc, rate, sbytes, ba, bits = res
    if (comp != 1 or size > 16):
        if (comp == 3):
          global _ieee
          _ieee = True
        else:
            pass
          # warnings.warn("Unfamiliar format bytes", WavFileWarning)
        if (size>16):
            fid.read(size-16)
    return size, comp, noc, rate, sbytes, ba, bits

# assumes file pointer is immediately
#   after the 'data' id
def _read_data_chunk(fid, noc, bits, normalized=False):
    size = struct.unpack('<i',fid.read(4))[0]

    if bits == 8 or bits == 24:
        dtype = 'u1'  #uint8
        bytes_val = 1
    else:
        bytes_val = bits//8
        dtype = '<i%d' % bytes_val

    if bits == 32 and _ieee:
       dtype = 'float32'
    data = numpy.fromfile(fid, dtype=dtype, count=size//bytes_val)

    if bits == 24:
        a = numpy.empty((len(data) // 3, 4), dtype='u1')
        a[:, :3] = data.reshape((-1, 3))
        a[:, 3:] = (a[:, 3 - 1:3] >> 7) * 255
        data = a.view('<i4').reshape(a.shape[:-1])

    if noc > 1:
        data = data.reshape(-1,noc)

    if bool(size & 1):     # if odd number of bytes, move 1 byte further (data chunk is word-aligned)
      fid.seek(1,1)

    if normalized:
        if bits == 8 or bits == 16 or bits == 24:
            normfactor = 2 ** (bits-1)
        data = numpy.float32(data) * 1.0 / normfactor

    return data

def _skip_unknown_chunk(fid):
    data = fid.read(4)
    size = struct.unpack('<i', data)[0]
    if bool(size & 1):     # if odd number of bytes, move 1 byte further (data chunk is word-aligned)
      size += 1
    fid.seek(size, 1)

def _read_riff_chunk(fid):
    str1 = fid.read(4)
    if str1 != b'RIFF':
        raise ValueError("Not a WAV file.")
    fsize = struct.unpack('<I', fid.read(4))[0] + 8
    str2 = fid.read(4)
    if (str2 != b'WAVE'):
        raise ValueError("Not a WAV file.")
    return fsize

def read(file, readmarkers=False, readmarkerlabels=False, readmarkerslist=False, readloops=False, readpitch=False, normalized=False, forcestereo=False, log=False, readinfo=False):

    if hasattr(file,'read'):
        fid = file
    else:
        fid = open(file, 'rb')

    fsize = _read_riff_chunk(fid)
    noc = 1
    bits = 8
    #_cue = []
    #_cuelabels = []
    _markersdict = collections.defaultdict(lambda: {'position': -1, 'label': ''})
    loops = []
    pitch = 0.0
    # 当前读取的位置
    while (fid.tell() < fsize):
        # read the next chunk
        chunk_id = fid.read(4)
        if chunk_id == b'fmt ':
            size, comp, noc, rate, sbytes, ba, bits = _read_fmt_chunk(fid)
        elif chunk_id == b'data':
            data = _read_data_chunk(fid, noc, bits, normalized)
        elif chunk_id == b'cue ':
            str1 = fid.read(8)
            size, numcue = struct.unpack('<ii',str1)
            for c in range(numcue):
                str1 = fid.read(24)
                idx, position, datachunkid, chunkstart, blockstart, sampleoffset = struct.unpack('<iiiiii', str1)
                #_cue.append(position)
                _markersdict[idx]['position'] = position                    # needed to match labels and markers

        elif chunk_id == b'LIST':
            str1 = fid.read(8)
            size, datatype = struct.unpack('<ii', str1)
        elif chunk_id in [b'ICRD', b'IENG', b'ISFT', b'ISTJ']:
            _skip_unknown_chunk(fid)
        elif chunk_id == b'labl':
            str1 = fid.read(8)
            size, idx = struct.unpack('<ii',str1)
            size = size + (size % 2)
            label = fid.read(size-4).rstrip(bytes('\x00', 'UTF-8'))               # remove the trailing null characters
            #_cuelabels.append(label)
            _markersdict[idx]['label'] = label                           # needed to match labels and markers

        elif chunk_id == b'smpl':
            str1 = fid.read(40)
            size, manuf, prod, sampleperiod, midiunitynote, midipitchfraction, smptefmt, smpteoffs, numsampleloops, samplerdata = struct.unpack('<iiiiiIiiii', str1)
            cents = midipitchfraction * 1./(2**32-1)
            pitch = 440. * 2 ** ((midiunitynote + cents - 69.)/12)
            for i in range(numsampleloops):
                str1 = fid.read(24)
                cuepointid, datatype, start, end, fraction, playcount = struct.unpack('<iiiiii', str1)
                loops.append([start, end])
        else:
            if log:
                pass
            # warnings.warn("Chunk " + str(chunk_id) + " skipped", WavFileWarning)
            _skip_unknown_chunk(fid)
    fid.close()

    if data.ndim == 1 and forcestereo:
        data = numpy.column_stack((data, data))

    _markerslist = sorted([_markersdict[l] for l in _markersdict], key=lambda k: k['position'])  # sort by position
    _cue = [m['position'] for m in _markerslist]
    _cuelabels = [m['label'] for m in _markerslist]
    duration = round(len(data)/rate, 2)

    return ((rate, data, bits, ) if readinfo else ())\
        + ((_cue,) if readmarkers else ()) \
        + ((_cuelabels,) if readmarkerlabels else ()) \
        + ((_markerslist,) if readmarkerslist else ()) \
        + ((loops,) if readloops else ()) \
        + ((pitch,) if readpitch else ())

def write(filename, rate, data, bitrate=None, markers=None, loops=None, pitch=None, normalized=False):
    """
    Write a numpy array as a WAV file

    """

    # normalization and 24-bit handling
    if bitrate == 24:   # special handling of 24 bit wav, because there is no numpy.int24...
        if normalized:
            data[data > 1.0] = 1.0
            data[data < -1.0] = -1.0
            a32 = numpy.asarray(data * (2 ** 23 - 1), dtype=numpy.int32)
        else:
            a32 = numpy.asarray(data, dtype=numpy.int32)
        if a32.ndim == 1:
            a32.shape = a32.shape + (1,)  # Convert to a 2D array with a single column.
        a8 = (a32.reshape(a32.shape + (1,)) >> numpy.array([0, 8, 16])) & 255  # By shifting first 0 bits, then 8, then 16, the resulting output is 24 bit little-endian.
        data = a8.astype(numpy.uint8)
    else:
        if normalized:   # default to 32 bit int
            data[data > 1.0] = 1.0
            data[data < -1.0] = -1.0
            data = numpy.asarray(data * (2 ** 31 - 1), dtype=numpy.int32)

    fid = open(filename, 'wb')
    fid.write(b'RIFF')
    fid.write(b'\x00\x00\x00\x00')
    fid.write(b'WAVE')

    # fmt chunk
    fid.write(b'fmt ')
    if data.ndim == 1:
        noc = 1
    else:
        noc = data.shape[1]
    bits = data.dtype.itemsize * 8 if bitrate != 24 else 24
    sbytes = rate * (bits // 8) * noc
    ba = noc * (bits // 8)
    fid.write(struct.pack('<ihHIIHH', 16, 1, noc, rate, sbytes, ba, bits))

    # cue chunk
    if markers:
        if isinstance(markers[0], dict):
            labels = [m['label'] for m in markers]
            markers = [m['position'] for m in markers]
        else:
            labels = ['' for m in markers]

        fid.write(b'cue ')
        size = 4 + len(markers) * 24
        fid.write(struct.pack('<ii', size, len(markers)))
        for i, c in enumerate(markers):
            s = struct.pack('<iiiiii', i + 1, c, 1635017060, 0, 0, c)
            fid.write(s)

        lbls = b''
        for i, lbl in enumerate(labels):
            lbls += b'labl'
            label = lbl + (b'\x00' if len(lbl) % 2 == 1 else b'\x00\x00')
            size = len(lbl) + 1 + 4          # because \x00
            lbls += struct.pack('<ii', size, i + 1)
            lbls += label

        fid.write(b'LIST')
        size = len(lbls) + 4
        fid.write(struct.pack('<i', size))
        fid.write(b'adtl')
        fid.write(lbls)

    # smpl chunk
    if loops or pitch:
      if not loops:
        loops = []
      if pitch:
        midiunitynote = 12 * numpy.log2(pitch * 1.0 / 440.0) + 69
        midipitchfraction = int((midiunitynote - int(midiunitynote)) * (2**32-1))
        midiunitynote = int(midiunitynote)
      else:
        midiunitynote = 0
        midipitchfraction = 0
      fid.write(b'smpl')
      size = 36 + len(loops) * 24
      sampleperiod = int(1000000000.0 / rate)

      fid.write(struct.pack('<iiiiiIiiii', size, 0, 0, sampleperiod, midiunitynote, midipitchfraction, 0, 0, len(loops), 0))
      for i, loop in enumerate(loops):
        fid.write(struct.pack('<iiiiii', 0, 0, loop[0], loop[1], 0, 0))

    # data chunks
    fid.write(b'data')
    fid.write(struct.pack('<i', data.nbytes))
    import sys
    if data.dtype.byteorder == '>' or (data.dtype.byteorder == '=' and sys.byteorder == 'big'):
        data = data.byteswap()

    data.tofile(fid)

    if data.nbytes % 2 == 1:
        s1 = '\x00'
        s2 = str.encode(s1)
        fid.write(s2)

    size = fid.tell()
    fid.seek(4)
    fid.write(struct.pack('<i', size-8))
    fid.close()
    # print('Marked！')

class SWaveObject(object):
    def __init__(self, wav_path):
        super(SWaveObject, self).__init__()
        info = read(wav_path, readinfo=True)
        self.readmarkerslist = read(wav_path, readmarkerslist=True)[0]
        self.readmarkerlabels = read(wav_path, readmarkerlabels=True)[0]
        self.wav_path = wav_path
        self.framerate = info[0]
        self.data = info[1]
        self.bits = info[2]
        self.duration = round(len(info[1]) / info[0], 2)
        self.RMS = int
        self.channel = int(len(self.data)*8)/(self.bits*self.framerate)
        # self.DBList = self.audio2DB(self.data, self.bits)
        # self.voice_recognition_list = self.voiceRecognition()

    ###### 转DB ######
    def audio2DB(self, data, bits):

        self.DBList = []

        for eachSampleData in data:
            if eachSampleData == 0:
                eachSampleData = 1
            if eachSampleData < 0:
                DB = 20 * log((abs(eachSampleData) / (2 ** (bits - 1))), 10)
            if eachSampleData > 0:
                DB = 20 * log((abs(eachSampleData) / (2 ** (bits - 1))), 10)
            each_DB = round(DB, 1)
            self.DBList.append(each_DB)

        # with open(txt_path, "w") as f:
        #     f.writelines(self.DBList)

        return self.DBList

    ##### 计算一段音频的RMS值 ######
    def wavRMS(self, ourRate):

        song = AudioSegment.from_wav(self.wav_path)

        duration = float(song.duration_seconds)

        total = (int)(duration * (1 / ourRate) + 0.5)

        s = []

        db_list = []

        for i in range(0, total):
            each_duration = ourRate * 1000

            slice = song[i * each_duration:(i + 1) * each_duration]

            db = slice.dBFS

            peak = slice.max_dBFS

            db_list.append(db)

            rms = slice.rms

            s.append(str(rms))

        # fileshape = ''.join(s)
        waveDate = s
        return waveDate, db_list

    ######使用DB进行静音剪切，现在是首尾都剪######
    def cutZeroByDB(self, result_path, ):
        # voice_input = SSWave.SWaveObject(wav_path)
        dblist = self.DBList

        # len(string)
        def get_count(dblist):
            count = 0
            for i in range(len(dblist)):
                if dblist[i] < -60:
                    count = count + 1
                if dblist[i] >= -60:
                    break
            return count

        start_count = get_count(dblist)
        string_reverse = dblist[::-1]
        end_count = len(dblist) - get_count(string_reverse)

        start_time = start_count / self.framerate
        end_time = end_count / self.framerate

        # cut
        self.audioCut(result_path, start_time, end_time)

    ###### 音频剪切 ######
    ##直接输入时间就可以##
    def audioCut(self, result_path, start_time, end_time):
        start_time = float(start_time) * 1000
        end_time = float(end_time) * 1000

        sound = AudioSegment.from_wav(self.wav_path)
        word = sound[start_time:end_time]

        ##fade
        fade_duration = 0.001 * 1000
        fade_in_the_hard_way = word.fade(from_gain=-120.0, start=0, duration=fade_duration)
        fade_out_the_hard_way = fade_in_the_hard_way.fade(to_gain=-120.0, end=(word.duration_seconds)*1000, duration=fade_duration)
        fade_out_the_hard_way.export(result_path, format="wav")

        print('Cut!')

    ###### FadeIn和FadeOut ######
    def audioFadeIn(self, result_path, from_gain_db, start_time, fade_duration):
        start_time = float(start_time)*1000

        sound = AudioSegment.from_wav(self.wav_path)

        # fade_in_the_hard_way = sound.fade(from_gain=-120.0, start=0, duration=5000)
        fade_duration = int(fade_duration * 1000)
        fade_in_the_hard_way = sound.fade(from_gain=from_gain_db, start=int(start_time), duration=int(fade_duration))

        fade_in_the_hard_way.export(result_path, format="wav")

        print('Fade In!')

    def audioFadeOut(self, result_path, to_gain, end_time, fade_duration):
        end_time = float(end_time)*1000

        sound = AudioSegment.from_wav(self.wav_path)

        # fade_out_the_hard_way = sound.fade(to_gain=-120.0, end=0, duration=5000)
        fade_duration = int(fade_duration * 1000)
        fade_out_the_hard_way = sound.fade(to_gain=to_gain, end=int(end_time), duration=int(fade_duration))

        fade_out_the_hard_way.export(result_path, format="wav")

        print('Fade Out!')
