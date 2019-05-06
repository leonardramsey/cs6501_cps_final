# import Solver as Solver
from z3 import *

# ------ Speech Coverage Criteria ------
# 0: vol_min: min volume amount
# 1: vol_max: max volume amount
# 2: pitch_min: min pitch amount
# 3: pitch_max: max pitch amount
# 4: speed_min: min speed amount
# 5: speed_max: max speed amount
# 6: vol_d_min: min distance between vol
# 7: vol_d_max: max distance between vol
# 8: pitch_d_min: min distance between vol
# 9: pitch_d_max: max distance between vol
# 10: speed_d_min: min distance between vol
# 11: speed_d_max: max distance between vol

C_g = [0, 100, 0, 100, 0, 100, 0, 20, 0, 10, 0, 5]  # global coverage criteria
N = 2

# Boundary Information
vol_min = 0
pitch_min = 0
speed_min = 0
vol_max = 100
pitch_max = 100
speed_max = 100

s = Optimize()

def abs(x):
    return If(x >= 0, x, -x)

# Constraints
# vol_min <= volume <= vol_max
# pitch_min <= pitch <= pitch_max
# speed_min <= speed <= speed_max
# vol_d_min <= abs(vol_prev - vol_next) <= vol_d_max
# pitch_d_min <= abs(pitch_prev - pitch_next) <= pitch_d_max
# speed_d_min <= abs(speed_prev - speed_next) <= speed_d_max

def speech_gen(prev_speech, volume, pitch, speed, vol_min, vol_max, pitch_min, pitch_max, speed_min, speed_max, vol_d_min, vol_d_max, pitch_d_min, pitch_d_max, speed_d_min, speed_d_max):
        # omit random number generator for this assignment as per instruction

        # volume/pitch/speed constraint
        s.add(vol_min <= volume[0], volume[0] <= vol_max,
              pitch_min <= pitch[0], pitch[0] <= pitch_max,
              speed_min <= speed[0], speed[0] <= speed_max)

        # attribute distance constraint
        s.add(vol_d_min <= abs(volume[0] - prev_speech[0]), abs(volume[0] - prev_speech[0]) <= vol_d_max,
              pitch_d_min <= abs(pitch[0] - prev_speech[1]), abs(pitch[0] - prev_speech[1]) <= pitch_d_max,
              speed_d_min <= abs(speed[0] - prev_speech[2]), abs(speed[0] - prev_speech[2]) <= speed_d_max)

        # # for increase vol...
        # s.add(prev_speech[0] <= volume[0])
        #
        # # for decrease vol...
        # s.add(prev_speech[0] >= volume[0])
        #
        # # for increase pitch...
        # s.add(prev_speech[1] <= pitch[0])
        #
        # # for decrease pitch...
        # s.add(prev_speech[1] >= pitch[0])
        #
        # # for increase speed
        # s.add(prev_speech[2] <= speed[0])
        #
        # # for decrease speed
        # s.add(prev_speech[2] >= speed[0])

def coverage_consistence(C_l, C_g):
    if C_l[0] < C_g[0]: # vol_min
        return False
    elif C_l[1] > C_g[1]: # vol_max
        return False
    elif C_l[2] < C_g[2]: # pitch_min
        return False
    elif C_l[3] > C_g[3]: # pitch_max
        return False
    elif C_l[4] < C_g[4]: # speed_min
        return False
    elif C_l[5] > C_g[5]: # speed_max
        return False
    else:
        return True


# Each array is a 2D array
# e.g. solArrayVol = [[1, 2, 3], [4, 5, 6]] means the road network has 2 segments and each segment has 3 waypoints.
#      The X-coordinates of the 3 waypoints of Segment1 are 1, 2, and 3, the X-coordinates of the 3 waypoints of Segment2 are 4, 5, and 6.
# For your outputs, the size of your solArrayVol/Y/Z will be (solN * N), which means your road network has solN segments, and each segment has N waypoints
# number of curves..."N" from Q1
solArrayVol = []
solArrayPitch = []
solArraySpeed = []
curNumArray = []


