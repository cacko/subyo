from pathlib import Path
from pydub import AudioSegment
from transformers import pipeline
import moviepy.editor as mp
import math
from hashlib import md5
from stringcase import spinalcase


class AudioRecognitionMeta(type):
    _instances: dict[str, 'AudioRecognition'] = {}
    _pipeline = None
    _model_name = "facebook/s2t-large-librispeech-asr"
    _task = "automatic-speech-recognition"

    def __call__(cls, *args, **kwds):
        key = md5(args[0].encode()).hexdigest()
        if key not in cls._instances:
            cls._instances[key] = type.__call__(cls, *args, **kwds)
        return cls._instances[key]

    def register(cls, model_name: str):
        cls._model_name = model_name

    @property
    def model_name(cls):
        return cls._model_name

    @property
    def pipeline(cls):
        if not cls._pipeline:
            cls._pipeline = pipeline(task=cls._task, model=cls._model_name)
        return cls._pipeline

    def subtitles(cls, path):
        return cls(path).do_subtitles()


def get_timestamp(time):
    result = int(time * 1000)
    millisecond = result % 1000
    result //= 1000
    second = result % 60
    result //= 60
    minute = result % 60
    result //= 60
    hour = result
    return "{hour:02d}:{minute:02d}:{second:02d},{millisecond:03d}".format(hour=hour, minute=minute, second=second,
                                                                           millisecond=millisecond)


class AudioRecognition(object, metaclass=AudioRecognitionMeta):
    __path: Path = None
    temp_video_path = "tmp.mp4"
    audio_path = "audio.wav"
    subtitle_path = None

    subtitle = []
    subtitleSub = []
    WINDOW_SIZE = 0.5
    THRESHOLD = 0.3
    SUBTITLE_TYPE = 'srt'

    def __init__(self, path: str):
        self.__path = Path(path)
        out_name = spinalcase(f"{self.__path.stem} {self.__class__.model_name.replace('/', ' ')}")
        self.subtitle_path = Path(".") / f"{out_name}.{self.SUBTITLE_TYPE}"
        tmp_path = Path(self.temp_video_path)
        tmp_path.write_bytes(self.__path.read_bytes())

    def do_subtitles(self):
        clip, file_length = self.cvt_video2audio()
        self.extract_sound(clip, file_length)
        self.make_subtitle()

    def make_subtitle(self):
        subtitle_index = 1
        pipe = self.__class__.pipeline
        with self.subtitle_path.open("w") as out:
            source = AudioSegment.from_wav(self.audio_path)
            normalized = "normalized.wav"
            source.export(normalized, format="wav", parameters=["-filter:a", "loudnorm"])
            source = AudioSegment.from_wav(normalized)
            for (idx, _) in enumerate(self.subtitle):
                start, end = _
                audio = source[start * 1000:end * 1000] + 20
                if audio:
                    try:
                        audio.export("tmp.wav", format="wav", parameters=[
                            "-ac", "1", '-ar', "16000"
                        ])
                        res = pipe("tmp.wav")
                        text = res["text"]
                        if not len(text):
                            continue
                        print(f"{start} - {end} {text}")
                        start_time = get_timestamp(start)
                        end_time = get_timestamp(end)
                        output_format = f'{subtitle_index}\n{start_time} --> {end_time}\n{text}\n\n'
                        out.write(f"{output_format}\n")
                        self.subtitleSub.append(output_format)
                        subtitle_index += 1
                    except Exception as e:
                        print(e)
                else:
                    print('no audio')

    def cvt_video2audio(self):
        video = mp.VideoFileClip(self.temp_video_path)
        video.audio.write_audiofile(self.audio_path)
        my_clip = mp.VideoFileClip(self.temp_video_path)
        file_length = math.floor(my_clip.audio.end / self.WINDOW_SIZE)
        return my_clip, file_length

    def extract_sound(self, my_clip, file_length):
        is_start_speak = True
        start_time = 0
        for i in range(file_length):
            s = my_clip.audio.subclip(
                i * self.WINDOW_SIZE, (i + 1) * self.WINDOW_SIZE)
            if s.max_volume() > self.THRESHOLD:
                if is_start_speak:
                    start_time = i * self.WINDOW_SIZE
                is_start_speak = False
            else:
                if not is_start_speak:
                    end_time = i * self.WINDOW_SIZE
                    self.subtitle.append((start_time, end_time))
                is_start_speak = True
