## 콜백 패턴

비동기 코드를 작성하기 위해 어떻게 콜백 메커니즘을 이해해야 하는지

- 비동기 작업을 처리할 때 필요한 '작업의 결과를 전달하기 위해 호출되는 함수'
- 비동기 세계에서 콜백은 return 명령을 대신함
- JS는 콜백에 이상적인 언어로, 함수가 일급 클래스 객체이면서, 변수에 할당, 인자로 전달, 다른 함수호출에서 반화되고, 자료구조에 저장되는 언어이기 대문
- 클로저(closure)를 통해 생성된 함수환경 구현

### 연속전달방식(CPS: Continuation-Passsing Style)

- 콜백을 다른함수에 인자로 전달하는 방식 → 호출자에게 결과를 다른함수(콜백)로 전달

```tsx
//Dircet style
fucntion add(a,b) {
	return a+b
}

//CPS (동기식 연속전달 방식)
fuction addCps(a, b, callback) {
	callback(a + b)
}

//비동기 연속 전달 방식
function additionAsync(a, b, callback) {
	setTimeout(() => callback(a + b), 100)
}

console.log('before')
additionAsync(1, 2, result => console.log('result: ${result}'))
console.log('after')
/*
결과
before
after
result: 3
*/
```

1. before
2. setTimeout() → 제어는 다음으로 넘어감(비동기 실행중)
3. after
4. callback함수 진행(result:3)

→ 즉 동기함수는 조작을 완료할때 까지 블로킹, 비동기함수는 제어를 즉시 반환함

위의 코드에서 Javascript의 클로저 덕분에 콜백이 다른 시점과 다른 위치에서 호출되더라도, 비동기 함수의 호출자 컨텍스트를 유지한다. 따라서, additionAsync() 함수가 종료되었음에도 이벤트 루프의 다음 사이클에서 콜백함수가 수행될 때, 변수값을 유지한 상태로 결과값이 출력된다.
※ 클로저(Closer)란, 내부 함수가 참조하는 외부함수의 지역변수가 외부함수가 리턴된 이후에도 유효성이 유지될 때, 이 내부함수를 클로저라고 한다

- 비연속 전달(Non-CPS)콜백
  단순 배열 접근을 위한 map 함수의 경우 요소를 반복하는데 사용될 뿐, 비동기적으로 연산 결과를 전달하지 않기 때문에 결과는 직접적인 방식으로 동기적으로 반환
  ```tsx
  const result = [1, 5, 7].map((element) => element - 1);
  console.log(result); // [0, 4, 6]
  ```

### 동기? 비동기?

- 예측할수 없는 함수를 만들지 말것

```tsx
import { readFile } from "fs";

const cache = new Map();

function inconsistentRead(filename, cb) {
  if (cache.has(filename)) {
    //동기적으로 호출
    cb(cache.get(filename));
  } else {
    //비동기 함수 내에서 콜백 사용
    readFile(Filename, "utf8", (err, data) => {
      cache.set(filename, data);
      cb(data);
    });
  }
}
```

- 왜 이렇게 동기와 비동기를 섞어쓰면 안되는가?

```tsx
function createFileReader(filename) {
  const listeners = [];
  inconsistentRead(filename, (value) => {
    listeners.forEach((listener) => listener(value));
  });

  return {
    onDataReady: (listener) => listenenrs.push(listener),
  };
}

const reader1 = createFileReader("data.txt"); //비동기 수행 ->리스너를 등록하는데 충분한 시간
reader1.onDataReady((data) => {
  console.log("First call data : ${data}");

  //일정 시간 후 같은 파일 다시 읽기 시도
  const reader2 = createFileReader("data.txt");
  //동기수행 -> 이미 캐시가 존재하여 모든 리스너가 호출되지만 reader2의 생성후 등록하여 호출불가
  reader2.onDataReady((data) => {
    console.log("Second call data : ${data}");
  });
});
```

→ 함수가 실행이 예측 불가능 하게됨 :

1. 동기적 I/O로 변경하는 해결책을 사용할 수 있음

   단점: 동기식 API를 항상 사용은 불가 , 동시성 모델을 깨트려 애플리케이션 속도를 늦춤

