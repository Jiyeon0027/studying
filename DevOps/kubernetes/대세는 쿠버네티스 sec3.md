### Pod
Pod는 쿠버네티스에서 가장 작은 배포 단위

**Pod 내부 컨테이너**
- Pod 내부에는 하나 또는 여러 개의 컨테이너가 있을 수 있음
- 같은 Pod 내의 컨테이너들은 네트워크를 공유함
  - localhost로 서로 통신 가능
  - 같은 포트 번호를 사용할 수 없음 (포트 충돌 주의)
- 같은 Volume을 공유할 수 있음

**Pod의 IP**
- 각 Pod는 고유한 IP 주소를 가짐
- Pod가 재시작되면 IP가 변경됨 (휘발성)
- 따라서 Pod 간 통신 시 IP 직접 사용은 권장하지 않음
- Service를 통해 안정적인 통신 제공

### Label
**Label이란?**
- key-value 형태의 쌍으로 구성 (예: `type: web`, `env: production`)
- Pod, Service 등 모든 쿠버네티스 오브젝트에 부착 가능

**Label 사용 목적**
- 원하는 리소스를 선택하여 그룹화
- Service가 특정 Label을 가진 Pod들과 연결
- 배포 전략 구성 (예: dev/staging/production 환경 구분)

**Label Selector**
- `matchLabels`: 정확히 일치하는 Label 선택
- `matchExpressions`: 조건식을 사용한 복잡한 선택

## Node Schedule
Pod를 어떤 Node에 배치할지 결정하는 메커니즘

**직접 선택 방식**
- `NodeName`: Pod 생성 시 특정 Node를 직접 지정
- `NodeSelector`: Label을 사용하여 Node 선택
- 특정 하드웨어(GPU, SSD 등)가 필요한 경우 유용

**자동 선택 방식**
- 스케줄러가 자동으로 적절한 Node를 선택
- Node의 리소스 상태(CPU, Memory)를 고려
- Pod의 요구사항(requests, limits)과 Node의 가용 자원을 비교
- 가장 효율적인 Node에 배치

**고급 스케줄링**
- `NodeAffinity`: 선호하는 Node 조건 설정
- `PodAffinity/PodAntiAffinity`: 특정 Pod와 같이/다르게 배치
- `Taints & Tolerations`: Node가 특정 Pod만 받아들이도록 제한

## Service
Pod는 IP가 재시작 시 변경되므로, 안정적인 네트워크 연결을 위해 Service 오브젝트 사용

### ClusterIP (기본 타입)
**개념**
- 클러스터 내부에서만 접근 가능한 가상 IP 제공
- 외부에서는 접근 불가능
- 기본 Service 타입 (타입을 명시하지 않으면 ClusterIP로 생성)

**특징**
- 고정된 IP 주소 제공 (Pod IP와 달리 변경되지 않음)
- Label Selector로 여러 Pod를 그룹화하여 로드밸런싱
- 클러스터 내부 Pod 간 통신에 사용

**사용 사례**
- 데이터베이스 연결 (외부 노출 불필요)
- 마이크로서비스 간 내부 통신
- 백엔드 API 서버 (프론트엔드와의 내부 통신)

### NodePort
**개념**
- 모든 Node의 특정 포트를 열어서 외부에서 접근 가능하게 함
- ClusterIP 기능도 함께 제공 (내부 통신도 가능)
- 포트 범위: 30000-32767

**동작 방식**
- Node의 IP:포트로 접근 → Service로 전달 → Pod로 라우팅
- 어떤 Node IP로 접근해도 동일한 Service로 연결됨

**특징**
- 외부에서 `<NodeIP>:<NodePort>`로 직접 접근 가능
- 모든 Node에 동일한 포트가 열림

**사용 사례**
- 개발/테스트 환경에서 임시로 외부 노출
- 로드밸런서 없이 간단히 외부 접근 필요할 때
- 데모나 PoC(Proof of Concept)

**단점**
- Node IP를 직접 알아야 함
- 포트 관리가 복잡해질 수 있음
- 프로덕션 환경에는 비추천

### LoadBalancer
**개념**
- 클라우드 제공자(AWS, GCP, Azure 등)의 로드밸런서를 자동으로 생성
- NodePort와 ClusterIP 기능도 함께 제공
- 외부에 안정적인 단일 진입점 제공

**동작 방식**
- Service 생성 시 클라우드 로드밸런서가 자동으로 프로비저닝됨
- 외부 IP 주소가 할당됨
- 트래픽: 외부 IP → 로드밸런서 → NodePort → Service → Pod

