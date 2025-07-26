# Watpad --> TTS

## Setup

Install Modules
```
pip install requests beautifulsoup4 pyttsx3
```

Run the script
```
py main.py
```

## Troublshooting:

- IF getting error about not having voice, please install the United States Language Pack

- If its too fast go and change the pace line:

'''
def text_to_speech_combined(text, filename="story.wav", voice_name="David", rate=150):
'''
