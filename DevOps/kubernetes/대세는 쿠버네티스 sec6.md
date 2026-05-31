# 섹션 6. [중급편] Pod 상세

## Pod Lifecycle

### Status 구조
Pod의 상태는 크게 세 가지 레벨로 구성됨:

1. **Phase** (파드 전체 상태)
   - `Pending`: 파드가 생성되었지만 아직 실행되지 않은 상태
   - `Running`: 파드가 노드에 바인딩되고 컨테이너가 실행 중
   - `Succeeded`: 모든 컨테이너가 성공적으로 종료됨
   - `Failed`: 하나 이상의 컨테이너가 실패로 종료됨
   - `Unknown`: 파드 상태를 확인할 수 없음 (통신 장애 시)

2. **Conditions** (파드 상세 조건)
   - `status`: `True`, `False`, `Unknown`
   - `reason`: 상태에 대한 구체적인 이유
   - 종류: `PodScheduled`, `Initialized`, `ContainersReady`, `Ready`

3. **Container State** (컨테이너 상태)
   - `Waiting`: 컨테이너 시작 대기 중
   - `Running`: 컨테이너 실행 중
   - `Terminated`: 컨테이너 종료됨

### Pod 생성 흐름
1. 파드의 최초 상태: `Pending`
2. `initContainers` (초기화 컨테이너) 실행
3. 초기화 컨테이너 완료 → `PodScheduled`, `Initialized` 상태 업데이트
4. 파드에 이미지 다운로드
5. 파드 상태: `Running` (컨테이너: `running` 또는 `waiting`)
6. 최종 상태: `Failed`, `Succeeded`, `Unknown`

---

## Pod ReadinessProbe & LivenessProbe

### Readiness Probe
> 앱이 구동되기 전까지 서비스와 연결되지 않게 해줌

#### 필수 속성 (체크 방법 중 하나 선택)
| 속성 | 설명 |
|------|------|
| `httpGet` | HTTP GET 요청으로 헬스체크 (path, port 지정) |
| `exec` | 컨테이너 내부에서 명령어 실행 |
| `tcpSocket` | TCP 소켓 연결 확인 |

#### 옵션 속성
| 속성 | 설명 | 예시 |
|------|------|------|
| `initialDelaySeconds` | Pod 생성 후 헬스체크 시작까지 대기 시간 | 5초 |
| `periodSeconds` | 헬스체크 주기 | 10초 |
| `successThreshold` | 성공으로 판단하는 연속 성공 횟수 | 3회 |
| `failureThreshold` | 실패로 판단하는 연속 실패 횟수 | 3회 |

#### 동작 예시 (exec 방식)
```yaml
readinessProbe:
  exec:
    command: ["cat", "/ready.txt"]
  initialDelaySeconds: 5
  periodSeconds: 10
  successThreshold: 3
```

**동작 흐름:**
1. 컨테이너가 `Running` 상태가 되면 최초 **5초 동안 지연**
2. 5초 후 `ready.txt` 파일이 있는지 체크
3. 파일이 없다면 → **10초 후 다시 체크**
4. 계속 데이터가 없으면 → Pod의 Condition은 `False` 유지
5. 노드에 `ready.txt` 파일 추가 → 컨테이너 볼륨과 연결되어 있으므로 다음 probe에서 성공
6. **3번 연속 성공** 확인 → Condition 상태가 `True`로 변경
7. 엔드포인트가 정상 address로 간주되어 **서비스와 연결**됨

---

### Liveness Probe
> 앱 장애 시 지속적인 트래픽 실패를 방지 (파드 재실행)

#### 동작 예시 (httpGet 방식)
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

**시나리오:**
- 한 서비스에 두 파드가 Running 상태
- 앱에 `/health` 경로로 요청 시 status `200`을 반환하는 헬스체크 구현

**동작 흐름:**
1. 쿠버네티스가 **HTTP GET**으로 5초 후 `/health` 경로 체크
2. `200` 응답 수신 → 정상
3. **10초 간격**으로 지속적으로 체크
4. 만약 **3번 연속 실패** 시 → 파드 **재시작**

