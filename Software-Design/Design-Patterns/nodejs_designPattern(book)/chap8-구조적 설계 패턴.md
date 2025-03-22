## 프록시

- 다른 객체(subject)에 대한 액세스를 제어하는 객체
- 다른 객체에 대해 실행되는 **작업을 가로채서** 해당 동작을 **증강**하거나 **보완**

![프록시 패턴](attachment:07ba9664-6ac1-4d10-b6e1-ffe1054b5a39:image.png)

- 클라이언트가 `methodA()`를 호출
- 프록시가 이를 먼저 처리(가로채서 추가적인 동작 수행)
- 추후 subject의 `methodA()`를 호출

```jsx
class RealService {
  fetchData() {
    return "📦 원본 데이터";
  }
}

// 프록시 (Proxy) - 작업을 가로채고 로깅 추가
class LoggingProxy {
  constructor(service) {
    this.service = service;
  }

  fetchData() {
    console.log("🛑 프록시: 요청을 로깅 중...");
    return this.service.fetchData();
  }
}

const realService = new RealService();
const proxyService = new LoggingProxy(realService);

console.log(proxyService.fetchData());

// 🛑 프록시: 요청을 로깅 중...
// 📦 원본 데이터
```

- 예시
  - 데이터 검증: 입력을 subject에 전달하기 전에 유효성 검사
  - 보안: 권한을 확인하고, 권한이 있는 경우에만 요청을 subject에 전달
  - 캐싱: 데이터가 캐시에 존재하는지 확인하고, 없는 경우에만 subject에 전달

### 프록시 패턴 구현 예제

```jsx
// 스택 계산기
class StackCalculator {
  constructor() {
    this.stack = [];
  }
  // 스택에 값을 추가
  putValue(value) {
    this.stack.push(value);
  }
  // 스택에서 값을 추출
  getValue() {
    return this.stack.pop();
  }
  peekValue() {
    return this.stack[this.stack.length - 1];
  }
  clear() {
    this.stack = [];
  }
  // 두 값을 꺼내 나눈 뒤 스택에 저장
  divide() {
    const divisor = this.getValue();
    const dividend = this.getValue();
    const result = dividend / divisor;
    this.putValue(result);
    return result;
  }
  // 두 값을 꺼내 곱한 뒤 저장
  multiply() {
    const multiplicand = this.getValue();
    const multiplier = this.getValue();
    const result = multiplier * multiplicand;
    this.putValue(result);
    return result;
  }
}

const calculator = new StackCalculator();
calculator.putValue(3);
calculator.putValue(2);
console.log(calculator.multiply()); // 3*2 = 6
calculator.putValue(2);
console.log(calculator.multiply()); // 6*2 = 12
```

- 문제점

  - `divide()` 메서드에서 0으로 나누면 `Infinity`가 반환

- 해결 방안
  - 프록시 패턴을 사용해 `divide()` 를 가로채 0으로 나누려고 하면 오류를 발생시키도록 수정

### 프록시 패턴 구현(1) - 객체 컴포지션

- 기존 코드를 수정하지 않고, **새로운 객체를 감싸서 안전한 기능을 추가**하는 방식
- 특정 객체(`SafeCalculator`)가 다른 객체(`StackCalculator`)를 내부에 포함하고 (`this.calculator = calculator`) **필요한 기능만 수정하고 나머지는 그대로 사용**하는 방식

```jsx
class SafeCalculator {
  constructor(calculator) {
    // StackCalculator()
    this.calculator = calculator;
  }
  // 프록시 함수
  divide() {
    // 추가적인 검증 로직
    const divisor = this.calculator.peekValue();
    if (divisor === 0) {
      throw Error("Division by 0");
    }
    return this.calculator.divide();
  }
  // 위임된 함수들
  putValue(value) {
    return this.calculator.putValue(value);
  }
  getValue() {
    return this.calculator.getValue();
  }
  peekValue() {
    return this.calculator.peekValue();
  }
  clear() {
    return this.calculator.clear();
  }
  multiply() {
    return this.calculator.multiply();
  }
}

const calculator = new StackCalculator();
const safeCalculator = new SafeCalculator(calculator);

calculator.putValue(3);
calculator.putValue(2);
console.log(calculator.multiply()); // 3*2 = 6

safeCalculator.putValue(2);
console.log(safeCalculator.multiply()); // 6*2 = 12

// 기존 계산기
calculator.putValue(0);
console.log(calculator.divide()); // 12/0 = Infinity

// 새로운 계산기
safeCalculator.clear();
safeCalculator.putValue(4);
safeCalculator.putValue(0);
console.log(safeCalculator.divide()); // 4/0 -> 에러
```

