import time

from basic.event import EVENT_TRAIN
from basic.listener import MLListener


class MovieSheduler(object):
	
	def __init__(self):
		self.listener = MLListener([])
		self.channels = ['movie_mining']

	def get_data(self):
		print('get data...')
		
		time.sleep(3)

		print('trigger mining...')
		for c in self.channels:
			self.listener.publish(c, EVENT_TRAIN)
	

if __name__ == '__main__':
	# python lib/tasks/movielens/scheduler.py

	i = 0
	while True:
		i += 1
		print('Ready to schedule {} times'.format(i))
		scheduler = MovieSheduler()
		scheduler.get_data()
		time.sleep(20)