def main():
    # Coverage consistency check
    print('global criteria')
    print(C_g)
    C_l = [30, 90, 25, 80, 0, 80]
    print('local criteria')
    print(C_l)
    prev_speech = [75, 50, 40]  # prev_vol, prev_pitch, prev_speed
    print('previous speech')
    print(prev_speech)
    cov_con = coverage_consistence(C_l, C_g)
    if cov_con == False:
        print("Error: Coverage consistency check failed. No New Solution could be generated.\n")
        return prev_speech
    else:
        # this needs to be modified since this could will be called each time the behavior must be updated, so not all behaviors will be generated at once

        volume = [ Int('vol_%s' % i) for i in range(1) ]
        pitch = [ Int('pitch_%s' % i) for i in range(1) ]
        speed = [ Int('speed_%s' % i) for i in range(1) ]
        print('init volume')
        print(volume)
        print('init pitch')
        print(pitch)
        print('init speed')
        print(speed)
        speech_gen(prev_speech, volume, pitch, speed,
                   C_l[0], C_l[1], C_l[2], C_l[3], C_l[4], C_l[5],
                   C_g[6], C_g[7], C_g[8], C_g[9], C_g[10], C_g[11])
        print('Solver')
        print(s)
        s.check()
        model = s.model()
        solArrayVol.append([model[volume[0]].as_long()])
        solArrayPitch.append([model[pitch[0]].as_long()])
        solArraySpeed.append([model[speed[0]].as_long()])

        curNumArray.append(N)
        # s.reset()
        # s.add(solArrayVol[sol_ind][N - 1] == volume[0], solArrayPitch[sol_ind][N - 1] == pitch[0],
        #       solArraySpeed[sol_ind][N - 1] == speed[0])
        # s.add(
        #     abs(((pitch[0] - solArrayPitch[sol_ind][N - 2])) / ((volume[0] - solArrayVol[sol_ind][N - 2])) -
        #
        #         ((pitch[1] - solArrayPitch[sol_ind][N - 1])) / (volume[1] - solArrayVol[sol_ind][N - 1])) >= C_g[2],
        #
        #     abs(((pitch[0] - solArrayPitch[sol_ind][N - 2])) / (volume[0] - solArrayVol[sol_ind][N - 2]) -
        #
        #         ((pitch[1] - solArrayPitch[sol_ind][N - 1])) / (volume[1] - solArrayVol[sol_ind][N - 1])) <= C_g[3],
        #
        #     abs(((speed[0] - solArraySpeed[sol_ind][N - 2])) / (volume[0] - solArrayVol[sol_ind][N - 2]) -
        #
        #         (((speed[1] - solArraySpeed[sol_ind][N - 1])) / (volume[1] - solArrayVol[sol_ind][N - 1]))) >= C_g[2],
        #
        #     abs(((speed[0] - solArraySpeed[sol_ind][N - 2])) / (volume[0] - solArrayVol[sol_ind][N - 2]) -
        #
        #         (speed[1] - solArraySpeed[sol_ind][N - 1]) / (volume[1] - solArrayVol[sol_ind][N - 1])) <= C_g[3]
        #
        #     )

    print('final solArrayVol')
    print(solArrayVol)
    print('final solArrayPitch')
    print(solArrayPitch)
    print('final solArraySpeed')
    print(solArraySpeed)
    # Write the generated road information into a file
    file = open("speech.txt", "w")
    # for seg in range(N):
    file.write('Speech ' + str(0 + 1) + ':\n')
        # for point in range(curNumArray[seg]):
    file.write(
        str(solArrayVol[0][0]) + ',' + str(solArrayPitch[0][0]) + ',' + str(solArraySpeed[0][0]) + "\n")
    file.close()


    # DO NOT CHANGE THIS PART OF THE CODE
    # Additional part for generating the correct output format for visualising the generated road in Unity

    # if you wish to view the generated coordinates without alterations for Unity, just comment out
    # this last part up to if __name__ == '__main__':
    with open('speech.txt') as f:
        content = f.readlines()

    content = [x.strip() for x in content]
    last = ''
    to_remove = []
    for cont in content:
        if 'Speech' in cont:
            to_remove.append(cont)

    for rem in to_remove:
        content.remove(rem)

    to_remove = []
    for cont in content:
        if last == cont:
            to_remove.append(cont)
        last = cont

    for rem in to_remove:
        content.remove(rem)

    with open('speech.txt', 'w') as f:
        for item in content:
            f.write("%s\n" % item)


if __name__ == '__main__':
    main()
