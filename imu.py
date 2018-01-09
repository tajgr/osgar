"""
  Simple IMU data analysis
"""


def parse_line(line):
    assert line.startswith('$VNYMR'), line
    assert '*' in line, line
    s = line.split('*')[0].split(',')
    assert len(s) == 13, s
    arr = [float(x) for x in s[1:]]
    return arr[:3], arr[3:6], arr[6:9], arr[9:]


if __name__ == "__main__":
    import io
    import sys
    import matplotlib.pyplot as plt
    
    arr = []
    for line in io.open(sys.argv[1]):
        angle, mag, acc, gyro = parse_line(line)
        arr.append(angle)

    plt.plot(arr, 'o-', linewidth=2)
    plt.show()

# vim: expandtab sw=4 ts=4
