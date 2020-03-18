import sys
import getopt
import soundfile
import os
import os.path
import math

# 张口的分贝阈值
thresholdDecibel = -40
# 口型大小数量
mouthLevels = 3
# 游戏帧率
frameRate = 30


def main():
    global thresholdDecibel, mouthLevels, frameRate
    # 获取传进来的参数
    opts, args = getopt.getopt(sys.argv[2:], "t:f:m:")
    for opt, arg in opts:
        if opt == '-t':
            thresholdDecibel = int(arg)
            if thresholdDecibel > 0:
                thresholdDecibel *= -1
        elif opt == '-f':
            frameRate = int(arg)
        elif opt == '-m':
            mouthLevels = int(arg)
    directory = sys.argv[1]
    print('\n\n##### Mouth Shape Analysis #####\n-----made by Victor Liu\n')
    iterate_audio_files(directory)


# 遍历文件夹中所有音频文件
def iterate_audio_files(directory: str):
    total_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".wav"):
                total_count += 1
                full_path = os.path.join(root, file)
                process_audio_file(full_path)
                print(file + " analyzed!")
    print('\n\nProcess Finished!\nAnalyzed {} voice recordings.'.format(total_count))
    print('Analyze Settings: \n\tThreshold decibel: {}db\n\tMouth levels: {}\n\tGame frame rate: {}'.format(thresholdDecibel, mouthLevels, frameRate))


# 对单个音频文件进行处理
def process_audio_file(file_path):
    audio_info = soundfile.SoundFile(file=file_path)
    audio_data = soundfile.read(file=file_path)[0]
    original_sample_rate = audio_info.samplerate

    output_text = ''
    # 每个检测区间的采样数
    sound_frame_samples = int(original_sample_rate / frameRate)
    frame_begin_sample = 0
    step_size = thresholdDecibel / mouthLevels
    # 遍历每帧的音频
    while frame_begin_sample < len(audio_data):
        frame_end_sample = frame_begin_sample + sound_frame_samples
        frame_data = audio_data[frame_begin_sample:frame_end_sample]
        rms_db = get_sound_frame_rms_db(frame_data)
        # 小于张嘴阈值，为0
        if rms_db < thresholdDecibel:
            step = 0
        else:
            step = int(rms_db / step_size) + 1
        output_text += str(step)
        frame_begin_sample = frame_end_sample
    text_file = open(file_path.replace('wav', 'txt'), 'w')
    text_file.write(output_text)
    text_file.close()


# 获取一个采样窗口的RMS值并转换为dbfs
def get_sound_frame_rms_db(frame_data):
    value_sum = 0
    for sample_data in frame_data:
        value_sum += sample_data * sample_data
    rms_linear = math.sqrt(value_sum / len(frame_data))
    return math.log10(rms_linear) * 20


if __name__ == '__main__':
    main()