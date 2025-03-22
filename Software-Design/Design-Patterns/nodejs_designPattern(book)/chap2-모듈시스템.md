## # 모듈이란?

- 애플리케이션을 개발할 때 구조화하기 위한 부품
- 코드를 독립적으로 개발하고 테스트 가능한 작은 유닛으로 나누게 해줌
- 모듈내의 모든 함수와 변수들을 비공개로 유지하여 정보에 대한 은닉성을 강화시켜줌

## **# JavaScript와 Node.js에서의 모듈 시스템**

---

- 브라우저 관점에서 코드베이스는 여러 파일로 분할될 수 있으며 다른 <script> 태그를 사용하여 임포트될 수 있음. 초반에는 이러한 구조가 웹 페이지를 만드는데 문제 없었음
- JavaScript 브라우저 애플리케이션이 점점 복잡해지고 jQuery, Backbone, Angular와 같은 프레임워크가 생태계를 점유해나가면서 JavaScript 커뮤니티에는 모듈 시스템을 정의하기 위한 여러 시도가 나타나기 시작함
  가장 성공적인 것이 AMD이며, RequireJS에 의해서 대중화되었고 그 후에는 UMD가 나오게 됨
- Node.js가 처음 만들어졌을 때, 운영체제의 파일시스템에 직접적으로 접근하는 JavaScript를 위한 서버 런타임으로 구성됨
  이때 HTML <script>와 URL을 통한 리소스 접근에 의존하지 않고, 오직 로컬 파일시스템의 JavaScript 파일들에만 의존. 이 모듈 시스템을 도입하기 위해 JavaScript 모듈 시스템을 제공할 수 있도록 고안된 CommonJS의 명세를 구현하게 됨