- `StackCalculator`를 직접 수정하지 않고도 다른 검증 로직을 추가한 **다양한 버전의 계산기**를 만들 수 있음
- 하나만 프록시하는 경우에도 모든 함수들을 수동으로 위임해야함

### 프록시 패턴 구현(2) - 객체 리터럴과 팩토리 함수

- 위의 방식은 `constructor`와 `this`를 사용하여 객체를 초기화하고 메서드를 정의
- 팩토리 함수 방식에서는 객체 리터럴을 반환하는 방식으로 필요한 기능을 추가

```jsx
function createSafeCalculator(calculator) {
  return {
    // 프록시된 함수
    divide() {
      // 추가적인 검증 로직
      const divisor = calculator.peekValue();
      if (divisor === 0) {
        throw Error("Division by 0");
      }
      return calculator.divide();
    },
    //위임된 함수들
    putValue(value) {
      return calculator.putValue(value);
    },
    getValue() {
      return calculator.getValue();
    },
    peekValue() {
      return calculator.peekValue();
    },
    clear() {
      return calculator.clear();
    },
    multiply() {
      return calculator.multiply();
    },
  };
}
const calculator = new StackCalculator();
const safeCalculator = createSafeCalculator(calculator);

safeCalculator.putValue(6);
safeCalculator.putValue(3);
console.log(safeCalculator.divide()); // 6 / 3 = 2
// ...
```

- `this`를 사용하지 않아 코드가 직관적
- `new` 없이 사용 가능
- 원래의 `calculator` 객체를 감싸면서, 특정 로직을 추가하는 프록시 패턴을 구현
- 위의 방식과 마찬가지로, 하나만 프록시하는 경우에도 모든 함수들을 수동으로 위임해야함

### 프록시 패턴 구현(3) - 객체 확장

- 객체 직접 변경

```jsx
function patchToSafeCalculator(calculator) {
  const divideOrig = calculator.divide;
  calculator.divide = () => {
    const divisor = calculator.peekValue();
    if (divisor === 0) {
      throw Error("Division by 0");
    }
    return divideOrig.apply(calculator);
  };
  return calculator;
}

const calculator = new StackCalculator();
const safeCalculator = patchToSafeCalculator(calculator);
// ...
```

![프록시 패턴 구현](attachment:b473c32c-c434-4447-86c7-eb9f113848c8:image.png)

### 프록시 패턴 구현(4) - 내장 프록시 (★추천)

- 프록시 패턴을 구현하는 강력한 도구

```jsx
const proxy = new Proxy(target, handler);
```

- `target`: 실제로 작업이 수행될 객체(subject)
- `handler`: 프록시의 동작을 정의하는 객체로, 특정 작업에 대해 **트랩(trap) 함수**를 제공
- 트랩 함수: 작업을 가로채고 추가적인 로직을 실행
  - `get`: 객체의 속성에 접근할 때 호출
  - `set`: 객체의 속성 값을 설정할 때 호출
  - `apply`: 함수 호출을 가로챔
  - `has`: 객체 속성에 `in` 연산자를 사용할 때 호출

```jsx
const safeCalculatorHandler = {
  get: (target, property) => {
    if (property === "divide") {
      // 프록시된 divide 함수
      return function () {
        const divisor = target.peekValue();
        if (divisor === 0) {
          throw Error("Division by 0");
        }
        return target.divide();
      };
    }
    // 프록시 외의 함수 및 속성은 그대로 위임
    return target[property];
  },
};

const calculator = new StackCalculator();
const safeCalculator = new Proxy(calculator, safeCalculatorHandler);

safeCalculator.clear();
safeCalculator.putValue(4);
safeCalculator.putValue(0);
console.log(safeCalculator.divide()); // Error: Division by 0
```

