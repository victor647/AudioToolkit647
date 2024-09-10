import os.path

import soundfile


# 把分贝转换成0-1的值
def decibel_to_linear(decibel: float):
    return min(1.0, pow(10, (decibel / 20)))


# 检测音频文件是否完全是静音
def is_sound_completely_silent(file_path: str):
    if not os.path.exists(file_path):
        return False
    sound_file = soundfile.SoundFile(file=file_path)
    if not sound_file:
        return True
    sound_file.seek(0)
    audio_data = sound_file.read()
    return get_sound_frame_max_amp(audio_data) == 0


# 寻找下一个间隔
def find_next_silence(audio_data, threshold: float, samples_per_frame: int, gap_min_samples: int, frame_begin_sample=0):
    silence_start_sample = -1
    silence_end_sample = 0
    while frame_begin_sample < len(audio_data):
        frame_end_sample = frame_begin_sample + samples_per_frame
        frame_data = audio_data[frame_begin_sample:frame_end_sample]
        max_amp = get_sound_frame_max_amp(frame_data)

        # 静音开始
        if silence_start_sample == -1:
            if max_amp < threshold:
                silence_start_sample = frame_begin_sample
        # 静音结束
        elif max_amp > threshold:
            # 时间不满最短间隔，重新计算
            if frame_begin_sample - silence_start_sample < gap_min_samples:
                silence_start_sample = -1
            else:
                silence_end_sample = frame_begin_sample
                break
        frame_begin_sample = frame_end_sample
    return silence_start_sample, silence_end_sample


# 获取音频尾巴静音部分长度（以采样窗口为单位）
def get_tail_silence_duration_frames(audio_data, samples_per_frame: int, threshold: float):
    silence_frames = 0
    while True:
        if len(audio_data) < samples_per_frame:
            return silence_frames
        frame_data = audio_data[-samples_per_frame:]
        if get_sound_frame_max_amp(frame_data) > threshold:
            return silence_frames
        silence_frames += 1
        audio_data = audio_data[:len(audio_data) - samples_per_frame]


# 获取一个采样窗口的最大振幅
def get_sound_frame_max_amp(frame_data):
    if len(frame_data.shape) > 1:
        # 把交络波形转换成每个通道单独的数组
        return max(abs(frame_data.T[0]))
    else:
        return max(abs(frame_data))


# 淡入淡出，1为淡入，-1为淡出
def fade(audio_data, duration_samples: int, fade_direction: int):
    if duration_samples > len(audio_data):
        return
    for index in range(duration_samples):
        audio_data[fade_direction * index] *= index / duration_samples


def trim(audio_data, start_samples: int, end_samples: int):
    audio_data = audio_data[start_samples:end_samples]
