from pathlib import Path

def main():
    # 1. Filesystem basics
    # 1.1. Creating a path
    current_path = Path('.')
    print(current_path)
    print(current_path.resolve())

    # 1.2. Checking a path exists
    print(f'Path {current_path} exists: {current_path.exists()}')

    # 1.3. Checking a path is a file
    if current_path.is_file():
        print(f'{current_path} is a file')
    else:
        print(f'{current_path} is not a file')

    # 1.3. Checking a path is a directory
    if current_path.is_dir():
        print(f'{current_path} is a directory')
    else:
        print(f'{current_path} is not a directory')

    # 1.4. Better way to build scalable paths - is to start from the current Python module
    current_path = Path(__file__)
    print(current_path)

    current_directory_path = current_path.parent
    print(current_directory_path)

    # 1.5. Building paths with a slash
    target_score_path = current_path.parent.parent.parent / 'config' / 'target_score.txt'

    if target_score_path.exists():
        with open(target_score_path) as f:
            print(f.read())
    else:
        print('No such file!')

    # 1.6. Find files by extension



if __name__ == '__main__':
    main()