**특징**
- 하나의 고정된 외부 IP 제공
- 클라우드 로드밸런서의 헬스체크, SSL 종료 등 기능 활용 가능
- 높은 가용성과 확장성

**사용 사례**
- 프로덕션 환경의 웹 애플리케이션
- 외부 사용자에게 서비스 제공
- 안정적이고 확장 가능한 엔드포인트 필요 시

**비용**
- 각 LoadBalancer Service마다 클라우드 로드밸런서 비용 발생
- 여러 서비스는 Ingress 사용 권장 (하나의 로드밸런서로 여러 서비스 라우팅)

**비교 요약**

| 타입 | 접근 범위 | 외부 IP | 사용 환경 | 비용 |
|------|-----------|---------|-----------|------|
| ClusterIP | 클러스터 내부 | ❌ | 내부 통신 | 무료 |
| NodePort | 외부 (Node IP 필요) | ❌ | 개발/테스트 | 무료 |
| LoadBalancer | 외부 (단일 IP 제공) | ✅ | 프로덕션 | 유료 (클라우드) |

## Volume
Pod의 데이터는 기본적으로 휘발성 - Volume을 통해 데이터 영속성 확보

### emptyDir
**개념**
- Pod 생성 시 만들어지고, Pod 삭제 시 함께 삭제되는 임시 볼륨
- 같은 Pod 내의 컨테이너들이 데이터를 공유할 수 있음

**특징**
- Pod가 살아있는 동안에만 데이터 유지
- 컨테이너가 재시작되어도 데이터는 유지 (Pod가 살아있으므로)
- Pod가 삭제되면 데이터도 함께 삭제됨

**사용 사례**
- 컨테이너 간 임시 파일 공유
- 캐시 데이터 저장
- 중간 처리 데이터 임시 보관

**주의사항**
- 영구적인 데이터 저장에는 부적합
- Pod 재시작(재생성) 시 데이터 손실

### hostPath
**개념**
- Node(호스트)의 파일 시스템 경로를 Pod에 마운트
- Node의 특정 디렉토리를 Pod에서 직접 사용

**특징**
- 같은 hostPath를 사용하는 Pod들은 데이터를 공유할 수 있음
- Pod가 삭제되어도 Node에 데이터가 남아있음
- 같은 Node에 스케줄링된 Pod들만 데이터 접근 가능

**문제점**
- Pod가 다른 Node에 생성되면 이전 데이터에 접근 불가
- Node에 종속적이어서 이식성이 떨어짐
- 보안 위험 (Node의 파일 시스템 직접 접근)

**사용 사례**
- Node의 로그 파일 수집
- Docker 소켓 접근 (예: `/var/run/docker.sock`)
- 시스템 레벨 모니터링

**주의사항**
- 프로덕션 환경에서는 신중하게 사용
- Node 장애 시 데이터 손실 가능성
- 멀티 Node 환경에서는 비추천

### PV (PersistentVolume) & PVC (PersistentVolumeClaim)
**개념**
- **PV**: 관리자가 프로비저닝한 실제 저장소 리소스
- **PVC**: 사용자가 요청하는 저장소 요청서
- PV와 PVC를 연결하여 Pod에서 영구 저장소 사용

**동작 방식**
1. 관리자가 PV 생성 (실제 스토리지 연결)
2. 사용자가 PVC 생성 (필요한 용량과 속성 명시)
3. 쿠버네티스가 조건에 맞는 PV와 PVC 자동 바인딩
4. Pod에서 PVC를 마운트하여 사용

**PV 특징**
- 클러스터 레벨 리소스 (네임스페이스 독립적)
- 외부 스토리지와 연결 (NFS, AWS EBS, GCE PD 등)
- 용량(Capacity), 접근 모드(Access Mode) 정의

**PVC 특징**
- 네임스페이스 레벨 리소스
- 필요한 저장공간 크기와 접근 모드 요청
- PV와 바인딩되면 Pod에서 사용 가능

**접근 모드 (Access Modes)**
- `ReadWriteOnce (RWO)`: 하나의 Node에서만 읽기/쓰기 (가장 일반적)
- `ReadOnlyMany (ROX)`: 여러 Node에서 읽기만 가능
- `ReadWriteMany (RWX)`: 여러 Node에서 읽기/쓰기 (NFS 등)

**생명주기**
- PVC 삭제 후 PV 처리 정책:
  - `Retain`: PV 유지 (데이터 보존, 수동 정리 필요)
  - `Delete`: PV와 외부 스토리지 자동 삭제
  - `Recycle`: 데이터 삭제 후 PV 재사용 (deprecated)