- `get` 트랩은 객체의 속성에 접근할 때 호출
- `divide` 속성에 접근하면, 그 속성에 대한 함수가 새로운 함수로 반환
- 새로운 함수는 0으로 나누려는 시도를 검증 후, 원본 `target` 객체의 `divide` 메서드를 호출
- 다른 속성(예: `putValue`, `getValue`)에 접근할 때는 트랩 함수가 호출되지 않고, 원본 객체의 속성 값이 그대로 반환

| **장점**           | **설명**                                                                                                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **동적 수정**      | `Proxy`는 기존 객체를 수정하지 않고도 그 동작을 동적으로 변경할 수 있습니다. `target[property]`를 사용하여 속성이나 메서드에 대한 접근을 가로채고, 필요한 로직을 추가할 수 있습니다. |
| **확장성**         | `Proxy`를 사용하면 특정 메서드나 속성에 대해서만 변경을 가하고, 나머지 메서드나 속성은 자동으로 위임할 수 있습니다. 기존 코드의 수정 없이 기능을 확장할 수 있습니다.                 |
| **코드 변경 방지** | `Proxy`는 원본 객체의 코드를 변경하지 않으므로 기존 코드의 동작을 방해하지 않으면서 새로운 기능을 추가할 수 있습니다.                                                                |

## 데코레이터

- 기존 객체의 인터페이스를 수정하지 않으면서도 **추가적인 기능을 부여**
- 프록시 패턴과 유사하지만, 프록시는 객체의 동작을 제어하는 반면, 데코레이터는 동작을 확장

![데코레이터](attachment:557d3a00-3857-4478-ae96-9a95ff4d1120:image.png)

```jsx
class RealService {
  fetchData() {
    return "📦 원본 데이터";
  }
}

// 데코레이터 (Decorator) - 기능 추가 (응답에 !!! 추가)
class ExcitingDecorator {
  constructor(service) {
    this.service = service;
  }

  fetchData() {
    return this.service.fetchData() + " 🎉!!!";
  }
}

const realService = new RealService();
const decoratedService = new ExcitingDecorator(realService);

console.log(decoratedService.fetchData());
// 📦 원본 데이터 🎉!!!
```

### 데코레이터 패턴 구현(1) - 객체 컴포지션

- 기존 코드를 수정하지 않고, **새로운 객체를 감싸서 안전한 기능을 추가**하는 방식
- 특정 객체(`EnhancedCalculator`)가 다른 객체(`StackCalculator`)를 내부에 포함하고 (`this.calculator = calculator`) **필요한 기능만 수정하고 나머지는 그대로 사용**하는 방식

```jsx
class EnhancedCalculator {
  constructor(calculator) {
    this.calculator = calculator;
  }
  //새로운 함수
  add() {
    const addend2 = this.getValue();
    const addend1 = this.getValue();
    const result = addend1 + addend2;
    this.putValue(result);
    return result;
  }

  // 위임된 함수들
  putValue(value) {
    return this.calculator.putValue(value);
  }
  getValue() {
    return this.calculator.getValue();
  }
  peekValue() {
    return this.calculator.peekValue();
  }
  clear() {
    return this.calculator.clear();
  }
  multiply() {
    return this.calculator.multiply();
  }
}

const calculator = new StackCalculator();
const enhancedCalculator = new EnhancedCalculator(calculator);

enhancedCalculator.putValue(4);
enhancedCalculator.putValue(3);
console.log(enhancedCalculator.add()); // 4+3 = 7

enhancedCalculator.putValue(2);
console.log(enhancedCalculator.multiply()); // 7*2 = 14
```

- 기존 코드를 수정하지 않고, **새로운 객체를 감싸서 안전한 기능을 추가**하는 방식
- `StackCalculator`를 직접 수정하지 않고도 다른 검증 로직을 추가한 **다양한 버전의 계산기**를 만들 수 있음
- 하나만 프록시하는 경우에도 모든 함수들을 수동으로 위임해야함

### 데코레이터 패턴 구현(2) - 객체 확장

- 객체 직접 변경

  ```jsx
  function patchCalculator(calculator) {
    calculator.add = function () {
      const addend2 = calculator.getValue();
      const addend1 = calculator.getValue();
      const result = addend1 + addend2;
      calculator.putValue(result);
      return result;
    };
  }

  const calculator = new StackCalculator();
  const enhancedCalculator = patchCalculator(calculator);
  // ...
  ```

