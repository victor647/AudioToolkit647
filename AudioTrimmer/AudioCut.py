import sys
import getopt
import soundfile
import os
import os.path
import numpy
import librosa
import Tools

# 裁剪的分贝阈值
thresholdDecibel = -48
# 计算出对应的0-1采样值
thresholdLinear = 0.003
# 每次淡入淡出的时长
fadeDuration = 50
# 两个音效中间最短的空白时长
gapMinDuration = 300
# 给两个音效中间补齐的空白时长
gapPreservedDuration = 200
# 是否分割文件导出
splitAudioFile = False
# 输出的文件的采样率
targetSampleRate = 0
# 当前处理的音频文件的声道数量
channels = 2
# 得到优化的音频文件数量
editedCount = 0


def main():
    global thresholdDecibel, thresholdLinear, fadeDuration, gapMinDuration, gapPreservedDuration, targetSampleRate, splitAudioFile
    # 获取传进来的参数
    opts, args = getopt.getopt(sys.argv[2:], "t:f:d:p:s:c")
    for opt, arg in opts:
        if opt == '-t':
            thresholdDecibel = int(arg)
            if thresholdDecibel > 0:
                thresholdDecibel *= -1
        elif opt == '-f':
            fadeDuration = int(arg)
        elif opt == '-d':
            gapMinDuration = int(arg)
        elif opt == '-p':
            gapPreservedDuration = int(arg)
        elif opt == '-s':
            targetSampleRate = int(arg)
        elif opt == '-c':
            splitAudioFile = True

    thresholdLinear = Tools.decibel_to_linear(thresholdDecibel)
    directory = sys.argv[1]
    print('\n\n##### SFX Library Optimizer #####\n-----made by Victor Liu\n')
    iterate_audio_files(directory)


# 遍历文件夹中所有音频文件
def iterate_audio_files(directory: str):
    global editedCount
    editedCount = 0
    total_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".wav"):
                total_count += 1
                full_path = os.path.join(root, file)
                process_audio_file(full_path)
    print('\n\nProcess Finished, Optimized {} out of {} wav files.'.format(editedCount, total_count))
    print_trim_settings()


# 输出日志
def print_trim_settings():
    print('Trim Settings:')
    print('\tThreshold decibel: {}db'.format(thresholdDecibel))
    print('\tFade duration: {}ms'.format(fadeDuration))
    print('\tSilence gap detect threshold: {}ms'.format(gapMinDuration))
    if not splitAudioFile:
        print('\tPreserved gap duration: {}ms\n\n'.format(gapPreservedDuration))


# 对单个音频文件进行处理
def process_audio_file(file_path):
    global channels
    audio_info = soundfile.SoundFile(file=file_path)
    channels = audio_info.channels
    audio_data = soundfile.read(file=file_path)[0]

    # 转换采样率
    original_sample_rate = audio_info.samplerate
    if 0 < targetSampleRate < original_sample_rate:
        audio_data = librosa.resample(audio_data.T, original_sample_rate, targetSampleRate).T
        output_sample_rate = targetSampleRate
    else:
        output_sample_rate = original_sample_rate

    # 淡入淡出的采样数
    fade_samples = int(fadeDuration * output_sample_rate / 1000)
    # 插入的静音的采样数
    gap_preserved_samples = int(gapPreservedDuration * output_sample_rate / 1000)
    # 检测音效之间空白的采样数
    gap_min_samples = int(gapMinDuration * output_sample_rate / 1000)

    gap_start_sample = -gap_preserved_samples
    preserved_gap = Tools.create_silence(channels, gap_preserved_samples)
    gap_found = 0
    # 寻找所有空白
    while True:
        gap_start_sample, gap_end_sample = Tools.find_next_silence(audio_data, thresholdLinear, fade_samples, gap_min_samples, gap_start_sample + gap_preserved_samples)
        # 找到头部的空白
        if gap_start_sample == 0:
            audio_data = audio_data[gap_end_sample:]
            Tools.apply_fade(audio_data, fade_samples, 1)
            continue
        # 没有找到更多的静音，去除尾部静音后结束
        if gap_end_sample == 0:
            audio_data = audio_data[:gap_start_sample]
            Tools.apply_fade(audio_data, fade_samples, -1)
            break
        # 去除中段静音
        data_first = audio_data[:gap_start_sample]
        Tools.apply_fade(data_first, fade_samples, -1)
        data_second = audio_data[gap_end_sample:]
        Tools.apply_fade(data_second, fade_samples, 1)
        gap_found += 1
        # 分割模式，每找到一段则导出一个文件
        if splitAudioFile:
            split_file_path = file_path[:-4] + '_s' + str(gap_found).zfill(2) + '.wav'
            soundfile.write(file=split_file_path, data=data_first, samplerate=output_sample_rate, subtype=audio_info.subtype)
            audio_data = data_second
        else:
            audio_data = numpy.concatenate((data_first, preserved_gap, data_second), axis=0)
    # 没有可优化的地方
    if gap_found == 0:
        print('Silence gaps already optimized in ' + file_path)
    else:
        global editedCount
        editedCount += 1
        if not splitAudioFile:
            soundfile.write(file=file_path, data=audio_data, samplerate=output_sample_rate, subtype=audio_info.subtype)
            print('{} silence gaps trimmed in {}'.format(gap_found, file_path))
        else:
            gap_found += 1
            split_file_path = file_path[:-4] + '_s' + str(gap_found).zfill(2) + '.wav'
            soundfile.write(file=split_file_path, data=audio_data, samplerate=output_sample_rate, subtype=audio_info.subtype)
            print('{} split clips created from {}'.format(gap_found, file_path))
            os.remove(file_path)


if __name__ == '__main__':
    main()
