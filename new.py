
# create a function that plays the byte content
# create a function that converts text into speech bytes
#thread 1 will play sound thread

import concurrent.futures
import io
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment
from pydub.playback import play
import openai
import time
import sys


def sp_count(text):
    count=0
    for char in text:
        if char==".":
            count+=1
    return count 


def play_sound(response):


    try:
        # Synthesize speech
        
        audio_data = response.content

        # Create an in-memory file-like object
        start1=time.time()
        audio_stream = io.BytesIO(audio_data)
        end1=time.time()
        print(start1-end1,"fir")
        
        # Load and play the audio stream
        start2=time.time()
        audio_segment = AudioSegment.from_file(audio_stream, format='mp3')
        end2=time.time()
        print(start2-end2,"sec")
        
        play(audio_segment)

    except Exception as e:
        print(f"Error: {e}")
        
url = None
api_key=None


authenticator = IAMAuthenticator(api_key)
tts = TextToSpeechV1(authenticator=authenticator)
tts.set_service_url(url)
        
def text_to_resp(text):
    
    start=time.time()
    response = tts.synthesize(text, accept='audio/mp3', voice='en-US_EmilyV3Voice').get_result()
    end=time.time()
    print(end-start,"texttoresp")
    return response

# my_resp=text_to_resp("hello, How are you doing")
# play_sound(my_resp)

# my_resp=text_to_resp("Decide how you want to manage the concurrency between the sound-playing thread and the token-conversion thread. You might need to prioritize or coordinate their execution based on your specific requirements. For example, you can use synchronization mechanisms to pause or resume the sound-playing thread when the token-conversion thread has new data to process.")
# play_sound(my_resp)



pool=concurrent.futures.ThreadPoolExecutor(max_workers=2)


def openai_response(prompt):
    openai.api_key = None
    text=""
    model = 'gpt-3.5-turbo'
    messages = [
        {"role": "user", "content": prompt}
    ]
    max_tokens = 512
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        stream=True  # Enable streaming mode
    )
    for resp in response:
        if 'content' in resp.choices[0]['delta'].keys():
            
            text=text+ resp.choices[0]['delta']['content']

            
            if sp_count(text)==2:
                sys.stdout.write(text)
                sys.stdout.flush()
                future1 = pool.submit(text_to_resp,text)
                result1=future1.result()
                pool.submit(play_sound,result1)
                pool.shutdown(wait=True)
                text=""

                
                
                
    if sp_count(text)<=2:
        sys.stdout.write(text)
        sys.stdout.flush()
        future1 = pool.submit(text_to_resp,text)
        result1=future1.result()
        pool.submit(play_sound,result1)
        pool.shutdown(wait=True)
  
  
openai_response("write me a 100 letter story")
        

