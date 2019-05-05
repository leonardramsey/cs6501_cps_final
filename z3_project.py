# import Solver as Solver
from z3 import *

# Curve Coverage Criteria [n_min, n_max, theta_min, theta_max, d_min, d_max]
# n_min: min number of curves
# n_max: max number of curves
# theta_min: min curvature of each curve
# theta_max: max curvature of each curve
# d_min: min distance of any two adjacent curves
# d_max: max distance of any two adjacent curves
# ---------------------------------------
# vol_min: min number of curves
# vol_max: max number of curves
# pitch_min: min curvature of each curve
# pitch_max: max curvature of each curve
# speed_min: min distance of any two adjacent curves
# speed_max: max distance of any two adjacent curves

C_g = [0, 100, 0, 100, 0, 100]  # global coverage criteria

C_l = []  # local coverage criteria
solN = 5
# Adding local coverage criteria
C_l.append([4, 7, 0, 1, 10, 14])
C_l.append([2, 7, 1, 3, 11, 15])
C_l.append([3, 9, 0, 2, 8, 12])
C_l.append([3, 8, 1, 2, 12, 20])
C_l.append([2, 10, 0, 3, 10, 15])


# Boundary Information
x_min = 0
y_min = 0
z_min = 0
x_max = 300
y_max = 300
z_max = 300

# **** consider adding rate constraint for min or max rate of change for each speech category in terms of actual value
# e.g. if we go from volume 1 to 2, then maybe we should stay on the lower end of this spectrum to make the change smoother
# or give the developer the option to constrain this change?

s = Solver()

def abs(x):
    return If(x >= 0, x, -x)

#####################################
# Complete the code
# Q1: Road Segment Generation Algorithm
#####################################
# Constraints
# vol_min <= vol <= vol_max
# pitch_min <= pitch <= pitch_max
# speed_min <= speed <= speed_max
# ** d_min <= abs(vol_prev - vol_next) d_max **
# # ** d_min <= abs(pitch_prev - pitch_next) <= d_max **
# # ** d_min <= abs(speed_prev - speed_next) <= d_max **
def speech_gen(X, Y, Z, x_min, y_min, z_min, x_max, y_max, z_max, theta_min, theta_max, d_min, d_max, N):
        # omit random number generator for this assignment as per instruction

        # X/Y/Z constraint
        for i in range(N):
            s.add(x_min <= X[i], X[i] <= x_max, y_min <= Y[i], Y[i] <= y_max, z_min <= Z[i], Z[i] <= z_max)

        # curve distance constraint
        for i in range(0,N-1):
            s.add(d_min <= X[i+1] - X[i], X[i+1] - X[i] <= d_max, d_min <= Y[i+1] - Y[i], Y[i+1] - Y[i] <= d_max,
                      d_min <= Z[i+1] - Z[i], Z[i+1] - Z[i] <= d_max)

        # curvature constraint
        for i in range(N-3):
            # 1st theta constraint
            s.add(abs(((Y[i + 1] - Y[i]) / (X[i + 1] - X[i])) -
                      ((Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1]))) >= theta_min)
            s.add(abs(((Y[i + 1] - Y[i]) / (X[i + 1] - X[i])) -
                      ((Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1]))) <= theta_max)
            # 2nd theta constraint
            s.add(abs(((Z[i + 1] - Z[i]) / (X[i + 1] - X[i])) -
                      ((Z[i + 2] - Z[i + 1]) / (X[i + 2] - X[i + 1]))) >= theta_min)
            s.add(abs(((Z[i + 1] - Z[i]) / (X[i + 1] - X[i])) -
                      ((Z[i + 2] - Z[i + 1]) / (X[i + 2] - X[i + 1]))) <= theta_max
            )

        # alternating road constraint
        for i in range(N-3):
            s.add(((Y[i + 1] - Y[i]) / (X[i + 1] - X[i])) *
                  ((Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1])) <= 0)


#####################################
# Complete the code
# Q2: Coverage Consistency Check
#####################################

# ****** this would need to be modified as well since definition of coverage has changed
def coverage_consistence(C_l, C_g, K):
    for i in range (0,K):
        ci_nmin = []
        ci_nmax = []

        ci_nmin.append(C_l[i][0])
        ci_nmax.append(C_l[i][1])

    sum_ci_min = sum(ci_nmin)
    sum_ci_max = sum(ci_nmax)
    if (K-1)+sum_ci_min < C_g[0]:
        return False
    elif (K-1)+sum_ci_max > C_g[1]:
        return False

    for i in range(0, 5):
        if C_l[i][2] < C_g[2]:
            return False
        elif C_l[i][3] > C_g[3]:
            return False
        elif C_l[i][4] < C_g[4]:
            return False
        elif C_l[i][5] > C_g[5]:
            return False
        else:
            return True

