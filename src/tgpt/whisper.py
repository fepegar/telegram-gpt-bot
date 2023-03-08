from telegram import Voice


def dollars_to_pounds(dollars: float) -> float:
    return dollars * 0.8374  # TODO: use API


class Whisper:
    DOLLARS_PER_SECOND = 0.006 / 60

    def get_price_pounds(self, voice: Voice):
        seconds = voice.duration
        dollars = seconds * self.DOLLARS_PER_SECOND
        pounds = dollars_to_pounds(dollars)
        return pounds

    def transcribe(self, voice: Voice):
        pounds = self.get_price_pounds(voice)
        pence = pounds * 100
        text = f"Transcribing that would cost {pence:.2f}p"
        return text
