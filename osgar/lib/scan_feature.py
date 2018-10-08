"""
   Laser Feature Extractor
"""
import math

def scan_split(scan, max_diff, min_len=10):
    arr = []
    prev = scan[0]
    start_i = 0
    for i, dist in enumerate(scan[1:], start=1):
        diff = abs(dist - prev)
        if diff > max_diff:
            if i - start_i >= min_len:
                arr.append((start_i, i-1))
            start_i = i
        prev = dist
    arr.append((start_i, i))
    return arr


def get_scan_diff(scan):
    prev = None
    arr = []
    for i in range(len(scan)):
        dist = scan[i]
        if prev is not None:
            diff = abs(dist - prev)
            arr.append(diff)
        prev = dist
    return arr


def extract_features(scan):
    pairs = scan_split(scan[135:-135], max_diff=20)
    pairs = [(f+135, t+135) for f, t in pairs]

    seek = len(scan)//2
    for f, t in pairs:
        if f <= seek <= t:
            return [(f, t)]
    return []


def draw_xy(scan, pairs):
    step_angle = math.radians(1/3)
    arr_x, arr_y = [], []
    for i, dist in enumerate(scan):
        angle = (len(scan)//2 - i) * step_angle
        x, y = math.cos(angle) * dist, math.sin(angle) * dist
        arr_x.append(x)
        arr_y.append(y)
    plt.plot(arr_x, arr_y, '.', linewidth=2)

    for f, t in pairs:
        plt.plot([arr_x[f], arr_x[t]], [arr_y[f], arr_y[t]], 'o-', linewidth=2)

    plt.axis('equal')
    plt.show()


if __name__ == "__main__":
    import argparse
    import matplotlib.pyplot as plt
    from osgar.logger import LogReader, lookup_stream_id
    from osgar.lib.serialize import deserialize

    parser = argparse.ArgumentParser(description='Extract features in laser scan')
    parser.add_argument('filename', help='input log file')
    parser.add_argument('--verbose', '-v', help="verbose mode", action='store_true')
    parser.add_argument('--draw', '-d', help="draw result", action='store_true')
    parser.add_argument('--index', '-i', help="scan index", type=int, default=0)
    args = parser.parse_args()

    filename = args.filename
    only_stream = lookup_stream_id(filename, 'lidar.scan')
    index = args.index
    with LogReader(filename) as log:
        for ind, row in enumerate(log.read_gen(only_stream)):
            if ind < index:
                continue
            timestamp, stream_id, data = row
            scan = deserialize(data)
            pairs = scan_split(scan[135:-135], max_diff=20)
            if args.verbose:
                for f, t in pairs:
                    print(f, t)
                    print(scan[135+f:135+t])
            pairs = [(f+135, t+135) for f, t in pairs]
#            pairs = extract_features(scan)
            if args.draw:
                draw_xy(scan, pairs)
            break


# vim: expandtab sw=4 ts=4
