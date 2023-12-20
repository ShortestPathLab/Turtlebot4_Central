import numpy as np # type: ignore

def rotate(x, y, radians):
    return (x*np.cos(radians) - y*np.sin(radians), x*np.sin(radians) + y*np.cos(radians))

if __name__ == "__main__":
    print(rotate(0.5, 0.5, 3.0815))
    # (-15.4613, 1.29542)
