import json
import os


def generate_study_links(root_dir=".", exclude_dirs=None, extensions=None):
    """_summary_

    Args:
        root_dir (str, optional): 루트 디렉토리. Defaults to ".".
        exclude_dirs (list, optional): 제외할 디렉토리. Defaults to None.
        extensions (list, optional): 확장자. Defaults to None.
    """
    if exclude_dirs is None:
        exclude_dirs = [".git", "node_modules", "__pycache__", ".idea"]

    if extensions is None:
        extensions = [".md", ".py"]

    result = ["# 공부 자료 목록\n"]
    structure = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # 제외 디렉토리 건너뛰기
        dirnames[:] = [
            d for d in dirnames if d not in exclude_dirs and not d.startswith(".")
        ]
        # print(f"dirnames: {dirnames}")

        # README.md 파일은 제외
        relevant_files = [
            f for f in filenames if f.endswith(tuple(extensions)) and f != "README.md"
        ]
        # print(f"relevant_files: {relevant_files}")

        if not relevant_files:
            continue

        # 디렉토리 경로를 파싱하여 구조 만들기
        path_parts = dirpath.replace("\\", "/").lstrip("./").split("/")
        # print(f"path_parts: {path_parts}")

        # 빈 루트 경로 처리
        if path_parts[0] == "":
            path_parts = path_parts[1:]

        if not path_parts:  # 루트 디렉토리는 건너뛰기
            continue

        # 경로를 구조에 추가
        current = structure
        for part in path_parts:
            if part not in current:
                current[part] = {"files": [], "dirs": {}}
            current = current[part]["dirs"]

        # 파일 추가
        for filename in relevant_files:
            file_path = os.path.join(dirpath, filename).replace("\\", "/")
            if file_path.startswith("./"):
                file_path = file_path[2:]

            current_level = structure
            for part in path_parts:
                current_level = current_level[part]["dirs"]

            # 파일 경로와 이름 저장
            current_level = structure
            for i, part in enumerate(path_parts):
                if i == len(path_parts) - 1:  # 마지막 디렉토리
                    current_level[part]["files"].append(
                        {"name": filename, "path": file_path}
                    )
                else:
                    current_level = current_level[part]["dirs"]

    # 구조를 마크다운으로 변환
    def build_markdown(struct, level=2):
        md = []
        print(f"struct: {json.dumps(struct, indent=4)}")

        # 최상위 디렉토리 정렬
        for dir_name in sorted(struct.keys()):
            dir_data = struct[dir_name]

            # 디렉토리 제목
            title_str = f"{'#' * level} {dir_name.title()}"
            if level <= 3:
                md.append(title_str)
            else:
                md.append(f"- {title_str}")

            # 파일 목록 추가
            files = sorted(dir_data["files"], key=lambda x: x["name"])
            for file in files:
                file_name = os.path.splitext(file["name"])[0]
                file_path = file["path"].replace(" ", "%20")
                if level <= 3:
                    md.append(f"- [{file_name}]({file_path})")
                else:
                    md.append(f"  - [{file_name}]({file_path})")

            # 하위 디렉토리가 있으면 재귀적으로 처리
            subdirs = dir_data["dirs"]
            if subdirs:
                md.append(build_markdown(subdirs, level + 1))

            md.append("")  # 공백 라인 추가

        return "\n".join(md)

    result.append(build_markdown(structure))
    return "\n".join(result)


# README.md 파일 업데이트
def update_readme():
    """_summary_

    Returns:
        None
    """
    readme_path = "README.md"
    study_links = generate_study_links()

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(study_links)

    print(f"README.md 파일이 업데이트되었습니다.")


if __name__ == "__main__":
    update_readme()
