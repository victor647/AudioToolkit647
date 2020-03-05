import sys
import getopt
import soundfile
import os
import os.path


threshold_db = -48
threshold_linear = 0.003
fade_ms = 10


def main():
    global threshold_db, fade_ms

    opts, args = getopt.getopt(sys.argv[2:], "t:f:")
    for opt, arg in opts:
        if opt == '-t':
            threshold_db = int(arg)
        elif opt == '-f':
            fade_ms = int(arg)

    global threshold_linear
    threshold_linear = min(1.0, pow(10, (threshold_db / 20)))

    directory = sys.argv[1]
    run(directory)


def run(directory: str):
    total_count = trimmed_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".wav"):
                total_count += 1
                full_path = os.path.join(root, file)
                if process_audio_file(full_path):
                    trimmed_count += 1
                    print(full_path + " trimmed!")
    print('Process Finished!\nTrimmed {} out of {} wav files.'.format(trimmed_count, total_count))
    print('TrimSetting: \n\tThreshold decibel: {}db\n\tFade duration: {}ms'.format(threshold_db, fade_ms))


def process_audio_file(file_path):
    audio_file = soundfile.read(file=file_path)
    audio_data = audio_file[0]
    sample_rate = audio_file[1]
    is_mono = True if len(audio_data.shape) == 1 else False
    original_samples = len(audio_data) - 1
    fade_samples = int(fade_ms * sample_rate / 1000)

    cut_begin = get_first_active_sample(audio_data, is_mono)
    cut_end = get_last_active_sample(audio_data, is_mono)

    if cut_begin > fade_samples:
        cut_begin -= fade_samples
    else:
        cut_begin = 0

    if cut_end <= original_samples - fade_samples:
        cut_end += fade_samples
    else:
        cut_end = original_samples

    if cut_begin == 0 and cut_end == original_samples:
        return False

    audio_data = audio_data[cut_begin:cut_end]
    if cut_begin > 0:
        fade_in(audio_data, fade_samples)
    if cut_end < original_samples:
        fade_out(audio_data, fade_samples)

    soundfile.write(file=file_path, data=audio_data, samplerate=sample_rate)
    return True


def get_first_active_sample(audio_data, is_mono: bool):
    current_sample = 0
    for sample_data in audio_data:
        if is_mono:
            if abs(sample_data) > threshold_linear:
                return current_sample
        else:
            for channel_data in sample_data:
                if abs(channel_data) > threshold_linear:
                    return current_sample
        current_sample += 1


def get_last_active_sample(audio_data, is_mono: bool):
    current_sample = len(audio_data) - 1
    for sample_data in reversed(audio_data):
        if is_mono:
            if abs(sample_data) > threshold_linear:
                return current_sample
        else:
            for channel_data in sample_data:
                if abs(channel_data) > threshold_linear:
                    return current_sample
        current_sample -= 1


def fade_in(audio_data, duration_samples: int):
    for index in range(duration_samples):
        audio_data[index] *= index / duration_samples


def fade_out(audio_data, duration_samples: int):
    for index in range(duration_samples):
        audio_data[-index] *= index / duration_samples


if __name__ == '__main__':
    main()