import praw
from urllib.request import Request, urlopen
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
import io
import time

def authenticate():
    """ retrieves reddit class using credentials stored in praw.ini """
    print("authenticating...")
    reddit = praw.Reddit()
    print("logged in as {}".format(reddit.user.me()))
    return reddit

def get_mentions(reddit):
    """ returns a list of "bot mention" messages as a list """
    mentions = list()
    for message in reddit.inbox.unread(limit=None):
        subject = message.subject.lower()
        if subject == "username mention" and isinstance(message, praw.models.Comment):
            mentions.append(message)

    return mentions

def get_audio_url(reddit, submission):
    """ returns url containing submission media """
    url = None
    try:
        # assume submission is a video and grab media url
        url = submission.media['reddit_video']['fallback_url']
        url = str(url)

        # enable audio
        url = url.rpartition('/')[0] + "/audio"

    except Exception as e:
        print("Error encountered: {}".format(e))
        print("Cannot read media's url, submission is not a reddit video")

    return url

def has_audio(url):
    """ checks if a url with /audio suffix has audio by trying to open it"""
    try:
        request = Request(url)
        response = urlopen(request)
        return response.read()
    except Exception as e:
        print("Error encountered: {}".format(e))
        return None


def transcribe(audio_file):
    """ transcribes audio file to a text string using Google
    speech-to-text following
    https://cloud.google.com/speech-to-text/docs/sync-recognize """
    print("transcribing audio")
    client = speech_v1p1beta1.SpeechClient()
    enable_word_time_offsets = True

    config = {
        "language_code": "en-US",
        "sample_rate_hertz": 44100,
        "encoding": enums.RecognitionConfig.AudioEncoding.MP3,
        "model": "default",
        "enable_word_time_offsets": enable_word_time_offsets
    }

    audio = {"content": audio_file}

    operation = client.long_running_recognize(config, audio)
    response = operation.result()

    transcription = "beep boop. I'm a bot."
    print(response)

    # Print the start and end time of each word
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        first_word = alternative.words[0]

        transcription += "\r\r ({:02d}:{:02d})  \r".format(first_word.start_time.seconds // 60, first_word.start_time.seconds % 60)
        transcription += str(alternative.transcript)

    print("transcription successful")
    transcription += "\r\r [End of Transcription]"
    return transcription

def main():
    # create reddit class
    reddit = authenticate()

    while(True):
        # check inbox for mentions
        mentions = get_mentions(reddit)

        # parse each mention's post
        for mention in mentions:
            # get submission the mention/comment is in
            submission = mention.submission
            print("submission title: {}".format(submission.title))

            # get audio file as an url
            audio_url = get_audio_url(reddit, submission)
            audio_file = has_audio(audio_url)

            # confirm there is audio
            if audio_file == None:
                continue

            # extract data
            transcription = transcribe(audio_file)

            # reply to mention
            mention.reply(transcription)

            # wait a second so we don't spam reddit
            time.sleep(1)

        # mark mentions as read
        reddit.inbox.mark_read(mentions)

        # wait 5 seconds before checking for new mentions
        time.sleep(5)

if __name__ == '__main__':
    main()
