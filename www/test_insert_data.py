#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import orm
import asyncio
from models import User, Blog, Comment

async def test(loop):
	await orm.create_pool(loop=loop, host='127.0.0.1', user='root', password='123456', db='awesome')

	u = User(name='Test', email='test2@example.com', passwd='1234567890', image='about:blank')

	await u.save()
	# await orm.destory_pool()
if __name__ == '__main__':

	loop = asyncio.get_event_loop()
	loop.run_until_complete(test(loop))
	print('Test finished')
	# loop.close()