---

### Readiness vs Liveness 비교

| 구분 | Readiness Probe | Liveness Probe |
|------|-----------------|----------------|
| 목적 | 트래픽 수신 준비 확인 | 컨테이너 정상 동작 확인 |
| 실패 시 동작 | 서비스에서 제외 (Endpoint 제거) | 컨테이너 재시작 |
| 사용 시점 | 앱 초기 구동 시 | 앱 운영 중 장애 감지 |
| 영향 범위 | 트래픽 라우팅 | 파드 생명주기 |

### 사용 시 주의사항
- Readiness Probe 사용 시 파드 생성/변화 상태를 모니터링 가능
- Liveness Probe는 앱 장애 시 자동 복구를 위해 사용
- 두 Probe를 함께 사용하면 더 안정적인 서비스 운영 가능

## QoS Classes
> QoS (Quality of Service): 노드 자원이 부족할 때 어떤 파드를 먼저 종료할지 결정하는 우선순위

### 자원 반환 우선순위
```
BestEffort (가장 먼저 종료) → Burstable → Guaranteed (가장 마지막 종료)
```

---

### 1. Guaranteed (보장됨)
> 가장 높은 우선순위, 자원 부족 시 가장 마지막에 종료

**조건:**
- 모든 컨테이너에 `requests`와 `limits`가 설정되어야 함
- `requests` = `limits` (CPU, Memory 모두 동일해야 함)

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

**특징:**
- 요청한 리소스를 보장받음
- OOM(Out of Memory) 발생 시 가장 마지막에 종료 대상이 됨
- 안정적인 서비스 운영이 필요한 파드에 적합

---

### 2. Burstable (버스트 가능)
> 중간 우선순위, Guaranteed와 BestEffort 사이

**조건:**
- Guaranteed 조건을 충족하지 않음
- 최소 하나의 컨테이너에 `requests` 또는 `limits`가 설정됨

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

**특징:**
- `requests`만큼은 보장, `limits`까지 추가 사용 가능
- 자원 부족 시 Guaranteed보다 먼저 종료됨
- OOM 발생 시 **OOM Score**가 높은 파드부터 종료
  - OOM Score = 실제 메모리 사용량 / requests 비율로 계산

---

### 3. BestEffort (최선 노력)
> 가장 낮은 우선순위, 자원 부족 시 가장 먼저 종료

**조건:**
- 어떤 컨테이너에도 `requests`와 `limits`가 설정되지 않음

```yaml
resources: {}
# 또는 resources 섹션 자체가 없음
```

**특징:**
- 리소스 보장 없음, 남는 자원만 사용
- 노드에 여유 자원이 있을 때만 실행 가능
- 자원 부족 시 가장 먼저 종료 대상이 됨
- 중요하지 않은 배치 작업이나 테스트 파드에 적합

---

### 컨테이너 리소스 설정

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: qos-demo
spec:
  containers:
  - name: app
    image: nginx
    resources:
      requests:
        memory: "128Mi"   # 최소 보장 메모리
        cpu: "250m"       # 최소 보장 CPU (0.25 core)
      limits:
        memory: "256Mi"   # 최대 사용 가능 메모리
        cpu: "500m"       # 최대 사용 가능 CPU (0.5 core)
```

| 속성 | 설명 |
|------|------|
| `requests` | 컨테이너에 보장되는 최소 리소스 |
| `limits` | 컨테이너가 사용할 수 있는 최대 리소스 |

## Node Scheduling
> 파드를 어떤 노드에 배치할지 결정하는 방법

- NodeName, NodeSelector, NodeAffinity: 노드를 선택
    - NodeAffinity : NodeSelector 보다 좀더 다양한 방법으로 
    Node에 스케줄링을 할 수 있는 기능들을 제공
        - matchExpression : 해당 규칙에 부합하는 Node에 배치, 
        여러 Node가 있을 경우 자원이 많은 곳에 배치됨
        - required : 해당 옵션 지정시 절대적으로 
        matchExpression에 부합하는 Node에만 배치됨
        - preferred : 해당 옵션 지정시 matchExpression에 
        부합하는 Node가 없으면, 자원이 많은 Node에 배치됨
        - preferred.weight : 두 개 이상의 preferred 옵션을 
        설정시, 좀더 선호하는 옵션으로 가중치를 부여함
---

### 1. 노드 선택 (Node 지정)

#### NodeName
> 가장 단순한 방법 - 특정 노드 이름을 직접 지정

```yaml
spec:
  nodeName: node1
