import os

def generate_file_tree(directory, excluded_items, prefix='', is_last=False):

    items = os.listdir(directory)

    if is_last:
        prefix += ' ' * 4
    else:
        prefix += '|   '

    for index, item in enumerate(items):
        
        is_last_item = index == len(items) - 1
        item_path = os.path.join(directory, item)
        
        if os.path.isdir(item_path) == False:

            if item in excluded_items:
                continue

            if is_last_item:
                print(prefix + '└-- ' + item)
                continue
            
            print(prefix + '|-- ' + item)
            continue
        
        if item not in excluded_items:
            if is_last_item:
                print(prefix + '└-- ' + item)
            else:
                print(prefix + '|-- ' + item + '/')
            
            generate_file_tree(item_path, excluded_items, prefix, is_last_item)

if __name__ == "__main__":
    starting_directory = "."  # Change this to the directory you want to start from
    excluded_items = ['__pycache__', 'env', 'icons', '.gitignore', '.vscode', '.git']  # Note the removal of the double underscores
    print(starting_directory)
    generate_file_tree(starting_directory, excluded_items)