[CommonJS vs ES modules](https://www.notion.so/CommonJS-vs-ES-modules-34e886afe7b5481caa99cf8748435366?pvs=21)

- CommonJS는 그것의 시작과 함께 Node.js에서 주된 모듈 시스템이 되었고 2015년에 ESM이 나오게 됨 ESM은 문법과 의미론적 관점에서 ESM을 위한 공식적인 명세만을 정의하고 구체적인 구현을 제공하지 않음
  다른 여러 브라우저 회사들과 Node.js 커뮤니티가 확실한 명세를 구현하는데 몇년이 소요됨
  앞으로는 ESM 형태의 모듈이 지배적인 표준이 되는 데에는 어느 정도 시간이 소요될 것임

## **# 모듈 시스템과 패턴**

---

### **1. 노출식 모듈 패턴**

JavaScript의 주요 문제점 중 하나는 네임스페이스가 없다는 것 → 모든 스크립트는 전역 범위에서 실행됨
따라서 내부 애플리케이션 코드나 종속성 라이브러리가 그들의 기능을 노출시키는 동시에 스코프를 오염시킬 수 있음

이러한 문제를 해결하기 위한 보편적인 기법은 **노출식 모듈 패턴**을 사용하는 것이며, 다음과 같은 형식을 보임

```jsx
const myModule = (() => {
  const privateFoo = () => {};
  const privateBar = [];

  const exported = {
    publicFoo: () => {},
    publicBar: () => {},
  };

  return exported;
})();

console.log(myModule);
console.log(myModule.privateFoo, myModule.privateBar);
```

이 패턴은 자기 호출 함수를 사용함
이러한 종류의 함수를 즉시 실행 함수 표현 이라고 부르며 private 범위를 만들고 공개될 부분만 내보내게 됨
로그로 출력한 내용은 다음과 같습니다.

![로그 출력 결과](https://blog.kakaocdn.net/dn/nhOzL/btrfPJoOp4F/S0zFGBni7dFyXV7LPqio4K/img.png)

위에서 보여주듯이 myModule로부터 직접 접근이 가능한 것은 익스포트 된 객체뿐이라는 것을 알 수 있음
노출식 모듈 패턴은 CommonJS 모듈 시스템에서 사용됨

## **# CommonJS 모듈**

---

CommonJS는 Node.js 첫 번째 내장 모듈 시스템임
Node.js의 CommonJS는 명세를 고려하여 추가적인 자체 확장 기능과 함께 구현됨

CommonJS 명세의 두 가지 주요 개념

- require는 로컬 파일 시스템으로부터 모듈을 임포트하게 해줌
- exports와 module.exports는 특별한 변수로서 현재 모듈에서 공개될 기능들을 내보내기 위해서 사용됨

### **1. 모듈 정의**

모듈을 만들고 정의하는 것은 아래와 같은 코드로 동작할 수 있음
여기서 log 함수는 private 함수로써 보여지지 않는 객체 혹은 함수이며, require()을 통해 함수를 공개시킬 수 있음

```jsx
function log() {
  console.log("Hello world");
}

module.exports.run = () => {
  log();
};
```

기억해야 할 개념은 module.exports 변수에 할당되지 않는 이상, 모듈 안의 모든 것이 비공개라는 것
require()를 사용하여 모듈을 로드할 때 변수의 내용은 캐시되고 리턴됨

### **2. module.exports 대 exports**

변수 exports는 module.exports의 초기 값에 대한 참조
우리는 이 값이 본질적으로 모듈이 로드되기 전에 만들어지는 간단한 객체 리터럴이라는 것을 확인함
즉 exports의 객체에 속성을 추가하는 것은 가능하지만 **exports 자체를 할당하는 것은 아무런 효과가 없다는 것**을 아래에서 확인할 수 있음

```jsx
exports.hello = () => {
  console.log("hello");
};
```

```jsx
exports = () => {
  console.log("hello");
};
```

```jsx
module.exports = () => {
  console.log("hello");
};
```

### **3. 모듈 정의 패턴**

- API를 정의하기 위한 도구임
- API 디자인과 관련된 문제들의 경우 고려해야 할 주요 요소는 pirvate 함수와 public 함수 간의 균형
- 이것의 목표는 확장성과 코드 재사용 같은 소프트웨어 품질과의 균형을 유지하면서 정보 은닉 및 API 유용성을 극대화하는 것

### **4. exports 지정하기**

public API를 공개하는 가장 기본적인 방법은 exports 에 할당하는 것
이렇게 하면 exports에서 참조하는 객체의 속성에 공개할 모든 값을 할당함 → 외부에 공개된 객체는 일련의 관련 기능에 대한 컨테이너 또는 네임스페이스가 됨

```jsx
// logger.js 파일
exports.info = (msg) => {
  console.log(`info : ${msg}`);
};

exports.verbose = (msg) => {
  console.log(`verbose : ${msg}`);
};
```

### **5. 함수 내보내기**

- 가장 일반적인 모듈 정의 패턴 중 하나가 module.exports 변수 전체를 함수로 재할당하는 것임 → 서브스택패턴
- 주요 장점은 모듈에 대한 명확한 진입점을 제공하는 단일 기능을 제공하여 그것에 대한 이해와 사용을 단순화 하는 것임

```jsx
// logger.js 파일
module.exports = (msg) => {
  console.log(`info : ${msg}`);
};

module.exports.verbose = (msg) => {
  console.log(`info : ${msg}`);
};
```

### **6. 클래스 내보내기**

- 클래스를 내보내는 모듈은 함수를 내보내는 모듈이 특화
- 이점은 이 새로운 패턴을 통해 사용자에게 생성자를 사용하여 새 인스턴스를 만들 수 있게 하면서, 프로토타입을 확장하고 새로운 클래스를 만들 수 있는 기능을 제공할 수 있음

```jsx
// logger.js 파일
class Logger {
	constructor(name) {
    	this.name = name;
    }

    log(msg) {
    	console.log(`[${this.name}`] ${msg}`);
    }
}

