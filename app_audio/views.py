from django.views.decorators.csrf import csrf_exempt
import os
from datetime import datetime
import os
from django.http import JsonResponse
# from app_search.views import example

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)

@csrf_exempt
def create_audio(request):
    return_value = request.POST.dict()
    audio_file_name = return_value['audio_file_name']
    textunit_start = return_value['textunit_start']
    textunit_duration = return_value['textunit_duration']
    start_buffer = return_value['start_buffer']
    end_buffer = return_value['end_buffer']

    resulting_audio_name = ''
    for filename in os.listdir(BASE_DIR + "/data/audio"):
        if filename == audio_file_name + '.mp3':
            resulting_audio_name = datetime.now().strftime('%Y_%m_%d %H_%M_%S_%f') + '.mp3'
            
            ffmpeg_command = 'ffmpeg -ss ' + str(float(textunit_start) - float(start_buffer)) + ' -t ' + str(
                float(textunit_duration) + float(start_buffer) +
                float(end_buffer)) + ' -i ' + BASE_DIR + '/"data/audio/' + \
                filename + '" -c copy ' + '"' + BASE_DIR + '/media/' + resulting_audio_name + '"'
        
            os.system(ffmpeg_command)
            break

    resulting_audio_name_for_frontend = "/media/" + resulting_audio_name

    return JsonResponse({'resulting_audio_file': resulting_audio_name_for_frontend})
