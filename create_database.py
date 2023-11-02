from os.path import exists, abspath, join
from Engine import create_app, db
from shutil import copy
import os

backup_path = abspath("backup")
dataset_path = abspath("Engine\\recommender\\dataset")
database_path = abspath("instance\\app.db")

backup_contents = os.listdir(backup_path)
dataset_contents = os.listdir(dataset_path)

if not exists(backup_path):
    print("Backup path is missing")
    exit(1)

if not exists(dataset_path):
    print("Dateset folder is missing")
    exit(1)

if len(dataset_contents) > 0:

    # Deletes all dataset files
    for csv_file_name in dataset_contents:
        csv_file = join(dataset_path, csv_file_name)
        print(f"\n\tdeleting {csv_file}")
        os.remove(csv_file)

    dataset_contents = []
    
# If all files were deleted
if len(dataset_contents) <= 0:

    # copy all files from backup to dataset
    for backup_csv_file in backup_contents:

        if backup_csv_file == "__pycache__":
            continue

        csv_file = join(backup_path, backup_csv_file)
        print(f"\n\tcopying {csv_file}")
        copy(csv_file, dataset_path)

    database_exists: bool = exists(database_path)

    # delete old database first before running a new one
    if database_exists:
        print("\n\tDeleting database")
        os.remove(database_path)
        print("\n\tDatabase deleted")

    print("\n\tRebuilding database")
    app = create_app()

    with app.app_context():
        db.create_all()
    
    response = input("\n\tOperation completed. Start app? (Y/n): ")

    while True:

        if response in ['Y', 'y']:
            os.system("cls")
            break

        if response in ['N', 'n']:
            os.system("cls")
            exit(0)

        print("\n\tInput must either of the 4 'Y', 'y', 'N', 'n'")
        response = input("\n\tStart app? (Y/n): ")

    app = create_app()
    app.run(port=8080)