**사용 사례**
- 데이터베이스 데이터 저장
- 사용자 업로드 파일 저장
- 영구적으로 보존해야 하는 로그

**StorageClass**
- PV를 동적으로 생성하기 위한 템플릿
- PVC 생성 시 자동으로 PV를 프로비저닝
- 클라우드 환경에서 자동으로 디스크 생성

**비교 요약**

| 타입 | 데이터 보존 | 범위 | 용도 | Node 종속성 |
|------|------------|------|------|------------|
| emptyDir | Pod 삭제 시 삭제 | Pod 내부 | 임시 데이터 공유 | ❌ |
| hostPath | Node에 보존 | Node | 시스템 접근 | ✅ 있음 |
| PV/PVC | 영구 보존 | 클러스터 | 영구 데이터 저장 | ❌ |

## ConfigMap & Secret
애플리케이션의 설정과 민감 정보를 컨테이너 이미지와 분리하여 관리

### ConfigMap
**개념**
- 애플리케이션의 설정 데이터(환경변수, 설정 파일 등)를 저장하는 오브젝트
- 민감하지 않은 일반 설정 정보 관리
- key-value 형태로 데이터 저장

**사용 목적**
- 환경별(dev/staging/production) 설정 분리
- 컨테이너 이미지 재빌드 없이 설정 변경 가능
- 설정의 재사용성과 버전 관리

**생성 방법**
```yaml
# 직접 작성
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.url: "mysql://db.example.com"
  log.level: "info"
```

```bash
# 명령어로 생성
kubectl create configmap app-config --from-literal=key1=value1
kubectl create configmap app-config --from-file=config.properties
```

**사용 방법**

1. **환경변수로 주입**
```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      configMapKeyRef:
        name: app-config
        key: database.url
```

2. **전체 ConfigMap을 환경변수로**
```yaml
envFrom:
  - configMapRef:
      name: app-config
```

3. **파일로 마운트**
```yaml
volumes:
  - name: config-volume
    configMap:
      name: app-config
volumeMounts:
  - name: config-volume
    mountPath: /etc/config
```

**주의사항**
- 1MB 크기 제한
- ConfigMap 변경 시 Pod는 자동으로 재시작되지 않음 (수동 재시작 필요)
- 마운트된 ConfigMap은 일정 시간 후 자동 업데이트 (환경변수는 업데이트 안 됨)

### Secret
**개념**
- 비밀번호, 토큰, SSH 키 등 민감한 정보를 저장하는 오브젝트
- ConfigMap과 유사하지만 보안이 강화됨
- base64로 인코딩되어 저장 (암호화 아님!)

**ConfigMap과의 차이점**
- 민감한 정보 저장 용도
- etcd에 암호화되어 저장 가능 (설정 필요)
- 메모리에만 마운트되어 디스크에 기록되지 않음
- RBAC으로 접근 제어 가능

**생성 방법**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=      # base64 인코딩된 값
  password: cGFzc3dvcmQ=
```

```bash
# 명령어로 생성 (자동 base64 인코딩)
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=password
```

**Base64 인코딩/디코딩**
```bash
# 인코딩
echo -n "admin" | base64
# YWRtaW4=

# 디코딩
echo "YWRtaW4=" | base64 -d
# admin
```

**사용 방법**

1. **환경변수로 주입**
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-secret
        key: password
```

2. **파일로 마운트**
```yaml
volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
volumeMounts:
  - name: secret-volume
    mountPath: /etc/secrets
    readOnly: true
```

**Secret 타입**
- `Opaque`: 일반적인 용도 (기본값)
- `kubernetes.io/service-account-token`: 서비스 계정 토큰
- `kubernetes.io/dockerconfigjson`: Docker 레지스트리 인증
- `kubernetes.io/tls`: TLS 인증서와 키

**보안 주의사항**
- base64는 인코딩일 뿐 암호화가 아님 (누구나 디코딩 가능)
- etcd 암호화 설정 권장 (Encryption at Rest)
- RBAC으로 Secret 접근 제한
- Secret을 Git에 커밋하지 말 것
- 외부 Secret 관리 도구 사용 권장 (Vault, Sealed Secrets 등)

**ConfigMap vs Secret 선택 기준**

