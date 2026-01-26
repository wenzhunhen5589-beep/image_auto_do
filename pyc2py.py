import os
import subprocess

def convert_pyc_to_py(root_directory):
    for dirpath, dirnames, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_file_path = os.path.join(dirpath, filename)
                py_file_name = filename[:-1]  # 去掉 .pyc 后缀
                py_file_path = os.path.join(dirpath, py_file_name)

                try:
                    print(f'Converting: {pyc_file_path}')
                    with open(py_file_path, 'w') as py_file:
                        subprocess.run([r'C:\Users\TEST\AppData\Roaming\Python\Python36\Scripts\uncompyle6.exe', pyc_file_path], stdout=py_file, check=True)
                    print(f'Converted: {pyc_file_path} to {py_file_path}')
                except subprocess.CalledProcessError as e:
                    print(f'Error converting {pyc_file_path}: {e}')
                except Exception as e:
                    print(f'An error occurred while processing {pyc_file_path}: {e}')
def delete_py_files_if_pyc_exists(root_directory):
    # 遍历根目录及��子目录
    for dirpath, dirnames, filenames in os.walk(root_directory):
        # 用于存储.py文件和.pyc文件的名字
        py_files = {filename[:-3] for filename in filenames if filename.endswith('.py')}
        pyc_files = {filename[:-4] for filename in filenames if filename.endswith('.pyc')}

        # 找到同名的.py文件，并删除它们
        for py_file in py_files:
            if py_file in pyc_files:
                py_file_path = os.path.join(dirpath, f"{py_file}.py")
                try:
                    os.remove(py_file_path)
                    print(f'Deleted: {py_file_path}')
                except Exception as e:
                    print(f'Error deleting {py_file_path}: {e}')
if __name__ == '__main__':
    # root_dir = input("请输入根目录路径: ")
    root_dir ="C:\ocr"
    # delete_py_files_if_pyc_exists(root_dir)
    convert_pyc_to_py(root_dir)
