#### TODO
# BUG logging file handler error - disabling for now

# logging
# proper db operations
# module for enums for player status everywhere - client and remote
# display video duration in UI
# dont clear up videos db at start
#  error handling

# UI
# function to clear up queue
# function to restart vlc_controller
# table cell borders

# db operations error handling on both sides - client contoller and web app controller
# revamp controller mechanism. migrate controller to a django http listener?



import sqlite3
import time
import vlc
import pafy
from enum import Enum
import logging

YOUTUBE_BASE = 'https://www.youtube.com/watch?v='
player = 0
video_on_deck = {}


class PlayerStatus(Enum):
	STOP = 0
	PLAY = 1
	PAUSE = 2


def control_play(conn, video):
	global video_on_deck
	global player

	cur = conn.cursor()

	if video:
		logging.info(f'Start - {video["title"]}')
		url = f'{YOUTUBE_BASE}{video["video_id"]}'
		pvideo = pafy.new(url)
		best = pvideo.getbest()
		player = vlc.MediaPlayer(best.url)
		player.play()
		time.sleep(3) # sleep to let player.is_playing refresh

		video_on_deck = video

		logging.debug(f'update videos_video set status=1 where id={video["id"]}')
		cur.execute(f'update videos_video set status=1 where id={video["id"]}')
	else:
		player.play()
		logging.debug(f'update videos_video set status=1 where id={video_on_deck["id"]}')
		cur.execute(f'update videos_video set status=1 where id={video_on_deck["id"]}')

	cur.execute(f'update videos_controller set value=1 where attribute="player_status"')
	conn.commit()			


def control_pause(conn):
	global video_on_deck
	global player

	cur = conn.cursor()

	player.pause()
	logging.debug(f'update videos_video set status=2 where id={video_on_deck["id"]}')
	cur.execute(f'update videos_video set status=2 where id={video_on_deck["id"]}')

	cur.execute(f'update videos_controller set value=2 where attribute="player_status"')
	conn.commit()	

	
def play_next_video(conn):
	cur = conn.cursor()

	if player:
		player.stop()

	# pop off currently running or last run video
	if video_on_deck:
		cur.execute(f'delete from videos_video where id={video_on_deck["id"]}')

	cur.execute(f'update videos_controller set value=1 where attribute="player_status"')
	conn.commit()	

	videos = cur.execute('select id, video_id, title from videos_video order by id asc').fetchall()	
	if videos:
		control_play(conn, {
				'id' : videos[0][0]
				,'video_id' : videos[0][1]
				,'title' : videos[0][2]
			})


def init_db(conn):
	cur = conn.cursor()
	# cur.execute('delete from videos_video')
	cur.execute('delete from videos_controller')
	conn.commit()
	cur.execute(f'insert into videos_controller (attribute, value) values ("player_status", {PlayerStatus.PLAY.value})')
	conn.commit()

def get_controller_status(conn):
	cur = conn.cursor()
	cur.execute('select value,attribute from videos_controller where attribute="player_status"')
	rows = cur.fetchall()
	return rows[0][0]

def main():
	
	# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
	# '%(asctime)s - %(levelname)s - %(message)s'
	logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
	pafy.set_api_key('AIzaSyDScft974x9keK-q_IRpsDhFh4BQONwkOQ')
	conn = sqlite3.connect('db.sqlite3')

	# first run, assume karaoke time is just starting, clear things up from last time
	init_db(conn)

	while True:
		# check if any controls issued from ui need to be executed
		control_status = get_controller_status(conn)

		if control_status == PlayerStatus.PLAY.value and player and not player.is_playing():
			logging.info(f'Controller action - play. control_status: {control_status} player.is_playing(): {player.is_playing()}')
			control_play(conn, None)
		elif control_status == PlayerStatus.PAUSE.value and player and player.is_playing():
			logging.info(f'Controller action - pause. control_status: {control_status} player.is_playing(): {player.is_playing()}')
			control_pause(conn)
		elif control_status == PlayerStatus.STOP.value:
			logging.info(f'Controller action - stop. control_status: {control_status} player.is_playing(): {player.is_playing()}')
			play_next_video(conn)

		
		# if video is done, go to next
		if control_status == PlayerStatus.PLAY.value and (not player or not player.is_playing()):
			logging.info('Play next video')
			play_next_video(conn)


		time.sleep(3)

if __name__ == "__main__":
    main()