| 구분 | ConfigMap | Secret |
|------|-----------|--------|
| 용도 | 일반 설정 정보 | 민감한 정보 |
| 예시 | 로그 레벨, 서버 주소, 기능 플래그 | 비밀번호, API 키, 토큰 |
| 인코딩 | 평문 | base64 |
| 보안 | 기본 | 강화 (etcd 암호화, 메모리 마운트) |
| Git 저장 | 가능 | 절대 불가 |

**실전 팁**
- 환경변수 방식보다 파일 마운트 방식이 더 안전 (프로세스 목록에 노출 안 됨)
- ConfigMap/Secret 변경 시 Pod 재시작 자동화 필요 (Reloader 도구 사용)
- 민감도가 높은 정보는 외부 Secret 관리 솔루션 사용 권장

## Namespace
**개념**
- 클러스터 내에서 리소스를 논리적으로 격리하는 가상 공간
- 하나의 물리적 클러스터를 여러 가상 클러스터로 분할
- 리소스 이름의 범위(scope)를 제공

**기본 Namespace**
- `default`: 별도 지정 없으면 사용되는 기본 네임스페이스
- `kube-system`: 쿠버네티스 시스템 컴포넌트가 사용
- `kube-public`: 모든 사용자가 읽기 가능한 공개 리소스
- `kube-node-lease`: Node의 Heartbeat 정보 저장

**사용 목적**

1. **환경 분리**
   - dev, staging, production 환경을 Namespace로 구분
   - 각 환경에 독립적인 리소스 배포

2. **팀/프로젝트 분리**
   - 팀 A, 팀 B의 리소스를 서로 다른 Namespace에 배치
   - 리소스 이름 충돌 방지

3. **리소스 할당 및 제한**
   - Namespace별로 CPU/Memory 할당량 설정
   - ResourceQuota로 리소스 사용 제한

4. **접근 제어**
   - RBAC으로 Namespace별 권한 관리
   - 특정 사용자는 특정 Namespace만 접근 가능

**생성 및 사용**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
```

```bash
# 명령어로 생성
kubectl create namespace development

# 특정 Namespace에 리소스 생성
kubectl apply -f pod.yaml -n development

# Namespace 조회
kubectl get namespaces
kubectl get pods -n development
kubectl get pods --all-namespaces  # 또는 -A
```

**Pod에 Namespace 지정**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
  namespace: development  # 여기서 지정
spec:
  containers:
  - name: app
    image: nginx
```

**Namespace 간 통신**
- 같은 Namespace 내: Service 이름으로 접근 (`my-service`)
- 다른 Namespace: FQDN 사용 (`my-service.development.svc.cluster.local`)

**주의사항**
- 모든 리소스가 Namespace에 속하는 것은 아님
  - Namespace 대상: Pod, Service, Deployment, ConfigMap, Secret 등
  - 클러스터 레벨: Node, PV, StorageClass 등
- Namespace 삭제 시 내부의 모든 리소스도 함께 삭제됨

## ResourceQuota
**개념**
- Namespace별 리소스 사용량 제한을 설정하는 오브젝트
- CPU, 메모리, 스토리지, 오브젝트 개수 등을 제한
- 리소스 남용 방지 및 공정한 분배

**제한 가능한 리소스**

1. **컴퓨팅 리소스**
   - `requests.cpu`: 요청할 수 있는 총 CPU
   - `requests.memory`: 요청할 수 있는 총 메모리
   - `limits.cpu`: 설정할 수 있는 총 CPU 제한
   - `limits.memory`: 설정할 수 있는 총 메모리 제한

2. **스토리지 리소스**
   - `requests.storage`: 요청할 수 있는 총 스토리지
   - `persistentvolumeclaims`: PVC 개수 제한

3. **오브젝트 개수**
   - `count/pods`: Pod 개수 제한
   - `count/services`: Service 개수 제한
   - `count/configmaps`: ConfigMap 개수 제한
   - `count/secrets`: Secret 개수 제한

**생성 예시**
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"           # 총 10 CPU 코어
    requests.memory: "20Gi"      # 총 20GB 메모리
    limits.cpu: "20"
    limits.memory: "40Gi"
    requests.storage: "100Gi"    # 총 100GB 스토리지
    persistentvolumeclaims: "10" # PVC 10개까지
    count/pods: "50"             # Pod 50개까지
    count/services: "20"         # Service 20개까지
```

**동작 방식**
- ResourceQuota가 설정된 Namespace에서 리소스 생성 시 할당량 확인
- 할당량 초과 시 리소스 생성 거부
- Pod 생성 시 requests/limits 명시 필수 (ResourceQuota 설정 시)

**확인**
```bash
# ResourceQuota 조회
kubectl get resourcequota -n development
kubectl describe resourcequota dev-quota -n development