```

#### NodeSelector
> 노드의 Label을 기준으로 선택

```yaml
spec:
  nodeSelector:
    gpu: "true"
    disktype: ssd
```

#### NodeAffinity
> NodeSelector보다 다양한 조건으로 노드 스케줄링 가능

```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
            - nvme
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 80
        preference:
          matchExpressions:
          - key: gpu
            operator: Exists
```

**matchExpressions 연산자:**
| 연산자 | 설명 | 예시 |
|--------|------|------|
| `In` | 값 목록 중 하나와 일치 | `values: [ssd, nvme]` |
| `NotIn` | 값 목록에 없음 | `values: [hdd]` |
| `Exists` | 키가 존재함 | key만 지정 |
| `DoesNotExist` | 키가 존재하지 않음 | key만 지정 |
| `Gt` | 값보다 큼 | 숫자 비교 |
| `Lt` | 값보다 작음 | 숫자 비교 |

**Required vs Preferred:**
| 구분 | Required | Preferred |
|------|----------|-----------|
| 속성명 | `requiredDuringScheduling...` | `preferredDuringScheduling...` |
| 동작 | 조건에 맞는 노드에만 배치 (필수) | 조건에 맞는 노드 우선, 없으면 다른 노드 |
| 실패 시 | 파드 Pending 상태 유지 | 자원이 많은 노드에 배치 |
| weight | 없음 | 1-100 사이 가중치 설정 가능 |

**preferred.weight:**
- 여러 개의 preferred 옵션 설정 시 선호도 가중치 부여
- 값이 높을수록 해당 조건의 노드를 더 선호
- 각 노드의 점수 = Σ(조건 만족 시 weight)

---

### 2. Pod Affinity / Anti-Affinity
> 파드 간의 배치 관계를 정의

#### Pod Affinity
> 특정 파드와 **같은 노드**에 배치

```yaml
spec:
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: web
        topologyKey: kubernetes.io/hostname
```

#### Pod Anti-Affinity
> 특정 파드와 **다른 노드**에 배치

```yaml
spec:
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchLabels:
            app: web
        topologyKey: kubernetes.io/hostname
```

**topologyKey:**
| 값 | 의미 |
|----|------|
| `kubernetes.io/hostname` | 같은/다른 노드 |
| `topology.kubernetes.io/zone` | 같은/다른 가용 영역 |
| `topology.kubernetes.io/region` | 같은/다른 리전 |

---

### 3. Taint & Toleration
> 노드에 제한을 걸고, 특정 파드만 허용

#### Taint (노드에 설정)
> 노드에 오점(Taint)을 찍어서 파드가 스케줄링되지 않도록 제한


**Effect 종류:**
| Effect | 설명 |
|--------|------|
| `NoSchedule` | Toleration이 없는 파드는 스케줄링 불가 |
| `PreferNoSchedule` | 가급적 스케줄링하지 않음 (선호) |
| `NoExecute` | 기존 파드도 축출, 새 파드 스케줄링 불가 |

---

#### Toleration (파드에 설정)
> Taint가 있는 노드에도 스케줄링 허용

```yaml
spec:
  tolerations:
  - key: "key"
    operator: "Equal"
    value: "value"
    effect: "NoSchedule"
```

**Operator:**
| 연산자 | 설명 |
|--------|------|
| `Equal` | key, value, effect 모두 일치해야 함 |
| `Exists` | key만 일치하면 됨 (value 생략 가능) |

