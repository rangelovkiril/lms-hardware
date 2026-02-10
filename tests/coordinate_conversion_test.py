from utils.coordinate_conversion import cartesian_to_spherical, spherical_to_cartesian

if __name__ == "__main__":
    # Test 1: Straight ahead
    x, y, z = spherical_to_cartesian(10, 0, 0)
    print(f"Test 1: x={x:.3f}, y={y:.3f}, z={z:.3f}")
    # Expected: (10, 0, 0)

    # Test 2: 45° right
    x, y, z = spherical_to_cartesian(10, 45, 0)
    print(f"Test 2: x={x:.3f}, y={y:.3f}, z={z:.3f}")
    # Expected: (7.07, 7.07, 0)

    # Test 3: Straight up
    x, y, z = spherical_to_cartesian(10, 0, 90)
    print(f"Test 3: x={x:.3f}, y={y:.3f}, z={z:.3f}")
    # Expected: (0, 0, 10)

    # Test 4: Round-trip conversion
    r, az, el = cartesian_to_spherical(7.07, 7.07, 0)
    print(f"Test 4: r={r:.3f}, az={az:.3f}, el={el:.3f}")
    # Expected: (10, 45, 0)

    # Test 5: Another round-trip
    r, az, el = cartesian_to_spherical(10, 0, 0)
    print(f"Test 5: r={r:.3f}, az={az:.3f}, el={el:.3f}")
    # Expected: (10, 0, 0)
