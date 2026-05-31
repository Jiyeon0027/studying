# 섹션 5 컨트롤러

### Controller 기능
1. Auto Healing
2. Auto Scaling
3. Software Update - 한번에 업그레이드 및 롤백
4. Job

### Replication Controller : 현재 deprecated 된 object
### Replica Set : 대체로 사용
- Template 기능 :  Controller에서  Pod의 스펙을 입력하는 설정
- Replicas : Controller에 연결된 Pod의 개수를 조절하는 설정
    - Replica 의 수치에 따라 scale out , scale in
    - 보통 파드를 먼저 생성 후 replicaSet, Templcate의 Name 과 selector을 일치시키면 해당 pod와 연결됨
- Selector : ReplicaSet에만 있는 기능
    - selector.matchLabels : key:value를 이용한 기본적인 매칭 방법
    - selector.matchExpressions : 조건식을 이용해서 좀더 세밀하게 매칭 방법을 컨트롤 가능. 일반적으로 Pod를 Node에 배치시킬 때 주로 사용 (추후 Node Scheduling에서 다룸)
        - Exists, DoesNotExist, In, NotIn

### Deployment
한 서비스가 운영중인데 이 서비스를 업데이트 해야해서 재 배포를 해야 될 때 도움을 주는 컨트롤러
- ReCreate
    - 파드 삭제 후 다시 만들어줌
    - 다운타임이 발생
- Rolling Update
    - 하나만 삭제 후 점진적 변경
    - 추가적 자원 요구 하지만, 다운타임 없음
- Blue, Green
    - ReplicaSet을 관리하는 모든 컨트롤러를 이용
    - 라벨을 사용해서 연결을 변경
    - 순간적으로 변경하여 다운타임 없음
    - 자원 사용량은 두배, 롤백이 쉬움
- Canary
    - 카나리아새...? 카나리와 같은 실험체를 통해 위험을 검증하고 이후 정식 배포
    - typeapp에 라벨을 달아서 연결
    - 트래픽을 연결하여 ingress Controller로 특정타겟만 테스트할 수 있도록 진행

Recreate Strategy 예시
```yaml
    strategy:
        type: Recreate
```
Rolling update Strategy 예시
```yaml
    strategy:
        type: RollingUpdate
    minReadySeconds: 10
```

### DaemonSet
- 모든 노드에  파드가 하나씩 생긴다는 특징
1. 성능 수집 ㅣ 모니터링(프로메테우스 같은 성능 수집)
2. 로그 수집 (FluentD)
3. 스토리지에 활용 (ClusterFS 와 같이 각각의 노드에 설치)

- NodeSelector를 통해 원하는 Node에만 Pod를 배치시킬 수 있음
- hostPort를 설정하면 각 Node별 hostPort가 해당 노드위에 있는 Pod의 Port로 연결

### Job
일시적인 작업을 하기 위한 용도로 Pod를 생성하고, 작업이 종료되면 Pod는 중지됨 <br>
-> 중지이기 때문에 로그를 확인 할 수 있음
- Recreate vs Restart
    - Recreate: 파드를 다시 만들어짐
    - Restart: 파드 안의 컨테이너만 재가동
- yaml 명령어
    - completions : 총 생성 시킬 Pod 수
    - parallelism : 동시에 생성 시킬 Pod 수
    - activeDeadlineSeconds : 30초가 될 때까지 모든 작업이 완료되지 않으면 실행중인 Pod는 강제로 삭제되, 완료된 Pod만 남아있게 됩니다.

### CronJob
특정시간에 반복적으로 실행할 목적
- 데이터 백업 정기적으로
- 주기적 업데이트나 메시지 발송
- Concurrency Policy 
    - allow (default) : 이전 Job의 상태에 상관없이 정해진 시간에 따라 Job을 생성
    - forbid : 동시에 Job이 실행되는걸 허용하지 않음. 이전 Job이 아직 실행중이면 정해진 시간의 Job은 Skip됨
    - replace : 다음 정해진 시간까지 이전 Job이 실행중이면, 강제로 종료시키고 새로운 Job을 생성시킴
- yaml 명령어
    - schedule : (*/1 * * * *) 1분 간격으로 Job을 하나씩 생성
    - suspend : 일시 정지
    - Manual Trigger : 수동으로 Job을 직접 실행 시킴 