# 사용 현황 확인
# Used: 현재 사용량, Hard: 최대 한도
```

**사용 사례**
- 개발 환경에는 적은 리소스, 프로덕션에는 많은 리소스 할당
- 팀별로 공정하게 리소스 분배
- 비용 관리 및 예산 통제

## LimitRange
**개념**
- Namespace 내에서 개별 리소스(Pod, Container)의 최소/최대/기본값을 설정
- ResourceQuota는 전체 한도, LimitRange는 개별 한도
- Pod/Container 생성 시 자동으로 기본값 적용

**제한 대상**
- Pod: Pod 전체의 리소스
- Container: 개별 컨테이너의 리소스
- PVC: PersistentVolumeClaim의 스토리지 크기

**설정 가능한 값**

1. **min**: 최소값 (이보다 작으면 생성 거부)
2. **max**: 최대값 (이보다 크면 생성 거부)
3. **default**: 기본 limits 값 (명시하지 않으면 자동 적용)
4. **defaultRequest**: 기본 requests 값 (명시하지 않으면 자동 적용)
5. **maxLimitRequestRatio**: limits/requests 비율 제한

**생성 예시**
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limitrange
  namespace: development
spec:
  limits:
  - type: Container
    max:
      cpu: "2"           # 컨테이너당 최대 2 CPU
      memory: "2Gi"      # 컨테이너당 최대 2GB
    min:
      cpu: "100m"        # 컨테이너당 최소 0.1 CPU
      memory: "128Mi"    # 컨테이너당 최소 128MB
    default:
      cpu: "500m"        # 기본 limits
      memory: "512Mi"
    defaultRequest:
      cpu: "250m"        # 기본 requests
      memory: "256Mi"
    maxLimitRequestRatio:
      cpu: "4"           # limits는 requests의 최대 4배
      memory: "4"
  
  - type: Pod
    max:
      cpu: "4"           # Pod 전체 최대 4 CPU
      memory: "8Gi"      # Pod 전체 최대 8GB
  
  - type: PersistentVolumeClaim
    min:
      storage: "1Gi"     # PVC 최소 1GB
    max:
      storage: "50Gi"    # PVC 최대 50GB
```

**동작 방식**
- Pod/Container 생성 시 requests/limits를 명시하지 않으면 기본값 자동 적용
- 명시한 값이 min보다 작거나 max보다 크면 생성 거부
- limits/requests 비율이 maxLimitRequestRatio를 초과하면 거부

**확인**
```bash
# LimitRange 조회
kubectl get limitrange -n development
kubectl describe limitrange dev-limitrange -n development
```

**ResourceQuota vs LimitRange**

| 구분 | ResourceQuota | LimitRange |
|------|---------------|------------|
| 제한 범위 | Namespace 전체 합계 | 개별 리소스 (Pod/Container) |
| 목적 | 전체 리소스 사용량 제한 | 개별 리소스 크기 제한 |
| 예시 | "Namespace에서 총 10 CPU까지" | "한 컨테이너는 최대 2 CPU" |
| 기본값 설정 | ❌ 불가능 | ✅ 가능 (default, defaultRequest) |
| 필수 명시 | requests/limits 필수 | 생략 시 기본값 자동 적용 |

**함께 사용하기**
```yaml
# 시나리오: development Namespace
# - 전체 합계: 10 CPU, 20GB 메모리
# - 개별 컨테이너: 최대 2 CPU, 2GB 메모리
# - 기본값: 500m CPU, 512Mi 메모리

# ResourceQuota (전체 제한)
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"

# LimitRange (개별 제한 + 기본값)
---
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limitrange
  namespace: development
spec:
  limits:
  - type: Container
    max:
      cpu: "2"
      memory: "2Gi"
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "250m"
      memory: "256Mi"
```

**실전 활용**
- **개발 환경**: 작은 기본값, 넉넉한 최대값 (개발자 편의)
- **프로덕션 환경**: 적절한 기본값, 엄격한 최대값 (안정성)
- **멀티 테넌트 환경**: ResourceQuota + LimitRange로 공정한 리소스 분배
- **비용 최적화**: 과도한 리소스 요청 방지

**주의사항**
- ResourceQuota가 있으면 Pod에 requests/limits 필수 (또는 LimitRange로 기본값 설정)
- LimitRange는 기존 리소스에 소급 적용되지 않음 (신규 생성부터 적용)
- 너무 작은 값 설정 시 Pod가 정상 작동하지 않을 수 있음
