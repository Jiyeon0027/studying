제7장, 제8장 → 복잡한 객체 구조를 만들고 생성하는데 도움이 되는 패턴

제9장 : 컴포넌트들의 동작과 관련된 소프트웨어의 다른 측면(확장, 모듈화, 재사용가능하도록 객체를 결합하고 상호작용할 수 있도록)

## 9-1. 전략패턴

컨텍스트라는 객체를 활성화시켜 변수 부분을 전략(Strategy)이라는 별도
의 상호 교환 가능한 객체로 추출하여 로직의 변경을 지원

- `컨텍스트(Context)`: 공통 로직을 구현
- `전략(Strategy)`: 가변적인 알고리즘을 구현

→ 이는 컴포넌트의 동작이 경우에 따라 달라지는 것을 지원하기 위해, 조건문, 동일한 역할범위에서의 다른 컴포넌트를 혼합해야 하는 상황에서 유용함

즉, 객체 내의 다양한 가변적인 알고리즘을 구현해야 할때 전략 객체에 처리를 위임하여 관리하는 방법

### 여러 형식을 지원하는 환경설정 객체

데이터 베이스에서 여러 매개변수에 접근하고 ,다양한 형식을 지원하는 등의 구현

```jsx
import { promises as fs } from "fs";
import objectPath from "object-path";

export class Config {
  constructor(formatStrategy) {
    this.data = {};
    this.formatStrategy = formatStrategy;
  }

  // 데이터 접근 메서드
  get(configPath) {
    return objectPath.get(this.data, configPath);
  }

  set(configPath, value) {
    return objectPath.set(this.data, configPath, value);
  }

  // 전략을 사용하는 메서드
  async load(filePath) {
    console.log(`Deserializing from ${filePath}`);
    //역직렬화
    this.data = this.formatStrategy.deserialize(
      await fs.readFile(filePath, "utf-8")
    );
  }

  async save(filePath) {
    console.log(`Serializing to ${filePath}`);
    //직렬화
    await fs.writeFile(filePath, this.formatStrategy.serialize(this.data));
  }
}
```

```jsx
// strategy.js

// INI 파일 전략
// INI 파일 형식을 사용하여 데이터의 구문을 분석하고 직렬화하는 전략
export const iniStrategy = {
  deserialize: (data) => ini.parse(data),
  serialize: (data) => ini.stringify(data),
};

// JSON 파일 전략
export const jsonStrategy = {
  deserialize: (data) => JSON.parse(data),
  serialize: (data) => JSON.stringify(data, null, " "),
};
```

```jsx
//결합하여 사용하는 방식

import { Config } from "./config.js";
import { jsonStrategy, iniStrategy } from "./strategies.js";

async function main() {
  const iniConfig = new Config(iniStrategy);
  await iniConfig.load("samples/conf.ini");
  iniConfig.set("book.nodejs", "design patterns");
  await iniConfig.save("samples/conf_mod.ini");

  const jsonConfig = new Config(jsonStrategy);
  await jsonConfig.load("samples/conf.json");
  jsonConfig.set("book.nodejs", "design patterns");
  await jsonConfig.save("samples/conf_mod.json");
}
main();
```

위의 예시

- 공통적인 부분(콘텍스트)을 구현하는 하나의 Config 클래스
- 전략 ini, json
- 두 가지 다른 전략 제품군 생성: 하나는 역 직렬화를 위한 것이고 다른 하나는 직렬화를 위한 것입니다. 이렇게 하면 한 형식으로 읽고 다른 형식으로 저장할 수 있습니다.
- 전략을 동적으로 선택: 제공된 파일의 확장자에 따라 Config 객체는 확장자 맵을 가지고 주어진 확장자에 따라 알맞은 알고리즘을 선택할 수 있습니다

> **전략패턴과 어댑터 패턴?**
>
> 전략패턴의 목적: 알고리즘의 교체 가능성을 제공  
> 어댑터 패턴의 목적: 호환되지 않는 인터페이스들을 함께 동작하도록 만듦 (단순한 인터페이스 변환의 역할)

### 실전에서

- passport 에서 사용하는 Node.js 용 인증 프레임 워크
  - 웹 서버가 다양한 인증체계를 지원 (구글, 카카오, 페이스북,,,)
  - 공통된 로직과 실제인증단계를 분리하여 구현됨

## 9-2. 상태(State)

- 컨텍스트의 상태에 따라 전략이 변경되는 특별한 전략 패턴
- 차이점

  - 전략 패턴: 전략이 한번 설정되면 보통 변경되지 않음
  - 상태 패턴: 객체의 수명주기 동안 동적으로 상태(전략)가 변경됨

  ex. 호텔 예약 시스템</br>
  3가지의 전략 (confirm, cancel, delete) → 이를 각자 하나의 동작만 하도록 구현하고 상태에 따라 다른 전략의 활성화를 해야함

### 기본적인 안전 소켓 구현

- 서버 연결이 끊어져도 실패하지 않는 TCP 클라이언트 소켓 구현
- 오프라인 상태에서 데이터를 큐에 저장하고, 온라인 시 재전송

