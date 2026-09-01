import numpy as np
import math
from itertools import combinations
from scipy.spatial import ConvexHull
from tqdm import tqdm

def transform_points(p1, p2):
    x = (p1[0],p2[0])
    y = (p1[1],p2[1])
    return x, y

def circle(center, radius):
    theta = np.linspace(-np.pi, np.pi, 100)
    xc, yc = center
    x = xc + radius * np.cos(theta)
    y = yc + radius * np.sin(theta)
    return x, y

def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y

def midpoint_of_line(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    center = (mid_x, mid_y)
    return center

def circle_line_intersect(circle_center, circle_radius, line):
    # Line direction vector
    h, k = circle_center

    (x1, y1), (x2, y2) = line

    dx = x2 - x1
    dy = y2 - y1

    # Convert to line equation coefficients: Ax + By + C = 0
    A = dy
    B = -dx
    C = dx * y1 - dy * x1

    # Distance from circle center to the line
    d = abs(A*h + B*k + C) / math.sqrt(A*A + B*B)

    if d < circle_radius:
        return True # "The line intersects the circle (two points)."
    elif d == circle_radius:
        return True # "The line is tangent to the circle (one point)."
    else:
        return False # "The line does not intersect the circle."

def median_combinations(median_segments):
    valid_combs = []
    all_combs = list(combinations(median_segments,2))
    for comb in all_combs:
        l1, l2 = comb
        p1, p2 = l1
        if p1 in l2:
            valid_combs.append(comb)
            continue
        if p2 in l2:
            valid_combs.append(comb)
            continue
    return valid_combs

def comb_to_same_start(comb):
    c1, c2 = comb
    if c1[0] == c2[0]:
        new_comb = comb
    elif c1[0] == c2[1]:
        new_comb = (c1, (c2[1], c2[0]))
    elif c1[1] == c2[0]:
        new_comb = ((c1[1], c1[0]), c2)
    elif c1[1] == c2[1]:
        new_comb = ((c1[1], c1[0]), (c2[1],c2[0]))
    return new_comb

def angle_between_vectors(l1, l2):
    l1, l2 = comb_to_same_start((l1, l2))
    p1, p2 = l1
    p3, p4 = l2
    v1 = np.array([p2[0]-p1[0], p2[1]-p1[1]])
    v2 = np.array([p4[0]-p3[0], p4[1]-p3[1]])
    
    angle = abs(np.arctan2(v1[1], v1[0]) - np.arctan2(v2[1],  v2[0]))
    if angle < np.pi:
        angle_bigger_pi = False # False
    else:
        angle_bigger_pi = True # True
    angle = angle%np.pi
    return angle, angle_bigger_pi

def orthogonal_connection_exists(P, A, B):
    """
    A, B, P are 2D points as numpy arrays, e.g. np.array([x, y])
    Returns True if the perpendicular projection of P onto AB
    lies within the segment AB.
    """

    A = np.array(A)
    B = np.array(B)

    AB = B - A
    AP = P - A

    # Squared length of AB
    AB_len2 = np.dot(AB, AB)
    if AB_len2 == 0:
        return False  # A and B are the same point

    # Projection parameter t
    t = np.dot(AP, AB) / AB_len2

    # Check if projection lies on the segment
    return 0 <= t <= 1

def side_of_segment(p, a, b, only_in_bounds=True):
    """
    Classifies point p relative to the directed segment a→b.

    Returns:
        "left"         → p is left of the segment
        "right"        → p is right of the segment
        "on"           → p lies exactly on the segment line
        "out_of_bounds"→ perpendicular projection is not between a and b
    """
    # Vector ab and ap
    AB = (b[0] - a[0], b[1] - a[1])
    AP = (p[0] - a[0], p[1] - a[1])

    if only_in_bounds:
        in_bounds = orthogonal_connection_exists(p, a, b)
        if not in_bounds:
            return "out_of_bounds"

    # Cross product to determine left/right/on
    cross = AB[0]*AP[1] - AB[1]*AP[0]
    
    if cross > 0:
        return "left"
    elif cross < 0:
        return "right"
    else:
        return "on"

def get_median_lines(points, only_in_bounds=True):
    majority = len(points)//2 + 1

    median_lines = []

    point_combs = list(combinations(points,2))
    for pc in point_combs: 
        right_counter = 0
        left_counter = 0
        for p in points:
            if p in pc:
                continue
            s = side_of_segment(p, *pc, only_in_bounds=only_in_bounds)
            if s == "left":
                left_counter += 1
            elif s == "right":
                right_counter += 1
            elif s == "on":
                left_counter += 1
                right_counter += 1
        left_counter += 2
        right_counter += 2
        if left_counter >= majority and right_counter >= majority:
            median_lines.append(pc)
    return median_lines

def yolk(points, accuracy=0.1, start_yolk_radius=100000, start_yolk_center=[]):
    median_lines = get_median_lines(points, only_in_bounds=False)
    # Check if all median lines share a point.
    potential_common = median_lines[0][0]
    potential_common_sum = sum([True for l in median_lines if potential_common in l])
    if potential_common_sum == len(median_lines):
        yolk_center, yolk_radius = potential_common, 0
        print("All median lines share a point. Yolk radius is 0.")
        return yolk_center, yolk_radius
    else:
        potential_common = median_lines[0][1]
        potential_common_sum = sum([True for l in median_lines if potential_common in l])
        if potential_common_sum == len(median_lines):
            yolk_center, yolk_radius = potential_common, 0
            print("All median lines share a point. Yolk radius is 0.")
            return yolk_center, yolk_radius

    # Bin mir immer noch unsicher welche median combinations ausreichend sind. 4 ist recht willkürlich gewählt.
    mcombs = median_combinations(median_lines)
    if True: #len(mcombs) < 4:
        new_lines = []
        all_mcombs = list(combinations(median_lines,2))
        for l1, l2 in all_mcombs:
            try:
                comb_to_same_start((l1, l2))
            except:
                intersect = line_intersection(l1,l2)
                new_lines.append((intersect, l1[0]))
                new_lines.append((intersect, l2[0]))
                new_lines.append((intersect, l1[1]))
                new_lines.append((intersect, l2[1]))
        mcombs = list(combinations(new_lines, 2)) + mcombs

    points_comb = list(combinations(np.array(points),2))
    dists = [np.linalg.norm(pc[0]-pc[1]) for pc in points_comb]
    max_dist = max(dists)
    dists_to_check = np.arange(accuracy, max_dist, accuracy)

    yolk_radius = start_yolk_radius
    yolk_center = start_yolk_center
    for comb in tqdm(mcombs):
        try:
            comb = comb_to_same_start(comb)
        except:
            continue

        angle, angle_bigger_pi = angle_between_vectors(*comb)

        c1, c2 = comb
        c1 = np.array(c1) 
        c2 = np.array(c2)
        r1 = np.array([c1[1]-c1[0],c1[1]-c1[0]]) 
        r2 = np.array([c2[1]-c2[0],c2[1]-c2[0]])

        angle_vector = 1/2 * (r1/np.linalg.norm(r1) + r2/np.linalg.norm(r2))
        angle_vector = angle_vector/np.linalg.norm(angle_vector)
        
        median_lines_to_cross = [ml for ml in median_lines if ml not in comb]

        for distance in dists_to_check:
            circle_center = (c1[0] + distance * angle_vector)[0]
            if not angle_bigger_pi:
                circle_radius = np.sin(angle/2) * distance * 1/np.sqrt(2) # sin
            else:
                circle_radius = np.cos(angle/2) * distance * 1/np.sqrt(2) # cos
            intersections_check = [circle_line_intersect(circle_center, circle_radius, ml) for ml in median_lines_to_cross]
            if sum(intersections_check) == len(median_lines_to_cross):
                if circle_radius < yolk_radius:
                    yolk_radius = circle_radius
                    yolk_center = circle_center     
    return yolk_center, yolk_radius

def calculate_yolk(points, accuracy=0.1):
    points = list(dict.fromkeys(points)) # delete duplicate points    
    
    ### Check points is just one single point.
    if len(points) == 1:
        yolk_center = points[0]
        yolk_radius = 0
        return yolk_center, yolk_radius
    
    ### Check if points vary in 1D only.
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    if len(set(x)) <= 1:
        yolk_center = (x[0], np.mean(y))
        yolk_radius = 0
        print("Parties vary in 1D only. Yolk radius is 0.")
        return yolk_center, yolk_radius
    if len(set(y)) <= 1:
        yolk_center = (np.mean(x), y[0])
        yolk_radius = 0
        print("Parties vary in 1D only. Yolk radius is 0.")
        return yolk_center, yolk_radius

    if len(points) == 2:
        yolk_center, yolk_radius = midpoint_of_line(points[0], points[1]), 0
        print("Yolk is Midpoint. Yolk radius is 0.")
    elif len(points) > 2:
        start_yolk_radius = 1000000
        start_yolk_center = []
        yolk_center, yolk_radius = yolk(points, accuracy=accuracy, start_yolk_radius=start_yolk_radius, start_yolk_center=start_yolk_center)
        if yolk_radius == start_yolk_radius:
            print("Starting approximation...")
            outer_points = [points[i] for i in ConvexHull(points).vertices]
            inner_points = [p for p in points if p not in outer_points]
            for i in range(1,len(inner_points)+1):
                points_to_delete = inner_points[:i]
                reduced_points = [p for p in points if p not in points_to_delete]
                yolk_center, yolk_radius = yolk(reduced_points, accuracy=accuracy, start_yolk_radius=start_yolk_radius, start_yolk_center=start_yolk_center)
                if yolk_radius != start_yolk_radius:
                    break
    else:
        yolk_center, yolk_radius = [], 0

    return yolk_center, yolk_radius