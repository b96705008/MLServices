import redis

from event import EVENT_TRAIN, EVENT_NEW, EVENT_KILL
from utils.env import logger


class MLListener(object):
    def __init__(self, channel, r=None):
        self.channel = channel

        if r is None:
            self.redis = redis.Redis()
        else:
            self.redis = r

        self.pubsub = self.redis.pubsub()
        self.subscribe(self.channel)

    def get_channel(self):
        return self.channel

    def listen(self):
        for item in self.pubsub.listen():
            yield item

    def publish(self, channel, event):
        self.redis.publish(channel, event)

    def unsubscribe(self):
        self.pubsub.unsubscribe()
        logger.info('{} tries to unsubscribe the channelds successfully'.format(type(self).__name__))

    def subscribe(self, channel):
        self.pubsub.subscribe(channel)
