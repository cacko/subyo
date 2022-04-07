import click
from setuptools import Command
from pathlib import Path
from subyo.pipeline.audio_recognition import AudioRecognition
from subyo.pipeline.translate import Translation


class SubyoCommands(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=SubyoCommands)
def cli():
    pass


@cli.command('subtitles')
@click.argument('path', type=click.Path(exists=True))
@click.option('-m', '--model', default="")
def cmd_export(path, model):
    if len(model):
        AudioRecognition.register(model)
    AudioRecognition.subtitles(path)


@cli.command('translate')
@click.argument('path', type=click.Path(exists=True))
@click.option('-m', '--model', default="Helsinki-NLP/opus-mt-en-hy")
def cmd_translate(path, model):
    path = Path(path)
    model_path = Path(model)
    output = Path(".") / f"{path.stem}-{model_path.name}.srt"
    with output.open("wb") as out:
        for line in Translation(model).translate(path.read_text()):
            line = line.strip()
            print(line)
            out.write(f"{line}\n".encode())
