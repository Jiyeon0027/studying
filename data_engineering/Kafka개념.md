- 소스 시스템과 타겟 시스템의 연결

<img src="https://velog.velcdn.com/images/julia2039/post/9b14cae4-e56b-4338-95ed-71a7b982b2f9/image.png" width="500" alt="소스시스템과 타겟시스템의 연결">

- 왜 아파치 카프카를 쓰는 가 : open source project
- distributed, resilient architecture, fault tolerant
- horizontal scalability : 수평적으로 브로커를 계속 확장 가능하고, 메세지도 확장 가능
- high performance : 지연시간이 10ms 미만 →실시간 시스템

<img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Ft1.daumcdn.net%2Fcfile%2Ftistory%2F99B7A03C5C20888D04" width="500" alt="카프카 아키텍쳐">

- Topic : 보내는 메시지를 구분하기 위한 카테고리화
  - 데이터 베이스와 비슷함 (without constraints)
  - 원하는 만큼 토픽을 정할 수 있음 (name 으로 구분)
  - 어떠한 종류의 메세지 포맷이든 상관없이 스트림
  - 쿼리를 할 수 없음, 그 대신 producer로 데이터를 보내고 카프카 consumer 로 읽어들임
- Partition : 토픽을 구성하는 데이터 저장소로서 수평확장이 가능한 형태
  - 파티션으로 카프카의 메세지가 가게되고 그 이후 메세지가 파티션마다 정렬됨
  - 파티션마다 incremental id 를 가지고 있는데 이를 offset 이라고 부름
  - kafak 토픽은 immutable 이기 때문에 파티션에 한번 써지면 변경 불가

→ 데이터는 제한된 시간에만 저장되어 있음(default = one week)

→ offset 은 재사용되지 않음

→ 카프카에서 원하는만큼 파티션을 가질 수 있음

파티션의 갯수를 결정하는 방법

- Producer : 데이터를 만들어내어 전달하는 전달자 topic에 데이터를 만듦

  - 어떤 파티션에 쓸지 미리 알고 쓸 수 있음 → 카프카 브로커가 실패하면 생산자가 자동으로 회복가능
  - 프로듀서 : 메시지 안에 메세지 키를 전송 → 이 키를 이용해서 항상 같은 파티션으로 이동(해싱)
  - 카프카 메시지 : key -value → compression → +header → partition+offset  
    ![카프카메시지](https://prod-files-secure.s3.us-west-2.amazonaws.com/1206d1c4-0281-421a-8d0e-ffc21959e876/f5c41edf-b526-4e19-96b2-77f9aa6ab2ef/Untitled.png)
  - kafka message serializer :
    - 카프카는 오직 입력값으로 bytes 만 받고 bytes 값만 내보냄
    - 따라서 이를 serialization을 진행 :  
      ![serializer](https://prod-files-secure.s3.us-west-2.amazonaws.com/1206d1c4-0281-421a-8d0e-ffc21959e876/c942900b-a7a3-4ee7-9284-dbc2f5ea6fdc/Untitled.png)
  - kafka partitioner : 레코드에서 code logic 을받아서 어디 파티셔닝으로 보낼지 결정

- Consumer : 프로듀서에서 전달한 데이터를 브로커에 요청하여 메시지(데이터)를 소비하는 역할
  - 파티션 하나에서 consumer 가 읽어감(파티션 여러개를 읽기 가능)
  - 데이터는 offset 이 낮은순서에서 높은 순서로 읽힘(각 파티션마다)
  - consumer deserializer : bytes 에서 객체와 데이터로 변경됨
  - consumer는 자신이 가져오는 데이터 타입을 알아야 하므로 serialization, deserialization type는 변경되지 않을 의무가 있음.
  - 토픽의 데이터 유형을 변경하고 싶으면 새 토픽을 생성해야 함
- consumer groups
  - 소비자 그룹에 너무 많은 소비자가 있다면?? 어떤 consumer 은 inactive (consumer 의 대기)
  - 하나의 주제에 대해 multiple consumer groups
    <img src="https://velog.velcdn.com/images/hyeondev/post/0c2663f6-7eca-4043-8041-9b663b74f56d/img%20(3).png" width="500" alt="consumer groups">
- consumer offsets:
  - 이를 이용해 읽어오는데 실패하거나 다운된 데이터를 다시 볼 수 있음
  - delivery semantics for consumers : 3가지
    - at least once(usually preferred)
    - at most once
    - exactly once : 트랜잭션 api 를 사용
- Broker : 생산자와 소비자와의 중재자 역할을 하는 역할 (서버)

  - ID로 식별 : 브로커 여러개가 한개의 클러스터에 있음
  - 각 브로커는 topic partitions 를 포함
  - brokers and topics
    - 데이터의 분산으로 인해 horizontal scale 가능
      <img src="https://velog.velcdn.com/images%2Fhyeondev%2Fpost%2Fe1919472-63ec-4846-8230-abce247e5489%2Fimg%20(1).png" width="500" alt="horizontal scale">
  - bootstrap server 라고도 불림
  - bootstrap server 라고도 불림
  - 카프카 브로커는 모든 브로커 마다 메타 데이터안데 다른 브로커들의 정보를 가지고 있기 때문에 어떤 한 브로커에 연결해도 가져오고 싶은 토픽 브로커에 연결 가능

- topic replication factor
  - 브로커가 하나가 다운되면 다른 브로커가 데이터 제공
  - 파티면의 복제마다 하나의 리더가 있고, 데이터가 충분이 빨리 복제되면 ISR을 가지게 됨 (in sync replica)
- producer 는 토픽 리더에게 write 하고 리더는 consumer 에 제공(리더가 사라지면 복제본이 리더가 되는 형식)
  - 최신 : fetching - 소비자가 가장 가까운 replica 에서 읽을 수 있도록 변경됨
- producer acks

  - producer 는 acks를 데이터를 쓰면서 보낼 수 있음
  - acks =0 : producer won’t wait acks (possible data loss)
  - acks =1 : producer will wait for leader acks (limited data loss)
  - acks =all : 리더와 모든 복제본이 필요함 (no data loss

- Zookeeper

  - 카프카를 관리하는 소프트 웨어 - 파티션의 리더를 정하는 역할
  - 메타데이터를 관리하고 브로커, 토픽 등의 관리
  - kafka 2.x 는 주키퍼와 사용하는 것이 필수
  - zookeeper는 consumer offsets 에 대한 정보를 가지고 있지 않음

- kafka kraft
  - 메타 데이터를 효율적으로 관리 zookeeper 의 의존성을 제거
  - 기존의 주키퍼를 사용할떄 메타데이터의 업데이트는 주키퍼에서 동기방식으로 , 브로커에서는 비동기방식으로 전달 → 메타데이터의 불일치 발생 가능, 병목현상 발생가능
  - 카프카 단일 어플리케이션 내에서 메타데이터를 관리할 수 있도록 함, 컨트롤러가 여러개로 구성되고, 액티브 컨트롤러가 리더 역할 수행
  - 파티션 리더 선출의 최적화 → 더 많은 파티션의 생성 가능
  - 단순화된 아키탠처 → 성능향상
