import os
import tqdm
import shutil

DATA_PATH = "data"
PREPARED_DATA_PATH = "."
GT_FILES = [
    "brock200_1", 
    "brock200_2", 
    "brock200_3", 
    "brock200_4", 
    "C125.9", 
    "gen200_p0.9_44",
    "gen200_p0.9_55",
    "hamming8-4",
    "johnson16-2-4",
    "johnson8-2-4",
    "keller4",
    "MANN_a27",
    "MANN_a9",
    "p_hat1000-1",
    "p_hat1500-1",
    "p_hat300-3",
    "san1000",
    "sanr200_0.9"]


def check_file(file_name: str) -> bool:
    for gt_file in GT_FILES:
        if gt_file in file_name:
            return True
    return False

if __name__ == "__main__":
    dir_path = os.path.join(PREPARED_DATA_PATH, "prepared_data")
    if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    os.mkdir(dir_path)
    for file_name in tqdm.tqdm(os.listdir(DATA_PATH), total=len(os.listdir(DATA_PATH))):
        if not check_file(file_name=file_name):
            continue
        file_new_name = file_name[:file_name.rfind(".")]
        file_new_dir = os.path.join(dir_path, file_new_name)
        if os.path.exists(file_new_dir):
            shutil.rmtree(file_new_dir)
        os.mkdir(file_new_dir)
        file_path = os.path.join(DATA_PATH, file_name)
        with open(file_path, errors="replace") as f:
            row = ""
            while row.find("p edge") == -1 and row.find("p col") == -1:
                row = f.readline()
            new_file = os.path.join(file_new_dir, file_new_name + ".txt")
            with open(new_file, "w+") as f_new:
                info = [e.split()[-2:] for e in f.read().split("\n")]
                print(" ".join(row.split()[-2:]), file=f_new)
                for e in info:
                    print(" ".join(e), file=f_new)