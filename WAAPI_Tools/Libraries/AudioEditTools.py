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
    if not audio_data.any():
        return True
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


# 在指定路径创建静音文件
def create_silence_audio_file(path: str, duration: int, sample_rate=44100):
    if os.path.exists(path):
        return False
    num_samples = int(duration * sample_rate)
    silence_data = [0] * num_samples
    soundfile.write(path, silence_data, sample_rate)
    return True


# 获取音频静音部分长度（以采样窗口为单位）
def get_silence_duration_frames(audio_data, samples_per_frame: int, threshold: float, direction_tail: bool):
    silence_frames = 0
    while True:
        if len(audio_data) < samples_per_frame:
            return silence_frames
        if direction_tail:
            frame_data = audio_data[-samples_per_frame:]
        else:
            frame_data = audio_data[:samples_per_frame]
        if get_sound_frame_max_amp(frame_data) > threshold:
            return silence_frames
        silence_frames += 1
        if direction_tail:
            audio_data = audio_data[:-samples_per_frame]
        else:
            audio_data = audio_data[samples_per_frame:]


# 获取一个采样窗口的最大振幅
def get_sound_frame_max_amp(frame_data):
    if len(frame_data.shape) > 1:
        # 把交络波形转换成每个通道单独的数组
        return max(abs(frame_data.T[0]))
    else:
        return max(abs(frame_data))


# 淡入淡出，1为淡入，-1为淡出
def fade(audio_data, duration_samples: int, fade_direction: int):
    duration_samples = round(duration_samples)
    if duration_samples > len(audio_data):
        return
    for index in range(duration_samples):
        audio_data[fade_direction * index] *= index / duration_samples


# 裁剪音频数据
def trim(audio_data, start_samples: int, end_samples: int):
    start_samples = round(start_samples)
    end_samples = round(end_samples)
    if end_samples == 0:
        audio_data = audio_data[start_samples:]
    elif start_samples == 0:
        audio_data = audio_data[:end_samples]
    else:
        audio_data = audio_data[start_samples:end_samples]
    return audio_data
