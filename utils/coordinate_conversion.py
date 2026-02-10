import numpy as np
from numpy.typing import NDArray


def spherical_to_cartesian(
    dist: float, azimuth_deg: float, elevation_deg: float
) -> NDArray[np.float64]:
    """
    Convert spherical coordinates to Cartesian.

    Args:
        dist: Distance from origin (meters)
        azimuth_deg: Horizontal angle, 0° = +x, 90° = +y (degrees)
        elevation_deg: Vertical angle, 0° = horizontal, 90° = up (degrees)

    Returns:
        np.array([x, y, z]) in meters
    """
    az = np.deg2rad(azimuth_deg)
    el = np.deg2rad(elevation_deg)

    x = dist * np.cos(el) * np.cos(az)
    y = dist * np.cos(el) * np.sin(az)
    z = dist * np.sin(el)

    return np.array([x, y, z])


def cartesian_to_spherical(x: float, y: float, z: float) -> NDArray[np.float64]:
    """
    Convert Cartesian coordinates to spherical.

    Args:
        x: X coordinate (meters)
        y: Y coordinate (meters)
        z: Z coordinate (meters)

    Returns:
        np.array([range, azimuth, elevation])
        - range in meters
        - azimuth in degrees, 0° = +x, 90° = +y
        - elevation in degrees, 0° = horizontal, 90° = up
    """
    r = np.sqrt(x**2 + y**2 + z**2)

    if r < 1e-6:
        return np.array([0.0, 0.0, 0.0])

    az = np.degrees(np.arctan2(y, x))
    el = np.degrees(np.arcsin(z / r))

    return np.array([r, az, el])
