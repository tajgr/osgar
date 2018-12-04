"""
  Explore - follow a wall/obstacles
    (use 2D SICK LIDAR only)
"""
import math

import numpy as np

from osgar.node import Node


def min_dist(data):
    data = np.array(data)
    mask = (data > 0)
    if np.any(mask):
        return np.min(data[mask]) * 0.001
    return None 


def min_dist_arr(data):
    """Fake segments as in demo.py for Velodyne"""
    num = len(data)
    # laser data are anticlockwise -> swap left, right
    return min_dist(data[num/2:]), min_dist(data[:num/2])


def tangent_circle(dist, radius):
    if dist < 2 * radius:
        if dist >= radius:
            return math.asin(radius/float(dist))
        return math.radians(100)
    return None


def follow_wall_angle(laser_data, radius = 2.0):
    data = np.array(laser_data)
    mask = (data == 0)
    data[mask] = 20000
    index = np.argmin(data[:2*135])  # only right side
    dist = data[index]/1000.0
    laser_angle = math.radians((-270+index)/2.0)
    angle = tangent_circle(dist, radius)
    if angle is not None:
        # print '(%d, %.3f) %.1f' % (index, dist, math.degrees(laser_angle + angle))
        return laser_angle + angle
    return None


class FollowWall(Node):
    def __init__(self, config, bus):
        super().__init__(config, bus)


if __name__ == "__main__":
    from osgar.logger import LogWriter, LogReader
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Follow Wall')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')
    subparsers.required = True
    parser_run = subparsers.add_parser('run', help='run on real HW')
    parser_run.add_argument('config', nargs='+', help='configuration file')
    parser_run.add_argument('--note', help='add description')

    parser_replay = subparsers.add_parser('replay', help='replay from logfile')
    parser_replay.add_argument('logfile', help='recorded log file')
    parser_replay.add_argument('--force', '-F', dest='force', action='store_true', help='force replay even for failing output asserts')
    parser_replay.add_argument('--config', nargs='+', help='force alternative configuration file')
    args = parser.parse_args()

    if args.command == 'replay':
        from osgar.replay import replay
        args.module = 'app'
        game = replay(args, application=FollowWall)
        game.run()

    elif args.command == 'run':
        log = LogWriter(prefix='wall-', note=str(sys.argv))
        config = config_load(*args.config)
        log.write(0, bytes(str(config), 'ascii'))  # write configuration
        robot = Recorder(config=config['robot'], logger=log, application=FollowWall)
        game = robot.modules['app']  # TODO nicer reference
        robot.start()
        robot.join()

# vim: expandtab sw=4 ts=4 

