MAIN_PATH_NAME = "CREATURES"


def images(name, frames, left_init, right_init):
    # left
    print(f"{name.upper()}_LEFT = [", end="")
    for i in range(frames):
        print(f"load({MAIN_PATH_NAME}+'{name.lower()}_{left_init+i:02}.png')", end="")
        if i < frames - 1:
            print(end=", ")
    print("]")

    # right
    print(f"{name.upper()}_RIGHT = [", end="")
    for i in range(frames):
        print(f"load({MAIN_PATH_NAME}+'{name.lower()}_{right_init+i:02}.png')", end="")
        if i < frames - 1:
            print(end=", ")
    print("]")


images("walking_test", 1, 1, 1)
