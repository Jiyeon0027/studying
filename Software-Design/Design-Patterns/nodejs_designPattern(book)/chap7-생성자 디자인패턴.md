## 7-1 팩토리(Factory) 패턴

> 노트
>
> - 팩토리는 객체 생성 로직을 감싸, **생성(Implementation)과 사용(Interface)을 분리**합니다.
> - JavaScript 특성(동적 타이핑, 함수 1급 객체, 프로토타입 기반) 덕분에,전통적 OOP 스타일보다 훨씬 **유연하게 객체를 생성**할 수 있게 해줍니다.
>
> [(동적 타이핑, 함수 1급 객체, 프로토타입 기반)](https://www.notion.so/1-ab4df62a6c1048e7862be95ba333e798?pvs=21)

---

### 1) 팩토리 패턴의 핵심 아이디어

- **객체 생성 로직을 한 곳에 캡슐화**함으로써, 구현 세부사항을 숨기고 유연성을 높임
- `new` 키워드를 직접 사용하기보다, **함수**를 통해 객체 생성 과정을 감싸는 방식
- **특정 조건**에 따라 **서로 다른 객체**를 반환할 수도 있음 (예: 이미지 확장자별로 다른 객체)

```jsx
function createImage (name) {
	if (name.match(/\.jpe?g$/)) {
		return new ImageJpeg(name)
	} else if (name.match(/\.gif$/)) {
		return new ImageGif(name)
	} else if (name.match(/\.png$/)) {
		return new ImagePng(name)
	} else {
		throw new Error('Unsupported format') }
	}
}
```

---

### 2) 장점

1. **구현 교체나 확장 용이**
   - 내부에서 어떤 클래스나 방식을 써서 객체를 만들지, 호출자는 알 필요 없음
   - 필요한 경우, 팩토리 코드만 수정하면 됨 (나머지 호출부 전혀 변경 X)
2. **작은 노출 면(Encapsulation)**

   - 팩토리는 함수이므로 클래스 자체를 외부에 노출하지 않아도 됨
   - 캡슐화를 강화하고, **프라이빗 멤버**를 구현하기에도 유리(클로저 활용)

   ```jsx
   function createPerson(name) {
     const privateProperties = {};
     const person = {
       setName(name) {
         if (!name) {
           throw new Error("A person must have a name");
         }
         privateProperties.name = name;
       },
       getName() {
         return privateProperties.name;
       },
     };

     person.setName(name);
     return person;
   }
   ```

3. **동적 타이핑의 활용**
   - 조건에 따라 전혀 다른 형태(클래스 인스턴스 / 단순 객체 리터럴)를 반환해도 문제없음
   - “덕 타이핑(Duck Typing)”으로 인터페이스만 맞으면 동일하게 취급 가능

---

### 3) 간단 예시: 프로파일러(Profiler) 만들기

### 구조

```jsx
// profiler.js
class Profiler {
  constructor(label) {
    this.label = label;
    this.lastTime = null;
  }

  start() {
    this.lastTime = process.hrtime();
  }

  end() {
    const diff = process.hrtime(this.lastTime);
    console.log(
      `Timer "${this.label}" took ${diff[0]} seconds ` +
        `and ${diff[1]} nanoseconds.`
    );
  }
}

const noopProfiler = {
  start() {},
  end() {},
};

export function createProfiler(label) {
  if (process.env.NODE_ENV === "production") {
    return noopProfiler;
  }
  return new Profiler(label);
}
```

- `createProfiler` 함수(팩토리):
  - 프로덕션(`production`) 환경이면 **빈 객체(noopProfiler)**를 반환 → 성능 영향 최소화
  - 팩토리를 사용하여 Profile 객체의 생성을 추상화 함 → 개발 환경이면 **Profiler 인스턴스** 반환 → 실제 코드 프로파일링 수행

### 사용 예시

```jsx
// index.js
import { createProfiler } from "./profiler.js";
function getAllFactors(intNumber) {
  const profiler = createProfiler(`Finding all factors of ${intNumber}`);

  profiler.start();
  const factors = [];
  for (let factor = 2; factor <= intNumber; factor++) {
    while (intNumber % factor === 0) {
      factors.push(factor);
      intNumber = intNumber / factor;
    }
  }
  profiler.end();

  return factors;
}

const myNumber = process.argv[2];
const myFactors = getAllFactors(myNumber);
console.log(`Factors of ${myNumber} are: `, myFactors);
```

- 팩토리를 통해 **환경에 따라 다른 객체**를 리턴하지만, 사용자는 동일 인터페이스(`start`, `end`)만 호출

---

### 4) 실제 사례

- 예: **Knex** SQL 쿼리 빌더
  - `require('knex')`로 가져온 뒤, `knex({ ...config })` 같은 식으로 호출
  - 내부에서 DB 엔진( dialect )등에 따라 **맞춤형 객체**를 생성해 반환

---

## 핵심 요약

- **팩토리 패턴**은 JavaScript에서 **객체 생성 로직**을 깔끔하게 캡슐화하는 대표적 방법
- 클로저, 동적 타이핑 등을 활용해 전통적 OOP보다 **더 유연하고 강력**한 접근이 가능
- 구현 교체, 노출 면 축소, 조건별 객체 반환 등에 유리하여 Node.js에서도 널리 활용됨

## 7-2 빌더(Builder) 패턴

> - 빌더 패턴은 **복잡한 객체 생성 로직**을 여러 단계로 나누어 **유창한 인터페이스(fluent interface)**를 제공
> - 인자가 복잡하거나 개수가 많은 생성자를 대체해 **가독성**과 **사용성**을 높이는 전형적 해결책

---

### 1) 빌더 패턴의 동기

- **긴 인자 목록** 또는 **복잡한 매개변수**를 요구하는 생성자가 있을 때 사용
- 사용자에게 **일관되고 유효한** 객체 생성을 강제하도록 인터페이스 제공
- 종종 “하나의 객체 리터럴”로 간단히 개선 가능하지만, 빌더를 쓰면 더욱 **가이드가 명확**해짐
  - 읽기 쉬우면서 자체 문서화가 가능한 유연한 인터페이스를 제공하여, 일관된 객체 생성을 위한 지침을 제공할 수 있음

---

### 2) 빌더 패턴 구조

1. **Builder 클래스**
   - 복잡한 인자를 **일련의 메서드**(`withXxx`, `setXxx`)로 나눠 호출
   - 호출할 때마다 **this**(빌더 인스턴스)를 반환 → **메서드 체이닝** 가능
2. **build()**
   - 빌더에 모인 모든 인자 정보로 **최종 객체** 생성
   - 결과 객체는 **일관된**(valid) 상태 보장

### 예: `BoatBuilder`

```jsx
// 일반적인 해결법 (객체 리터럴)
class Boat {
	constructor (allParameters) {
		// ...
	}
}

const myBoat = new Boat({
	hasMotor: true,
	motorCount: 2,
	motorBrand: 'Best Motor Co. ',
	motorModel: 'OM123',
	hasSails: true,
	sailsCount: 1,
	sailsMaterial: 'fabric',
	sailsColor: 'white',
	hullColor: 'blue',
	hasCabin: false
})

class BoatBuilder {
	withMotors (count, brand, model) {
		this.hasMotor = true
		this.motorCount = count
		this.motorBrand = brand
		this.motorModel = model
		return this
	}

	withSails (count, material, color) {
		this.hasSails = true
		this.sailsCount = count
		this.sailsMaterial = material
		this.sailsColor = color
		return this
	}

	hullColor (color) {
		this.hullColor = color return this
	}

	withCabin () {
		this.hasCabin = true
		return this
	}

	build() {
		return new Boat({
			hasMotor: this.hasMotor,
			motorCount: this.motorCount,
			motorBrand: this.motorBrand,
			motorModel: this.motorModel,
			hasSails: this.hasSails,
			sailsCount: this.sailsCount,
			sailsMaterial: this.sailsMaterial,
			sailsColor: this.sailsColor,
			hullColor: this.hullColor,
			hasCabin: this.hasCabin
		})
	}
}

// 빌더를 사용해서 boat 객체를 생성
const myBoat = new BoatBuilder()
	.withMotors(2, 'Best Motor Co. ', 'OM123')
	.withSails(1, 'fabric', 'white')
	.withCabin()
	.hullColor('blue')
	.build()

```

- **장점**: 필요한 속성만 `withXxx()` 메서드 체이닝으로 직관적 설정,최종적으로 `build()` 시에만 실제 객체 생성

---

### 3) 사용 예시: `UrlBuilder`

```jsx
import { UrlBuilder } from "./urlBuilder.js";

const url = new UrlBuilder()
  .setProtocol("https")
  .setAuthentication("user", "pass")
  .setHostname("example.com")
  .build();

console.log(url.toString()); // "https://user:pass@example.com"
```

- **인터페이스 가독성** 향상: 각 메서드가 어떤 인자를 설정하는지 명확
- **일관성**: `build()`가 호출되기 전까지 완성된 객체가 아니라,모든 필수 정보가 모였을 때만 최종 객체를 생성

---

### 4) 실전 사례

- **HTTP(S) 요청 라이브러리** 예: `superagent`
  - `.post(...)`, `.send(...)`, `.set(...)` 등을 메서드 체이닝으로 호출
  - 마지막에 `.then(...)` (또는 `await`)으로 실제 네트워크 요청 수행
  - 내부적으로 **빌더 패턴**을 적용, 복잡한 설정을 명료하게 표현

---

## 핵심 요약

- 빌더 패턴은 **매개변수나 설정이 많은** 복잡한 생성 로직을 **단계별**로 체계화하여 제공
- 메서드 체이닝과 `build()` 과정을 통해 **일관되고 유효한** 최종 객체를 생성
- Node.js 환경에서 **HTTP 요청**, **옵션이 많은 객체** 등을 쉽게 만들 수 있는 **일반적이고 강력한 패턴**

## 7-3 공개 생성자(Revealing Constructor) 패턴

> - 공개 생성자는 GoF 디자인 패턴 책에는 없는, JS/Node 커뮤니티에서 탄생한 패턴
> - **객체가 생성될 때만** 내부 기능 일부를 노출하여 조작 가능하게 하며,이후에는 **완전히 캡슐화**되는 객체를 만들 때 유용

---

### 1) 핵심 아이디어

- **생성자**가 호출될 때, **실행자 함수**(executor)를 인자로 받음
- 실행자 함수에 객체 내부의 일부 멤버(수정 권한 등을 가진 ‘revealedMembers’)를 전달
- 객체 생성이 완료되면, 그 ‘revealedMembers’는 더 이상 외부에서 접근할 수 없도록 함
- 결과적으로 **생성 직후**만 객체 내부를 조작할 수 있고, 이후엔 **불변(Immutable) 상태** 유지 가능

```

const object = new SomeClass(function executor(revealedMembers) {
  // revealedMembers를 사용해 내부 상태 조작
});

```

---

### 2) 적용 시나리오

1. 생성시 ‘단 한 번’만 설정할 수 있는 옵션이나 초기화 로직이 필요한 경우
2. **생성 이후 변경 불가한(Immutable) 객체**를 만들 때
3. 특정 속성(또는 메서드)을 **생성 과정에서만** 공개하고, 이후 **캡슐화**하고 싶을 때

---

### 3) 예시: 변경 불가능한(Immutable) Buffer

```jsx
// immutableBuffer.js
const MODIFIER_NAMES = ["swap", "write", "fill"];

export class ImmutableBuffer {
  constructor(size, executor) {
    const buffer = Buffer.alloc(size);
    const modifiers = {};

    // 1. 수정 가능한 함수(swap, write, fill 등)만 따로 추려내서 `modifiers`에 바인딩
    for (const prop in buffer) {
      if (typeof buffer[prop] !== "function") continue;
      if (MODIFIER_NAMES.some((m) => prop.startsWith(m))) {
        modifiers[prop] = buffer[prop].bind(buffer);
      } else {
        // 2. 나머지 읽기용 함수는 this에 직접 붙여 노출
        this[prop] = buffer[prop].bind(buffer);
      }
    }

    // 3. 생성 시점에만 실행자 함수를 통해 내부 buffer 수정
    executor(modifiers);
  }
}
```

### 사용 예시

```jsx
import { ImmutableBuffer } from "./immutableBuffer.js";

const hello = "Hello!";
const immutable = new ImmutableBuffer(hello.length, ({ write }) => {
  write(hello); // 생성 시점에만 write 가능
});

console.log(String.fromCharCode(immutable.readInt8(0))); // 'H'

// 아래 코드를 실행하면 에러 발생 (불변 객체이므로 write 불가)
// immutable.write('Hello?');
```

- **executor**가 노출하는 `modifiers` 객체를 통해서만 **생성 단계**에서 데이터를 쓸 수 있음
- 이후엔 `readInt8()`, `toString()`, 등 **읽기 전용 메서드**만 사용 가능 → **Immutable** 특성

---

### 4) 실제 사례

- **Promise**(ES6 표준)
  - `new Promise((resolve, reject) => { ... })`
  - 생성자( executor )에서만 `resolve`, `reject`를 호출 가능
  - 일단 생성된 뒤에는 **상태를 외부에서 함부로 변경 불가**
- **협업**이나 **공유 라이브러리**에서 **객체의 무결성**과 **캡슐화**를 보장해야 할 때 활용

---

## 핵심 요약

- **공개 생성자 패턴**은 생성 시점에만 내부 수정 권한을 노출해,이후에는 객체를 안전하게 **불변** 혹은 **제한적**으로 유지 가능
- Node.js 예시로 `ImmutableBuffer`, 표준 `Promise`가 대표적
- “한 번 생성되면 변경 불가” 객체를 만들어 **안정성**과 **캡슐화**를 극대화할 수 있음

### 7-4 싱글톤(Singleton)

- **개념**

  - 클래스의 인스턴스를 **오직 한 번**만 생성해, 애플리케이션 전역에서 공유
  - 주로 **상태 공유**나 **리소스 할당 최적화**가 필요할 때 사용 (예: DB 연결 풀)

- **Node.js에서의 싱글톤 구현**

  1. **모듈 캐싱** 활용

     ```jsx
     // dbInstance.js
     import { Database } from "./Database.js";
     export const dbInstance = new Database(/* ... */);
     ```

     - `import { dbInstance }`로 가져다 쓰면, 내부적으로 한 번만 생성된 인스턴스를 공유
     - 단, **패키지 경로**마다 캐시가 달라질 수 있으므로 버전이 다른 동일 패키지를 중첩으로 설치하면 **여러 인스턴스**가 생길 수 있음

  2. **Global** 사용

     ```jsx
     global.dbInstance = new Database(/* ... */);
     ```

     - **전역**으로 하나의 인스턴스를 공유하지만, 전역 오염 및 네임스페이스 충돌 위험

- **주의사항**
  - Node.js는 모듈 캐싱을 패키지(버전) 단위로 처리하므로, **진짜 싱글톤 보장**은 어려울 수 있음
  - 일반적으로 애플리케이션 메인 모듈 수준에서만 신경 쓰면 문제가 없는 경우가 많음
  - 가급적 **무상태(stateless) 모듈**이 권장

---

### 7-5 모듈 와이어링(Module Wiring)

### 1) 싱글톤 종속성(직접 모듈 임포트)

- **직접 import**를 통해 각 모듈이 필요로 하는 것을 싱글톤 형태로 결합
  - 예: `blog.js`에서 `dbInstance.js`를 직접 `import`
  - 장점: **간단**, **사용 편리**
  - 단점: **결합도가 높아** 다른 DB 구현으로 바꾸기 어렵고, 테스트/모킹이 까다로움

### 2) 종속성 주입(DI, Dependency Injection)

- **컴포넌트 간 결합**을 줄이고 **재사용성**을 높이는 기법
- **외부**에서 필요한 종속성들을 **주입**(Constructor Injection 등)
  - 예: `blog.js`가 DB 모듈을 직접 import하지 않고, 생성 시점에 `new Blog(db)`로 전달
  - “Blog”는 오직 “db.run(), db.all() 등”이 필요하다는 **인터페이스**만 전제
  - DB를 SQLite, Postgres 등 **어떤 구현체**로도 교체 가능

```jsx
// blog.js
export class Blog {
  constructor(db) {
    this.db = db;
    // ...
  }
  // ...
}
```

```jsx
// index.js (인젝터 역할)
import { createDb } from "./db.js";
import { Blog } from "./blog.js";

const db = createDb("data.sqlite");
const blog = new Blog(db);
// ...
```

- **장점**:
  - 테스트/교체 **유연성** 증가 (모킹, 다른 DB 등)
  - 컴포넌트 재사용 가능성 향상
- **단점**:
  - 종속성 그래프가 복잡해지면, **설정(와이어링) 로직**이 많아짐
  - 로드 순서, 의존 객체 생성 타이밍 고려 필요

## 핵심 요약

- **싱글톤**
  - 모듈 내 `export`로 쉽게 유사 싱글톤 구현 → 대부분의 단일 인스턴스 공유 시 충분
  - 다중 버전 설치 혹은 다른 패키지 구조 등으로 “진짜 전역 싱글톤”이 깨질 수 있음
- **종속성 주입(DI)**
  - 필요한 의존 객체를 외부에서 주입받아 **낮은 결합, 높은 유연성** 달성
  - 대규모 애플리케이션에서 확장성, 테스트 편의성 확보에 유리
  - 추가 설정/구조 관리가 필요하여 복잡도가 증가할 수 있음
