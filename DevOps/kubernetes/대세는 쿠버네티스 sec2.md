# 대세는 쿠버네티스 섹션2
- 기존의 9대의 서버가 필요한 경우 -> 이후 4대의 서버에서 `auto scaling`, `auto healing` 기능을 이용해 감소 가능
- 버전 업데이트를 해야하는 경우
	- `depolyment` (rolling update, recreate) 등의 기능으로 지원

### VM vs Container
- container : 마이크로 서비스에 대한 이야기가 따라옴
    - 모듈별로 쪼게서 컨테이너에 넣고 그 컨테이너들을 한 파드에 담을 수 있음
    - 파드는 배포단위
- VM : 한 서비스를 만드는 데에 여러 모듈을 한 언어로 만들어서 따로 올림

### Kubernetes 환경 Get Started

- 로컬에서의 리눅스 위의 언어 사용
- 도커를 이용해 컨테이너를 가져오고 node js 의 컨테이너 이미지를 가져와서 구동 시키기
- 이러한 컨테이너를 구동 시켜서 오픈
- 컨테이너 이미지를 도커에 올리고 이 컨테이너를 파드에 져와서 이미지를 가져와 8000번으로 오픈하도록 함
- 컨테이너 가상화 솔루션
	- linux에서 제공하는 namespace(커널) cgroup(자원)을 이용하여 컨테이너 단위로 사용할 수 있게 함
		- namespace : 프로세스를 실행할 때 싯스템의 리소스를 분리해서 실행할 수 있도록 하는 기능
		- cgroup : 프로세스에 할당된 시스템자원에 대한 제어를 제공
	- 컨테이너는 한 os를 사용하는 개념

### Kubernetes Overview
- Master(Control Plane) : 클러스터의 중앙 API 서버.
- Worker Node(Node1, Node2, Node3 …)
- Namespace는 클러스터 내부의 논리적 격리 공간
	- 서로 다른 네임스페이스에서는 접근할 수 없음
	- 이름이 같아도 충돌하지 않음.
- 컨트롤러 : “현재 상태”를 “원하는 상태”로 맞추는 관리 객체
- replication controller: Pod 개수를 유지하는 가장 초기 컨트롤러
- ReplicaSet : Deployment 내부에서 자동 사용됨.
- Deployment : ReplicaSet을 관리함.
	- Rolling Update, Rollback 등을 시행
- DemonSet: 모든 Node에 특정 Pod를 1개씩 배포.
- CronJob : 정해진 시간마다 Job 실행.
