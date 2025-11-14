import math
from typing import Tuple
from cm_colors.core.conversions import rgb_to_lab


def calculate_delta_e_2000(
    rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]
) -> float:
    """
    Calculate Delta E 2000 color difference with full mathematical rigor
    Most perceptually accurate color difference formula
    """
    if rgb1 == rgb2:
        return 0.0
    # Convert RGB to LAB
    L1, a1, b1 = rgb_to_lab(rgb1)
    L2, a2, b2 = rgb_to_lab(rgb2)

    # Calculate differences
    delta_L = L2 - L1
    delta_a = a2 - a1
    delta_b = b2 - b1

    # Calculate mean values
    L_mean = (L1 + L2) / 2

    # Calculate C (chroma) values
    C1 = math.sqrt(a1 * a1 + b1 * b1)
    C2 = math.sqrt(a2 * a2 + b2 * b2)
    C_mean = (C1 + C2) / 2

    # Calculate a' (adjusted a values)
    G = 0.5 * (1 - math.sqrt(pow(C_mean, 7) / (pow(C_mean, 7) + pow(25, 7))))
    a1_prime = a1 * (1 + G)
    a2_prime = a2 * (1 + G)

    # Calculate C' (adjusted chroma values)
    C1_prime = math.sqrt(a1_prime * a1_prime + b1 * b1)
    C2_prime = math.sqrt(a2_prime * a2_prime + b2 * b2)
    C_mean_prime = (C1_prime + C2_prime) / 2

    # Calculate h' (adjusted hue values)
    def calculate_hue_angle(a_prime, b):
        if a_prime == 0 and b == 0:
            return 0
        hue = math.atan2(b, a_prime) * 180 / math.pi
        return hue + 360 if hue < 0 else hue

    h1_prime = calculate_hue_angle(a1_prime, b1)
    h2_prime = calculate_hue_angle(a2_prime, b2)

    # Calculate delta h'
    delta_h_prime = 0
    if C1_prime == 0 or C2_prime == 0:
        delta_h_prime = 0
    elif abs(h2_prime - h1_prime) <= 180:
        delta_h_prime = h2_prime - h1_prime
    elif h2_prime - h1_prime > 180:
        delta_h_prime = h2_prime - h1_prime - 360
    else:
        delta_h_prime = h2_prime - h1_prime + 360

    # Calculate delta H' (capital H)
    delta_H_prime = (
        2
        * math.sqrt(C1_prime * C2_prime)
        * math.sin(math.radians(delta_h_prime / 2))
    )

    # Calculate delta C'
    delta_C_prime = C2_prime - C1_prime

    # Calculate H' mean
    H_mean_prime = 0
    if C1_prime == 0 or C2_prime == 0:
        H_mean_prime = h1_prime + h2_prime
    elif abs(h1_prime - h2_prime) <= 180:
        H_mean_prime = (h1_prime + h2_prime) / 2
    elif abs(h1_prime - h2_prime) > 180 and (h1_prime + h2_prime) < 360:
        H_mean_prime = (h1_prime + h2_prime + 360) / 2
    else:
        H_mean_prime = (h1_prime + h2_prime - 360) / 2

    # Calculate T (hue-dependent factor)
    T = (
        1
        - 0.17 * math.cos(math.radians(H_mean_prime - 30))
        + 0.24 * math.cos(math.radians(2 * H_mean_prime))
        + 0.32 * math.cos(math.radians(3 * H_mean_prime + 6))
        - 0.20 * math.cos(math.radians(4 * H_mean_prime - 63))
    )

    # Calculate delta theta
    delta_theta = 30 * math.exp(-pow((H_mean_prime - 275) / 25, 2))

    # Calculate RC (rotation factor)
    RC = 2 * math.sqrt(
        pow(C_mean_prime, 7) / (pow(C_mean_prime, 7) + pow(25, 7))
    )

    # Calculate SL, SC, SH (weighting functions)
    SL = 1 + (
        (0.015 * pow(L_mean - 50, 2)) / math.sqrt(20 + pow(L_mean - 50, 2))
    )
    SC = 1 + 0.045 * C_mean_prime
    SH = 1 + 0.015 * C_mean_prime * T

    # Calculate RT (rotation term)
    RT = -math.sin(math.radians(2 * delta_theta)) * RC

    # Calculate final Delta E 2000
    # Using standard weighting factors (kL=1, kC=1, kH=1)
    kL = kC = kH = 1.0

    delta_E_2000 = math.sqrt(
        pow(delta_L / (kL * SL), 2)
        + pow(delta_C_prime / (kC * SC), 2)
        + pow(delta_H_prime / (kH * SH), 2)
        + RT * (delta_C_prime / (kC * SC)) * (delta_H_prime / (kH * SH))
    )

    return delta_E_2000


# def oklch_color_distance(oklch1: Tuple[float, float, float], oklch2: Tuple[float, float, float]) -> float:
#     """
#     Calculate perceptual distance between two OKLCH colors
#     More accurate than RGB distance for perceptual uniformity
#     """
#     L1, C1, H1 = oklch1
#     L2, C2, H2 = oklch2

#     # Convert to Cartesian coordinates for proper distance calculation
#     a1 = C1 * math.cos(H1 * math.pi / 180)
#     b1 = C1 * math.sin(H1 * math.pi / 180)
#     a2 = C2 * math.cos(H2 * math.pi / 180)
#     b2 = C2 * math.sin(H2 * math.pi / 180)

#     # Euclidean distance in OKLab space
#     delta_L = L2 - L1
#     delta_a = a2 - a1
#     delta_b = b2 - b1

#     return math.sqrt(delta_L * delta_L + delta_a * delta_a + delta_b * delta_b)