```jsx
import { OfflineState } from "./offlineState.js";
import { OnlineState } from "./onlineState.js";

export class FailsafeSocket {
  constructor(options) {
    this.queue = []; // 데이터 큐
    this.states = {
      //두가지의 상태집합을 생성
      offline: new OfflineState(this),
      online: new OnlineState(this),
    };
    this.changeState("offline");
  }

  changeState(state) {
    this.currentState = this.states[state];
    this.currentState.activate();
  }

  send(data) {
    this.currentState.send(data);
  }
}
```

```jsx
//offlineState.js

import jsonOverTcp from "json-over-tcp-2"; // (1)

export class OfflineState {
  constructor(failsafeSocket) {
    this.failsafeSocket = failsafeSocket;
  }
  send(data) {
    // (2)
    this.failsafeSocket.queue.push(data);
  }
  activate() {
    // (3)
    const retry = () => {
      setTimeout(() => this.activate(), 1000);
    };

    console.log("Trying to connect...");

    this.failsafeSocket.socket = jsonOverTcp.connect(
      this.failsafeSocket.options,
      () => {
        console.log("Connection established");
        this.failsafeSocket.socket.removeListener("error", retry);
        this.failsafeSocket.changeState("online");
      }
    );
    this.failsafeSocket.socket.once("error", retry);
  }
}
```

→ 오프라인 상태에서의 소켓 동작

- 데이터를 큐에 넣는 작업만 진행함
- activate 함수를 이용해 온라인으로 연결설정하ㄹ고 계속 시도함 State 도 변경

```jsx
export class OnlineState {
  send(data) {
    // 데이터를 큐에 저장하고 즉시 전송 시도
    this.failsafeSocket.queue.push(data);
    this._safeWrite(data);
  }

  activate() {
    // 큐에 있는 모든 데이터 전송 시도
    // 연결 에러 발생 시 오프라인 상태로 전환
  }

  _safeWrite(data) {
    // 데이터 전송 성공 시 큐에서 제거
  }
}
```

→ 온라인 상태에서의 소켓 동작

- 온라인상태이므로 즉시 소켓에 직접 쓰려고 시도 후 성공하면 큐에서 제거하는 로직
- activate : 오프라인일때 대기열에 있던 큐를 비우고자하고, 오프라인이면 다시 전환

## 9-3. 템플릿 패턴

- 컴포넌트의 스켈레톤(공통부분을 나타냄)을 구현하는 추상 클래스를 정의
- 하위 클래스는 템플릿 함수라고 하는 누락된 함수 부분을 구현하여 컴포넌트의 빈 부분을 채움

- JavaScript에서는 추상 클래스를 정의하는 공식적인 방법이 없으므로 함수를 정의하지 않은 상태로 두거나 항상 예외를 발생시키는 함수에 할당하여 함수를 구현해야 함
- 상속이 구현의 핵심적인 부분

**전략 패턴과의 차이점**

- **구현 방식**:
  - 전략 패턴: 런타임에 동적으로 알고리즘 교체
  - 템플릿 패턴: 클래스 정의 시점에 동작 결정
- **유연성**:
  - 전략 패턴: 더 유연함 (실행 중 교체 가능)
  - 템플릿 패턴: 덜 유연하지만 더 단순함

### 9-3-1. 환경설정 관리 템플릿

전략패턴에서 구현했던 환경설정 관리 Config객체를 템플릿 패턴으로 구현

```jsx
export class ConfigTemplate {
  // 공통 로직 구현
  async load(file) {
    this.data = this._deserialize(await fsPromises.readFile(file, "utf-8"));
  }

  async save(file) {
    await fsPromises.writeFile(file, this._serialize(this.data));
  }

  // 템플릿 메서드 (하위 클래스에서 구현)
  _serialize() {
    throw new Error("Must implement");
  }

  _deserialize() {
    throw new Error("Must implement");
  }
}
```

\_serialize(), \_deserialize()부분은 열어둠

- \_ : 보호된 함수에 플래그를 지정하는 방법으로 내부전용임을 나타냄
- 단순한 모형(stubs) 로 정의하여 호출되면 오류를 발생시킴 (구체적인 하위 클래스에 의해 재정의 되지 않는 경우)

```jsx
// JSON 구현체
export class JsonConfig extends ConfigTemplate {
  _deserialize(data) {
    return JSON.parse(data);
  }

  _serialize(data) {
    return JSON.stringify(data, null, " ");
  }
}
```

```jsx
// INI 구현체
export class IniConfig extends ConfigTemplate {
  _deserialize(data) {
    return ini.parse(data);
  }

  _serialize(data) {
    return ini.stringify(data);
  }
}
```

- 이는 클래스 자체에서 포함되어 템플릿 매서드를 상속받아 사용됨
- 상속된 로직과 인터페이스를 재사용하고 몇가지 추상함수만 구현함

## 9-4. 반복자(Iterator)

- 컨테이너의 요소들을 순회하기 위한 공통 인터페이스/프로토콜을 정의
- 순회 알고리즘과 데이터 처리를 분리
- JavaScript에서는 프로토콜을 통해 구현됨

### 반복자 프로토콜

- next() 함수를 구현한 객체 : 반복자