module.exports = Logger
```

### **7. 인스턴스 내보내기**

- 우리는 require()의 캐싱 메커니즘 도움을 통해 생성자나 팩토리로부터 서로 다른 모듈 간에 공유할 수 있는 상태 저장 인스턴스를 쉽게 정의할 수 있음
- **싱글톤 패턴 구현 가능 → 일관된 상태와 동작을 유지하고, 메모리 사용을 최적화하며, 코드의 가독성과 유지보수성을 향상시키는 등의 여러 가지 장점**
  - `require()`는 모듈을 한 번만 로드하고 캐시에 저장하기 때문에, 모든 모듈이 동일한 인스턴스를 공유하게 됨
  - **장점**: 애플리케이션 전역에서 동일한 인스턴스를 사용하여 일관된 상태와 동작을 보장할 수 있음

```jsx
// logger.js 파일
class Logger {
	constructor(name) {
    	this.name = name;
    }

    log(msg) {
    	console.log(`[${this.name}`] ${msg}`);
    }
}

module.exports = new Logger('DEFAULT');
```

## **# ESM 모듈**

---

- ESM 모듈은 ECMAScript 2015 명세의 일부분으로 JavaScript에 서로 다른 실행 환경에서도 적합한 공식 모듈 시스템을 부여하기 위해 도입됨
- ESM 명세는 CommonJS나 AMD와 같은 기존의 모듈 시스템에 있는 좋은 방안들은 유지하려고 했고, 문법은 매우 간단하면서 짜임새를 갖추고 있음
- 순환 종속성에 대한 지원과 비동기적 모듈을 로드할 수 있는 방법을 제공함

ESM과 CommonJS 사이의 가장 큰 차이점

- ES 모듈은 static이라는 것
- 임포트가 모든 모듈의 가장 상위 레벨과 제어 흐름 구문의 바깥쪽에 기술됨
- 임포트할 모듈의 이름을 코드를 이용하여 실행 시에 동적으로 생성할 수 없으며, 상수 문자열만이 허용됨

```jsx
if (condition) {
	import module1 from 'module1'
else {
	import module2 from 'module2'
}
```

CommonJS에서는 다음과 같이 작성하는 것이 전혀 문제되지 않음

```jsx
let module = null;
if (condition) {
	module = require('module1')
else {
	module = require('module2')
}
```

### **1. Node.js에서 ESM 사용**

- Node.js는 모든 .js 파일이 CommonJS 문법을 기본으로 사용함
- .js 파일에 ESM 문법을 사용한다면 인터프리터는 에러를 냄

Node.js 인터프리터가 CommonJS 모듈 대신 ES 모듈을 받아들일 수 있는 몇 가지 방법

- 모듈 파일의 확장자를 .mjs 로 합니다.
- 모듈과 가장 근접한 package.json의 "type" 필드에 "module" 을 기재합니다.

### **2. exports와 imports 지정하기**

- ESM모듈에서는 기본적으로 모든 것이 private이며 export된 개체들만 다른 모듈에서 접근 가능
- export 키워드는 우리가 모듈 사용자에게 접근을 허용하는 개체 앞에 사용함

```jsx
// logger.js

// 'log'로서 함수를 익스포트
export function log(message) {
  console.log(message);
}

// 'DEFAULT_LEVEL'로서 상수를 익스포트
export const DEFAULT_LEVEL = "info";

// 'LEVELS'로서 객체를 익스포트
export const LEVELS = {
  error: 0,
  debug: 1,
  warn: 2,
  data: 3,
  info: 4,
  verbose: 5,
};

// 'Logger'로서 클래스를 익스포트
export class Logger {
  constructor(name) {
    this.name = name;
  }

  log(message) {
    console.log(message);
  }
}
```

- 우리가 모듈로부터 원하는 개체를 임포트하고 싶다면 import 키워드를 사용함
- 문법은 꽤나 유연하고 하나 이상의 개체를 임포트할 수 있으며 다른 이름으로도 지정 가능

```jsx
import * as loggerModule from "./logger.js";
console.log(loggerModule);
```

이번 예제에서는 모듈의 모든 멤버를 임포트하고 loggerModule 변수에 할당하기 위해서 \* 문법을 사용함

![](https://blog.kakaocdn.net/dn/nhjl5/btrfO5zudmv/FUFkjTDmJ24QpsLZKY8GsK/img.png)

만약 규모가 큰 모듈을 사용하고자 할 때, 모듈의 모든 기능을 원하지 않고 하나 혹은 몇개의 개체만을 사용하고 싶을 때 아래의 방법이 존재함

```jsx
import { log } from "./logger.js";
log("hello world");
```

하나 이상의 개체를 임포트하고 싶을 때에는 다음과 같이 합니다.

```jsx
import { log, Logger } from "./logger.js";
log("hello world");
const logger = new Logger("DEFAULT");
logger.log("hello world");
```

임포트되는 개체의 이름을 as 키워드로 바꾸어줄 수 있음

```jsx
import { log as log2 } from "./logger.js";
log2("hello world");
```

### **3. export와 import 기본 값 설정하기**

- CommonJS에서 가장 많이 사용되는 특성은 이름이 없는 하나의 개체를 module.exports에 할당하여 익스포트 할 수 있다는 것
- ESM에서도 비슷한 동작을 할 수 있는데, **export default** 키워드를 사용하여 처리 할 수 있음

```jsx
// logger.js
export default class Logger {
  constructor(name) {
    this.name = name;
  }

  log(msg) {
    console.log(msg);
  }
}
```

이 경우에 Logger라는 이름이 무시되며, 익스포트되는 개체는 default 라는 이름 아래 등록됨

```jsx
// main.js

import MyLogger from './logger.js'
constr logger = new MyLogger('DEFAULT')
logger.log('hello world')
```

### **4. 혼합된 export**

ESM 모듈에서는 이름이 지정된 export와 default export를 혼합하여 사용 가능함

```jsx
// logger.js
export default function log(msg) {
  console.log(msg);
}

export function info(msg) {
  log(`info : ${msg}`);
}
```

우리가 가진 default export와 이름을 가진 export를 임포트 하기를 원한다면 다음과 같은 형식을 사용함

```jsx
// main.js

import MyLogger, { info } from "./logger.js";
```

- 이 예제에서는 logger.js로부터 default export를 MyLogger라는 이름으로, 그리고 info를 임포트함

→ 정리하면, 하나의 기능을 익스포트 하고 싶을 경우에는 default export를 사용하되, 이름을 사용한 export 사용에 습관을 들이는 것이 일반적으로 좋은 방법

## **# 모듈의 수정**

---

- 읽기 전용 라이브 바인딩인 ESM 모듈을 통해 개체들을 임포트하였고, 외부 모듈에서 그것을 재 할당하는 것이 불가능함
- default export나 이름을 갖는 export의 바인딩을 바꿀 수 없는 것은 사실이지만, 바인딩이 **_객체_**라면 우리는 여전히 객체의 특정 속성을 변경하는 것이 가능함

```jsx
// mock-read-file.js
import fs from "fs";

const originalReadFile = fs.readFile;
let mockedResponse = null;

function mockedReadFile(path, cb) {
  setImmediate(() => {
    cb(null, mockedResponse);
  });
}

export function mockEnable(respondWith) {
  mockedResponse = respondWith;
  fs.readFile = mockedReadFile;
}

export function mockDisable() {
  fs.readFile = originalReadFile;
}
```

- 처음으로 fs 모듈을 임포트하여 fs.readFile함수를 저장 → fs.readFile의 함수를 변경하는 로직이 있기 때문에 원래의 함수 로직을 저장하는 것임
- mockedReadFile에서는 콜백함수를 받아서 처리하는 부분임 → mockedResponse 객체를 콜백 함수에 넘겨주는 역할 밖에 하지 않음
- 다음 mockEnable은 fs.readFile의 함수를 변경하는 역할 → 그 반대는 mockDisable 함수

간단한 로직을 통해 모듈을 수정 가능함

```jsx
// main.js
import fs from 'fs'
import { mockEnable, mockDisable } from './mock-read-file.js'

mockEnable(buffer.from('hello world'))

fs.readFile('fake-path', (err, data) {
	if (err) console.error(err)
    console.log(data.toString())
})

mockDisable()
```

- 정리하면 모듈을 수정하는 일은 별로 좋은 판단은 아님
- 모듈의 구조를 변경하거나 기능을 추가하려고 할 때 proxy 패턴을 사용하기 때문에 이러한 형태를 더 깊게 배운다는 것은 불필요한 행동이라고 생각함
