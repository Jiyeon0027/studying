# Chapter 9. 테스트 하기

- CI/CD 파이프라인에서 Airflow테스트 하기
- pytest로 테스트하기 위한 프로젝트 구성하기
- 템플릿을 적용한 테스트 태스크를 위한 DAG 실행 시뮬레이션하기
- 목업으로 외부 시스템 조작하기
- 컨테이너를 사용하여 외부 시스템에서 동작 테스트 하기

---

### 9.1 테스트 시작하기

- 개별테스크 단위로 단위 테스트
- 통합 테스트
- 승인 테스트

모든 CI/CD 시스템은 프로젝트 디렉터리의 루트에 YAML형식으로 파이프라인을 정의하여 작동함

### 9.1.1 모든 DAG에 대한 무결성 테스트

- DAG 무결성 테스트는 간단한 실수를 borken Dag로 표시해줌
- 순환오류를 포착하는 예시

pytest를 사용하는 방법 </br>
tests/ 디렉토리 아레에 기존 구조를 따라 그대로 적용하여 테스트 test\_접두사를 사용

```python

import glob
import importlib.util
import os

import pytest
from airflow.models import DAG

# DAG 파일을 보관하는 디렉터리 -> py 파일들 반복적 탐색
DAG_PATH = os.path.join(
   os.path.dirname(__file__), "..", "..", "dags/**/*.py"
)
DAG_FILES = glob.glob(DAG_PATH, recursive=True)

# DAG_FILE 안에 있는 모든 DAGS에 대해 테스트
@pytest.mark.parametrize("dag_file", DAG_FILES) # decorator
def test_dag_integrity(dag_file):
   module_name, _ = os.path.splitext(dag_file)
   module_path = os.path.join(DAG_PATH, dag_file)
   ➥ mod_spec = importlib.util.spec_from_file_location(module_name, module_path)
   module = importlib.util.module_from_spec(mod_spec)
   mod_spec.loader.exec_module(module)

   ➥ dag_objects = [var for var in vars(module).values() if isinstance(var, DAG)]

   assert dag_objects

   for dag in dag_objects:
       dag.test_cycle()

```