# Sequential Road Network Information
# Each array is a 2D array
# e.g. solArrayX = [[1, 2, 3], [4, 5, 6]] means the road network has 2 segments and each segment has 3 waypoints.
#      The X-coordinates of the 3 waypoints of Segment1 are 1, 2, and 3, the X-coordinates of the 3 waypoints of Segment2 are 4, 5, and 6.
# For your outputs, the size of your solArrayX/Y/Z will be (solN * N), which means your road network has solN segments, and each segment has N waypoints
# number of curves..."N" from Q1
solArrayX = []
solArrayY = []
solArrayZ = []
curNumArray = []


def main():
    # Coverage consistency check
    cov_con = coverage_consistence(C_l, C_g, solN)
    if cov_con == False:
        print("No-Sol\n")
        return 0
    else:
        #####################################
        # Complete the code
        # Q3: Sequential Road Network Generation Algorithm
        #####################################

        # this needs to be modified since this could will be called each time the behavior must be updated, so not all behaviors will be generated at once
        for sol_ind in range(solN):
            N_z3 = Int('N')
            s.add(N_z3 >= C_l[sol_ind][0], N_z3 <=C_l[sol_ind][1])
            s.check()
            if s.check() == sat:
                N = int(s.model()[N_z3].as_long())
                # generate X/Y/Z then pass to function
                X = [ Int('x_%s' % i) for i in range(N) ]
                Y = [ Int('y_%s' % i) for i in range(N) ]
                Z = [ Int('z_%s' % i) for i in range(N) ]
                speech_gen(X, Y, Z, x_min, y_min, z_min, x_max, y_max, z_max, C_l[sol_ind][2], C_l[sol_ind][3], C_l[sol_ind][4], C_l[sol_ind][5], N)
                s.check()
                model = s.model()
                solArrayX.append([model[X[i]].as_long() for i in range(N)])
                solArrayY.append([model[Y[i]].as_long() for i in range(N)])
                solArrayZ.append([model[Z[i]].as_long() for i in range(N)])
                curNumArray.append(N)
                # GLOBAL THETA CONSTRAINTS: C_g[2] = theta_min, C_g[3] = theta_max

                # rho(C_l_i+1) = And(
                # rho(C_l_i+1),
                # dead-end-current(x,y,z) == beginning-next(x,y,z),
                # does road-seg-A satisfy curvature constraint of global coverage criteria,
                # does road-seg-B satisfy curvature constraint of global coverage criteria
                s.reset()
                s.add(solArrayX[sol_ind][N-1] == X[0], solArrayY[sol_ind][N-1] == Y[0],
                      solArrayZ[sol_ind][N-1] == Z[0])
                s.add(
                    abs(((Y[0] - solArrayY[sol_ind][ N - 2])) / ((X[0] - solArrayX[sol_ind][N - 2])) -

                    ((Y[1] - solArrayY[sol_ind][N - 1])) / (X[1] - solArrayX[sol_ind][N - 1])) >= C_g[2],

                     abs(((Y[0] - solArrayY[sol_ind][N - 2])) / (X[0] - solArrayX[sol_ind][N - 2]) -

                     ((Y[1] - solArrayY[sol_ind][N - 1])) / (X[1] - solArrayX[sol_ind][N - 1])) <= C_g[3],

                   abs(((Z[0] - solArrayZ[sol_ind][N - 2])) / (X[0] - solArrayX[sol_ind][N - 2]) -

                  (((Z[1] - solArrayZ[sol_ind][N - 1])) / (X[1] - solArrayX[sol_ind][N - 1]))) >= C_g[2],

                    abs(((Z[0] - solArrayZ[sol_ind][N - 2])) / (X[0] - solArrayX[sol_ind][N - 2]) -

                   (Z[1] - solArrayZ[sol_ind][N - 1]) / (X[1] - solArrayX[sol_ind][N - 1])) <= C_g[3]

                )


    # Write the generated road information into a file
    file = open("coordinates.txt", "w")
    for seg in range(solN):
        file.write('Seg ' + str(seg + 1) + ':\n')
        for point in range(curNumArray[seg]):
            # print('solN = %d, curNumArray[seg] = %d, Seg = %d, Point = %d' % (solN, curNumArray[seg], seg, point))
            file.write(
                str(5 * int(str(solArrayY[seg][point]))) + ", 0, " + str(5 * int(str(solArrayZ[seg][point]))) + "\n")
    file.close()


    # DO NOT CHANGE THIS PART OF THE CODE
    # Additional part for generating the correct output format for visualising the generated road in Unity

    # if you wish to view the generated coordinates without alterations for Unity, just comment out
    # this last part up to if __name__ == '__main__':
    with open('coordinates.txt') as f:
        content = f.readlines()

    content = [x.strip() for x in content]
    last = ''
    to_remove = []
    for cont in content:
        if 'Seg' in cont:
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

    with open('coordinates.txt', 'w') as f:
        for item in content:
            f.write("%s\n" % item)


if __name__ == '__main__':
    main()