- 동일한 객체를 참조 후 반환

### 데코레이터 패턴 구현(3) - 내장 프록시 (★추천)

```jsx
const enhancedCalculatorHandler = {
  get(target, property) {
    if (property === "add") {
      // 새로운 함수
      return function add() {
        const addend2 = target.getValue();
        const addend1 = target.getValue();
        const result = addend1 + addend2;
        target.putValue(result);
        return result;
      };
    }

    // 위임된 함수들과 속성들
    return target[property];
  },
};

const calculator = new StackCalculator();
const enhancedCalculator = new Proxy(calculator, enhancedCalculatorHandler);
// ...
```

- `get` 트랩은 객체의 속성에 접근할 때 호출
- `add` 속성에 접근하면, 그 속성에 대한 함수가 새로운 함수로 반환
- 다른 속성(예: `putValue`, `getValue`)에 접근할 때는 트랩 함수가 호출되지 않고, 원본 객체의 속성 값이 그대로 반환

### 데코레이터 패턴 예제

- 특정 패턴의 객체가 DB에 저장될 때마다 알림
- 예시) {a:1}과 같은 패턴을 구독하는 경우, {a:1, b:3} 혹은 {a:1, c:‘x’}와 같은 객체가 데이터베이스에 저장될 경우 알림

```jsx
// db.subscribe() 함수를 추가하여 db 객체를 데코레이트
// 데이터베이스에 put()을 사용하여 데이터를 저장할 때 구독한 패턴과 일치하는지 검사
// 일치하면 listner(콜백)를 실행하여 알림
export function levelSubscribe (db) {
  db.subscribe = (pattern, listener) => {
    db.on('put', (key, val) => {
      const match = Object.keys(pattern).every(
        k => (pattern[k] === val[k])
      )
      if (match) {
	      //  일치하는 속성이 있으면 리스너에게 알림
        listener(key, val)
      }
    })
  }
  return db
}

...
// LevelDB 인스턴스 생성
const db = level(dbPath, { valueEncoding: 'json' })
levelSubscribe(db)

// 특정 패턴 구독 (doctype이 'tweet'이고 language가 'en'인 객체를 감지)
db.subscribe({ doctype: 'tweet', language: 'en' }, (k, val) => console.log(val))

// 데이터 저장 (패턴과 일치하면 콘솔 출력됨)
db.put('1', { doctype: 'tweet', text: 'Hi', language: 'en' })  // ✅ 콘솔 출력
db.put('2', { doctype: 'company', name: 'ACME Co.' })          // ❌ 출력 없음
```

## 프록시 vs 데코레이터

- **프록시** 패턴은 객체에 대한 **접근을 제어**
- **데코레이터** 패턴은 객체에 **새로운 동작을 추가**
- 두 패턴은 상호 보완적이고 때로는 교환 가능한 도구

![image.png](attachment:7973b3aa-5952-4817-8eda-e6eee46c1e31:image.png)

= 딱히 구분하지 맙시다.

## 어댑터

- 기존 객체의 기능을 그대로 유지하면서, 클라이언트가 기대하는 **새로운 인터페이스로 변환**
- 다른 시스템이나 클래스들이 **서로 호환되지 않을 때**, 객체의 인터페이스를 연결해주는 역할

![image.png](attachment:bbae7da5-3d89-45cb-98ab-e55a05359bb8:image.png)

- 클라이언트가 `methodA()`를 호출 → 어댑터가 이를 받아 `methodC()`, `methodD()` 로 변환하여 대상에 전달
- 클라이언트가 `methodB()`를 호출 → 어댑터가 이를 받아 `methodD()`로 변환하여 대상에 전달

```jsx
class RealService {
  fetchData() {
    return "📦 원본 데이터";
  }
}

// 어댑터 (Adapter) - fetchData()를 getData()로 변환
class DataAdapter {
  constructor(service) {
    this.service = service;
  }

  getData() {
    return this.service.fetchData(); // fetchData()를 getData()로 변환
  }
}

const realService = new RealService();
const adaptedService = new DataAdapter(realService);

console.log(adaptedService.getData());
// 📦 원본 데이터
```

### 어댑터 패턴 구현

```jsx
export function createFSAdapter(db) {
  return {
    readFile(filename, options, callback) {
      // ...
    },
    writeFile(filename, contents, options, callback) {
      // ...
    },
  };
}
```