2. 지연실행(deferred execution)으로 비동시성을 보장

   즉시 실행되지 않고 가까운 미래에 실행되도록 예약 ex. process.nextTick()을 사용

   ```tsx
   function consistentReadAsync(filename, callback) {
     if (cache.has(file)) {
       //지연된 콜백 호출
       process.nextTick(() => callback(cache.get(filename)));
     } else {
       //비동기 함수 사용
       readFile(Filename, "utf8", (err, data) => {
         cache.set(filename, data);
         cb(data);
       });
     }
   }
   ```

   - process.nextTick() : 현재 진행중인 작업의 완료 시점 뒤로 함수의 실행을 지연시킴.

   ※  process.nextTick() vs  setImmediate() vs setTimeout(callback,0)

   1. process.nextTick()은 현재 작업이 완료 된 후 바로 실행되어 다른 I/O 이벤트가 발생하기 전 실행됨
      (마이크로 테스크: 콜백을 인수로 받아 대기중인 I/O 이벤트 대기열의 앞으로 밀어넣고 즉시 반환)
      따라서 특정 I/O가 계속 수행되지 않는 기아 상태에 빠질 수 있다.
   2. setImmediate()은 이미 큐에 있는 I/O 이벤트들의 뒤에 넣어 대기하는 형태로 실행.
   3. setTimeout(callback,0)은 setImmediate()와 비슷하나 이벤트 루프의 다른 Phase에서 실행된다. setTimeout은 Timer에서, setImmediate는 check에서 실행되기 때문에, I/O 콜백과 연관되어 수행된다면 setImmediate()로 예약된 콜백이 먼저 수행된다.

### Node.js 콜백규칙

- 콜백은 맨 마지막 인자로!
- 오류는 맨 처음에
  - 콜백함수에 오류를 인자로 전달해야되는 경우, 콜백의 첫번째 인자로 전달한다.또한 오류는 항상 Error 타입으로 전달한다(간단한 문자열이나 숫자를 오류 객체로 전달하지 말 것)
  ```tsx
  readfile("foo.txt", "utf-8", (err, data) => {
    if (err) {
      handleError(err);
    } else {
      processData(data);
    }
  }); //이때 에러가 없으면 err 첫번째 인자는 null 혹은 undefined
  ```
- 오류 전파
  - throw 문을 사용하여 수행 오류가 catch될때 까지 호출 스택에서 실행
  - 비동기식 CPS 에서 적정한 에러 전파는 오류를 호출 체인의 다음에서 콜백으로 전달하여 수행
- 캐치되지 않는 예외
  - 콜백에서 에러 발생 시 콜백을 수행시키는 함수의 에러로 감지되지 않는다.
    ```tsx
    function readJSON(filename, callback) {
      readFile(filename, "utf8", (err, data) => {
        if (err) {
          //에러를 전파하고 현재의 함수에서 빠져 나옴
          return callback(err);
        }
        try {
          //파일 내용 파싱
          parsed = JSON.parse(data);
        } catch (err) {
          //파싱 에러 캐치
          return callback(err);
        }
        //에러없음. 데이터 전파
        callbcak(null, parsed);
      });
    }
    ```
    ```tsx
    function readJSON(filename, callback) {
      readFile(filename, "utf8", (err, data) => {
        if (err) {
          //에러를 전파하고 현재의 함수에서 빠져 나옴
          return callback(err);
        }
        //에러없음. 데이터 전파
        callbcak(null, JSON.parse(data));
      });
    }
    ```
    → 이런경우 예외가 콜백에서 스택으로 이동후 이벤트 루프로 이동하여 마지막으로 콘솔에서 포착됨
    - 동작하는 스택과 콜백이 호출된 스택이 달라 안티패턴을 일으키므로 uncaughtException 라는 특수 이벤트를 내보내 프로세스 종료 (fail-fast)

## 관찰자 패턴

Event Emitter 클래스에 의해서 구현되는 패턴으로 다양한 다중이벤트를 다루기 위해 콜백 사용

- 리액터 그리고 콜백과 함께 비동기적인 node.js 를 숙달하는데 필수적
- 콜백 패턴과의 파이점: 전통적인 CPS 는 오직 하나의 리스너에게 결과 전달, 관찰자 패턴은 여러 관찰자에게 통지 가능

### EventEmitter Class

- events 코어 모듈로부터 exports 됨
- 필수 메소드
  1.  on(event, listenr) : 주어진 이벤트 문자열에 대해 새로운 리스너(함수)를 등록
  2.  once(event, listener) : 첫 이벤트가 전달된 후 제거되는 1회성 리스너 등록
  3.  emit(event, [arg1], [...]) : 새 이벤트를 생성하고 리스너에게 전달할 추가적인 문자열(인자)를 제공4)
  4.  removeListenr(event, listenr) : 지정된 이벤트 문자열에 대한 리스너를 제거

### 오류 전파

- EventEmiiter는에러가 발생했을 때, 콜백처럼 예외를 throw 하는 방식이 아니라 error라는 특수한 이벤트를 발생시키고, Error 객체를 인자로 전달하는 방식
- 이때 오류 이벤트에 관련된 리스너가 없을 경우 자동으로 예외를 Throw하고 애플리케이션 종료되므로 오류 리스너를 항상 등록해주는 것이 권장

