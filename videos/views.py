from django.shortcuts import render, get_object_or_404, redirect
from .models import Video, Controller

import os
# import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import logging

logger = logging.getLogger(__name__)
loggerd = logging.getLogger('django')

def video_details(request, video_id):
	# video = Video.objects.get(video_id=video_id)
	if video_id == 'all':
		return render(request, 'video.html', {'videos':Video.objects.all()})
	else:
		video = get_object_or_404(Video, video_id=video_id)
		return render(request, 'video.html', {'videos':[video]})

def queue(request):
	# video = Video.objects.get(video_id=video_id)

	if request.method == 'POST':
		logger.info(f'POST video_id ({request.POST.get("id", "unknown")}) video_status ({request.POST.get("status", "unknown")}) action ({request.POST.get("action", "unknown")})')

	try:
		if request.method == 'GET':
			return render(request, 'queue.html', {'videos':Video.objects.all()})

		elif request.method == 'POST' and request.POST.get('action') == 'play':
			logger.info(f'Play control received')
			controller = Controller.objects.get(attribute='player_status')
			controller.value = 1
			controller.save()

		elif request.method == 'POST' and request.POST.get('action') == 'pause':
			logger.info(f'Pause control received')
			controller = Controller.objects.get(attribute='player_status')
			controller.value = 2
			controller.save()

		elif request.method == 'POST' and request.POST.get('action') == 'remove':
			vid = request.POST.get('id')
			status = int(request.POST.get('status'))
			logger.info(f'Removing video - {vid}')
			if status != 1 and status != 2:
				video = Video.objects.get(id=vid)
				if video:
					video.delete()
			else:
				controller = Controller.objects.get(attribute='player_status')
				controller.value = 0
				controller.save()

		return render(request, 'queue.html', {'videos':Video.objects.all()})

	except:
		logger.error('Error in queue processing')

def search(request):
	if request.method == "POST":
	    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

	    api_service_name = "youtube"
	    api_version = "v3"
	    youtube = googleapiclient.discovery.build(  
	               api_service_name, 
	               api_version, 
	               developerKey='AIzaSyBW6v2PaSHB386if5FQ0CZIZpwy0X-nORI')

	    yt_request = youtube.search().list(
	        part="snippet",
	        maxResults=20,
	        q=request.POST.get('searchString', ''),
	        type="video"
	    )
	    response = yt_request.execute()
	    videos = [
			    	{
			    		'title' : v.get('snippet', {}).get('title', '')
			    		,'video_id' : v.get('id', {}).get('videoId', '')
			    		,'description' : v.get('snippet', {}).get('description', '')
			    		,'thumbnail_url' : v.get('snippet',{}).get('thumbnails', {}).get('default', {}).get('url', '')
			    	}
			    	for v in response.get('items', [])
			    ]
	    return render(request, 'search.html', {'results':videos})



	else:
		return render(request, 'search.html', {'request':'not a post'})

def add(request):
	new_video = Video(
		video_id = request.POST.get('video_id','')
		,title = request.POST.get('title','')
		,description = request.POST.get('description','')
		,thumbnail_url = request.POST.get('thumbnail_url','')
	)
	new_video.save()
	return redirect('queue')

def remove(request):
	Video.objects.get(id = request.POST.get('id')).delete()
	return redirect('queue')