- `createFSAdapter` 함수는 **LevelDB**(`db`)를 이용해 파일 시스템처럼 동작하는 인터페이스를 제공
- LevelDB를 사용하면서, `fs` 모듈의 메서드처럼 파일 읽기와 쓰기 가능

```jsx
readFile (filename, options, callback) {
  if (typeof options === 'function') {
    callback = options
    options = {}
  } else if (typeof options === 'string') {
    options = { encoding: options }
  }

  db.get(resolve(filename), { valueEncoding: options.encoding }, (err, value) => {
    if (err) {
      if (err.type === 'NotFoundError') {
        err = new Error(`ENOENT, open "${filename}"`)
        err.code = 'ENOENT'
        err.errno = 34
        err.path = filename
      }
      return callback && callback(err)
    }
    callback && callback(null, value)
  })
}
```

- 파일을 읽는 함수 (DB에서 읽어옴)
- `options`가 함수로 들어오면, 이를 `callback`으로 간주하고 `options`는 기본값 `{}`로 설정합니다.
- `options`가 문자열이라면, `encoding`을 설정합니다.
- `db.get()`을 사용해서 LevelDB에서 `filename`에 해당하는 값을 가져옵니다. 이때 `resolve(filename)`은 파일 경로를 절대 경로로 변환합니다.
- 파일이 없으면 `ENOENT` 오류를 반환합니다. (파일이 없다는 의미)
- 파일을 찾으면, 콜백을 호출하여 파일의 내용을 반환합니다.

```jsx
writeFile (filename, contents, options, callback) {
  if (typeof options === 'function') {
    callback = options
    options = {}
  } else if (typeof options === 'string') {
    options = { encoding: options }
  }

  db.put(resolve(filename), contents, { valueEncoding: options.encoding }, callback)
}
```

- 파일을 쓰는 함수 (DB에 저장)
- `options`가 함수로 들어오면, 이를 `callback`으로 간주하고 `options`는 기본값 `{}`로 설정합니다.
- `options`가 문자열이라면, `encoding`을 설정합니다.
- `db.put()`을 사용하여 LevelDB에 `filename`에 해당하는 파일을 저장합니다. 이때 `resolve(filename)`은 파일 경로를 절대 경로로 변환하고, 파일 내용을 `contents`로 설정하여 저장합니다.

```jsx
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import level from "level";
import { createFSAdapter } from "./fs-adapter.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const db = level(join(__dirname, "db"), { valueEncoding: "binary" });
const fs = createFSAdapter(db);
```

- DB에 연결 후 fs객체 생성
- fs는 DB를 사용하여 만든 어댑터 객체 (readFile과 writeFile 제공)
- DB를 활용해 파일 시스템 API처럼 사용 가능
- `fs.readFile`과 `fs.writeFile`을 사용하여 **파일 읽기와 쓰기를 할 수 있도록 LevelDB에 맞게 변환**

## 요약

```jsx
// 🎯 1. 기본 서비스 클래스
class RealService {
  fetchData() {
    return "📦 원본 데이터";
  }
}

// 🎯 2. 프록시 (Proxy) - 요청을 가로채고 로깅 추가
class LoggingProxy {
  constructor(service) {
    this.service = service;
  }

  fetchData() {
    console.log("🛑 프록시: 요청을 로깅 중...");
    return this.service.fetchData();
  }
}

// 🎯 3. 데코레이터 (Decorator) - 기능 추가 (응답에 !!! 추가)
class ExcitingDecorator {
  constructor(service) {
    this.service = service;
  }

  fetchData() {
    return this.service.fetchData() + " 🎉!!!";
  }
}

// 🎯 4. 어댑터 (Adapter) - fetchData()를 getData()로 변환
class DataAdapter {
  constructor(service) {
    this.service = service;
  }

  getData() {
    return this.service.fetchData(); // fetchData()를 getData()로 변환
  }
}
```

- **프록시** 패턴은 기존 객체에 대한 **접근을 제어**하는 데 유용
- **데코레이터** 패턴은 기존 객체에 **추가적인 기능**을 부여
- **어댑터** 패턴은 기존 객체의 인터페이스를 **다른 형태로 변환**하여 호환성을 유지
