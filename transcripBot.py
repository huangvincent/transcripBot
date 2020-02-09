import praw
from urllib.request import Request, urlopen
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
import io

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
<<<<<<< HEAD
    """ """
=======
>>>>>>> d4f83fba09bc989eae1288629d336d4e11ac9c7e
    client = speech_v1.SpeechClient()

    config = {
        "language_code": "en-US",
        "sample_rate_hertz": 16000,
        "encoding": enums.RecognitionConfig.AudioEncoding.LINEAR16,
    }

    audio = {"content": audio_file}

    response = client.recognize(config, audio)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))


    return

def comment(reddit):
    return

def main():
    # create reddit class
    reddit = authenticate()

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
        # print("url={}".format(audio_url))

        # confirm there is audio
        if audio_file == None:
            continue
        print("extracted audio file")

        # extract data
        transcribe(audio_file)

<<<<<<< HEAD
        # reply to mention

=======
>>>>>>> d4f83fba09bc989eae1288629d336d4e11ac9c7e
if __name__ == '__main__':
    main()
