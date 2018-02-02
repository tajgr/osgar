"""
  RoboOrienteering 2018 - experiments with lib.logger and robot container
"""

import argparse
import sys

from lib.logger import LogWriter, LogReader
from lib.config import Config
from drivers import all_drivers
from robot import Robot


class RoboOrienteering2018:
    def __init__(self, robot):
        self.robot = robot
        self.last_position = None
        self.cmd = (0, 0)

    def update(self):
        packet = self.robot.update()
        if packet is not None:
            print('RO', packet)
            timestamp, msg_id, data = packet
            if msg_id == 'gps':
                self.last_position = data
            elif msg_id == 'spider':  # i.e. I can drive only spider??
                self.robot.execute('spider', data)  # just echo it

    def set_speed(self, speed, angular_speed):
        self.cmd = (speed, angular_speed)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='RoboOrienteering 2018')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    subparsers.required = True
    parser_run = subparsers.add_parser('run', help='run on real HW')
    parser_run.add_argument('config', help='configuration file')
    parser_run.add_argument('--note', help='add description')

    parser_replay = subparsers.add_parser('replay', help='replay from logfile')
    parser_replay.add_argument('logfile', help='recorded log file')
    args = parser.parse_args()

    if args.command == 'replay':
        pass  # TODO
    elif args.command == 'run':
        log = LogWriter(prefix='ro2018-', note=str(sys.argv))
        config = Config.load(args.config)
        log.write(0, bytes(str(config.data), 'ascii'))  # write configuration
        robot = Robot(config=config.data['robot'], logger=log)
        robot.start()
        game = RoboOrienteering2018(robot)
        for i in range(10):
            game.update()
        game.set_speed(10, 0)
        for i in range(100):
            game.update()
        game.set_speed(0, 0)
        for i in range(10):
            game.update()
        robot.finish()
    else:
        assert False, args.command  # unsupported command

# vim: expandtab sw=4 ts=4