### 관찰 가능한 객체 만들기

- 다른 클래스의 확장으로 구성됨 (EventEmitter 클래스를 상속받음)
- constructor내부에서 super 사용.

### EventEmitter 와 메모리 누수

- 메모리 누수를 예방하기 위해 `구독 해지` 하는 것이 매우 중요함.
  `emitter.removeListener('an_event', listener)`
- 리스너에거 계속 참조되므로 메모리에서 유지됨(도달가능한 상태 까지)
- emitter 자체에 대한 참조가 더이상 활성되어 있지 않아 도달할 수 없게 되는 경우에만 가비지 컬렉션에 잡혀 메모리 점유를 해지.
  즉, 코드를 잘못 작성하여 해제되지 않는 영구적인 EventEmiiter를 등록한다면 메모리 누수를 일으키게 되니 주의해야 한다(ex. once 메소드 사용하였는데, 이벤트가 한번도 발생하지 않는 경우)
  도

### 동기 및 비동기 이벤트

EventEmitter는 기본적으로 비동기적 이벤트를 다루는데 사용
이벤트를 동기적으로 발생시키는 것은 EventEmitter가 필요하지 않거나,  Zalgo의 상황(동기와 비동기 이벤트를 혼합하여 사용하는 것)이다. → 동기와 비동기를 섞어서 사용하지 말 것

```tsx
// 파일에서 특정 단어를 찾으면 이벤트를 발생시키는 경우
// find()함수에서 readFile(비동기) 사용시 found1, found2 둘다 감지되나,
// readFileSync(동기) 사용 시 found1만 감지됨
findRegexInstance
   .addFile(...)
   .on('found1', (file,match) => console.log('match found1'))
   .find()
   .on('found2', (file,match) => console.log('match found2'))
```

- 이벤트가 비동기적으로 발생할 때, 현재의 스택이 이벤트 루프에 넘어갈 때 까지는 이벤트가 발생한 이후에도 새로운 리스너를 등록할 수 있다.
  즉, 이벤트가 이벤트 루프 다음 사이클이 될 때까지 날라가지 않는것이 보장된다. 따라서 어떠한 이벤트도 놓치지 않게 된다.
- 이벤트가 특정 작업에서 동기적으로 발생한다면, 모든 리스너를 이벤트 발생 전에 등록해야 한다. (ex. 파일을 동기적으로 읽는 메소드 readFileSync() 을 사용하는 경우)

**3-2-7 EventEmitter vs 콜백**

기능을 동일하게 동작시킬 수는 있음

```jsx
import { EventEmitter } from "events";

function helloEvents() {
  const eventEmitter = new EventEmitter();
  setTimeout(() => eventEmitter.emit("complete", "hello world"), 100);
  return eventEmitter;
}

function helloCallback(cb) {
  setTimeout(() => cb(null, "hello workd"), 100);
}

helloEvents().on("complete", (message) => console.log(message));
helloCallback((err, message) => console.log(message));
```

어떤 스타일을 선택할지에 대한 규칙은 없지만 결정을 내리는데 도움될 힌트.

- 가독성 측면 : 콜백은 여러 유형의 결과를 전달하기 어렵기 떄문에, 여러 이벤트를 전달해야되는 경우 EventEmitter를 사용하면 코드가 깔끔하게 작성 가능하다.
- 의미 측면 : EventEmitter는 같은 이벤트가 여러번 발생하거나, 발생하지 않을 수도 있는 경우 사용되어야 한다.
  콜백은 작업이 성공/실패 여부와 상관없이 정확히 한번 호출되기 때문에, 반복 가능성이 있거나 발생하지 않을수도 있는 경우는 EventEmitter를 사용하는것이 좋다.
- 구현 측면 : 콜백을 사용하는 API는 오직 특정한 콜백 하나만 사용할 수 있고,EventEmitter는 같은 이벤트에 대해 다수의 리스너를 등록할 수 있다.

### 콜백과 EventEmitter의 결합

- glob 패키지(https://www.npmjs.com/package/glob) : 콜백을 사용하여 결과를 비동기적으로 전달하고, 동시에 EventEmitter를 반환하여 비동기 처리 상태에 대해 상세한 판단을 제공.
- 주어진 패턴과 일치하는 모든 파일 리스트를 가지고 호출된 콜백 함수를 가져온다. 프로세스 상태에 대해서 보다 세분화된 알림을 제공하는 EventEmitter 사용.
  `const eventEmitter = glob(pattern, [option], callback)`
