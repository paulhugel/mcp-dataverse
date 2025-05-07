import nemo.collections.asr as nemo_asr

class MultiMedia:
    def __init__(self, model_name):
        """Initialize the MultiMedia class with ASR model."""
        self.asr_model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)

    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio file and return timestamps.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            dict: Dictionary containing word, segment and char level timestamps
        """
        output = self.asr_model.transcribe([audio_file_path], timestamps=True)
        return {
            'word': output[0].timestamp['word'],
            'segment': output[0].timestamp['segment'],
            'char': output[0].timestamp['char']
        }

    def print_segments(self, audio_file_path):
        """
        Print segments with their timestamps.
        
        Args:
            audio_file_path (str): Path to the audio file
        """
        timestamps = self.transcribe_audio(audio_file_path)
        for stamp in timestamps['segment']:
            print(f"{stamp['start']}s - {stamp['end']}s : {stamp['segment']}")

    def get_word_timestamps(self, audio_file_path):
        """
        Get word level timestamps.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            list: List of word level timestamps
        """
        return self.transcribe_audio(audio_file_path)['word']

    def get_char_timestamps(self, audio_file_path):
        """
        Get character level timestamps.
        
        Args:
            audio_file_path (str): Path to the audio file
            
        Returns:
            list: List of character level timestamps
        """
        return self.transcribe_audio(audio_file_path)['char']