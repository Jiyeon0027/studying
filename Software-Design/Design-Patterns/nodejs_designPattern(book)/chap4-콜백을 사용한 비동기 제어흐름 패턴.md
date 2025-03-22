- 비동기 코드는 구문이 실행되는 순서를 예측하기 어려움
- 비동기 제어흐름을 다루기 위해 기본적으로 콜백을 사용함
- 콜백사용할 때의 가장 흔한 실수는 콜백 지옥에 빠지거나 가독성이 떨어질 수 있음

</br>

# 4-1 비동기 프로그래밍의 어려움

- JavaScript의 비동기 구조에서 콜백의 중첩과 in-place 정의(익명 함수를 바로 만들어 쓰는 방식)가 많아지면 유지보수성과 재사용성이 저하될 수 있다.

- KISS 원칙에 따라 간단하고 빠르게 개발할 수 있지만, 콜백 지옥으로 이어질 가능성이 있다.

- 전문가와 초보자를 가르는 기준은 코드의 구조가 어지럽혀지는 순간을 인지하고, 적절한 규칙과 방법을 미리 마련해둔 뒤 비동기 흐름을 통제할 수 있는지 여부다.

## 간단한 웹 스파이더 애플리케이션

- 입력받은 URL의 콘텐츠를 로컬 파일로 다운로드한다.
- 주요 의존성:
  - [superagent](https://www.npmjs.com/package/superagent): HTTP 요청 라이브러리
  - [mkdirp](https://www.npmjs.com/package/mkdirp): 재귀적으로 디렉터리를 생성해주는 유틸리티
- 유틸성 함수(예: `urlToFilename`)는 `./utils.js`에 구현되어 있다고 가정.
- **코드 구조**
  1. `fs.access`로 이미 다운로드된 파일인지 확인
  2. 다운로드가 필요하면 `superagent.get`을 통해 HTTP 요청
  3. `mkdirp`로 파일이 쓰여질 디렉터리 확보
  4. `fs.writeFile`로 파일 쓰기 후 콜백 처리

```jsx
"use strict";

const request = require("request");
const fs = require("fs");
const mkdirp = require("mkdirp");
const path = require("path");
const utilities = require("./utilities");

function spider(url, callback) {
  const filename = utilities.urlToFilename(url);
  fs.exists(filename, (exists) => {
    //[1] 해당파일이 생성되었는지 확인
    if (!exists) {
      console.log(`Downloading ${url}`);
      request(url, (err, response, body) => {
        //[2] 파일이 없다면 url 다운로드
        if (err) {
          callback(err);
        } else {
          mkdirp(path.dirname(filename), (err) => {
            //[3] 파일을 저장할 디렉터리 확인
            if (err) {
              callback(err);
            } else {
              fs.writeFile(filename, body, (err) => {
                //[4] 응답을 파일에 쓰기
                if (err) {
                  callback(err);
                } else {
                  callback(null, filename, true);
                }
              });
            }
          });
        }
      });
    } else {
      callback(null, filename, false);
    }
  });
}

spider(process.argv[2], (err, filename, downloaded) => {
  if (err) {
    console.log(err);
  } else if (downloaded) {
    console.log(`Completed the download of "${filename}"`);
  } else {
    console.log(`"${filename}" was already downloaded`);
  }
});
```

## # 콜백 지옥

🎲 **콜백 지옥(Callback Hell)의 문제점과 원인**

- **콜백 지옥의 정의**
  - 여러 개의 비동기 함수를 중첩 호출하며, 각 단계마다 콜백을 인라인으로 정의할 때 발생하는 문제.
  - 이런 구조가 깊어질수록 코드가 피라미드 형태로 변형되어 “죽음의 피라미드(pyramid of doom)”라고도 부름.
- **주요 문제점**
  1. **가독성 저하**
     - 깊은 중첩으로 함수의 시작과 끝을 파악하기 어려워짐.
  2. **변수 이름 충돌**
     - 각 스코프마다 유사한 변수를 사용하면서 err, error, err1 등 혼동이 발생.
  3. **메모리 누수 위험**
     - 활성 콜백이 참조하는 컨텍스트 때문에 가비지 컬렉션이 예상대로 동작하지 않을 수 있음.

예시코드

```jsx
asyncFoo((err) => {
  asyncBar((err) => {
    asyncFooBar((err) => {
      // ...
    });
  });
});
```

- 콜백 체인이 계속 중첩되어 스코프가 겹치고, 코드의 모양이 피라미드 형태로 깊어짐.

## 🎲 **정리**

- 콜백 지옥에 빠지면 코드 유지보수가 어려워지고, 디버깅 및 확장 시 장애가 커짐.
- 다음 섹션에서 언급될 다양한 패턴(프로미스, async/await 등)을 사용하면 이러한 문제를 완화할 수 있음.

# 4-2 콜백 모범 사례와 제어 흐름 패턴

## 콜백 지옥이란?

- **중첩된 콜백 함수**들이 여러 단계로 겹쳐지며 코드 가독성이 떨어지는 문제
- **비동기 흐름 제어**가 복잡해져, 코드 유지보수와 디버깅이 어려워짐

## 콜백 규칙

1. **빠른 반환(Early return)**
   - 오류를 만나면 즉시 `return`으로 빠져나오기
   - `if (err) { return cb(err) }` 형태를 사용하여, 불필요한 `else` 중첩을 줄임
2. **익명 함수 남용 지양**
   - 필요하다면 **명명된 함수**로 분리하여 가독성과 재사용성 확보
   - 스택 추적 시 함수 이름이 나타나 디버깅에 유리
3. **코드 모듈화**
   - 작은 단위의 함수로 분할하여 재사용성 강화
   - 각 함수는 **단일 책임**을 갖도록 구성

## 콜백 규칙 적용 예시

### (1) 빠른 반환 적용

```

if (err) {
  return cb(err)
}
// 에러가 없을 때 실행

```

- 불필요한 `else`문을 없애서 **중첩을 줄이고** 로직을 단순화

### (2) 모듈화 예시

**saveFile()**

```
function saveFile(filename, contents, cb) {
  mkdirp(path.dirname(filename), err => {
    if (err) {
      return cb(err)
    }
    fs.writeFile(filename, contents, cb)
  })
}
```

- 파일을 저장하는 로직을 별도 함수로 분리
- `mkdirp`를 통해 디렉터리가 없으면 생성, 그 후 파일에 내용 쓰기

**download()**

```
function download(url, filename, cb) {
  console.log(`Downloading ${url}`)
  superagent.get(url).end((err, res) => {
    if (err) {
      return cb(err)
    }
    saveFile(filename, res.text, err => {
      if (err) {
        return cb(err)
      }
      console.log(`Downloaded and saved: ${url}`)
      cb(null, res.text)
    })
  })
}

- 함수는 기능 한개만 수행한다
- 함수는 500 라인 이하로
- 기능이 복잡한 친구는
  - 이름을 한개만 수행하는 듯 작성
  - 각 스텝별로 서브 함수로 쪼갠다

doTask()
   processNotification()
	     buildList()
	     sendEmail()

```

- URL에서 파일을 다운받은 후 **저장 단계**를 분리하여 관리
- `saveFile()`을 재사용해 코드 중복 최소화

### (3) 최종 spider() 함수 개선

```
export function spider(url, cb) {
  const filename = urlToFilename(url)
  fs.access(filename, err => {
    if (!err || err.code !== 'ENOENT') {
      return cb(null, filename, false)
    }
    download(url, filename, err => {
      if (err) {
        return cb(err)
      }
      cb(null, filename, true)
    })
  })
}

```

- 오류가 없으면(또는 이미 파일이 존재하면) 즉시 반환
- 필요 시 `download()` 함수 호출로 비동기 작업을 처리
- **중첩 수준 감소**와 **재사용성** 확보

### 🎲 정리

- **콜백 지옥** 문제를 해결하기 위해서는 별도의 라이브러리 없이도,
  1. 빠른 반환, 2) 명명된 함수, 3) 모듈화와 같은 **기본 원칙만 잘 적용**해도 충분한 효과를 볼 수 있음
- 이러한 기법을 통해 **코드 유지보수**와 **재사용성**, **테스트 가능성**을 극대화

## 순차 실행

- **순차 실행(Sequential Execution)**한 번에 하나의 작업을 차례대로 실행하는 패턴. 작업 결과가 다음 작업에 영향을 미치는 경우, 순서 보존이 중요.
- **콜백 기반 비동기 순차 실행**순차 실행을 비동기로 구현할 때는 작업이 끝난 후 다음 작업을 호출하는 구조를 사용함.

  ```
  function task1(cb) {
    asyncOperation(() => {
      task2(cb);
    });
  }

  function task2(cb) {
    asyncOperation(() => {
      task3(cb);
    });
  }

  function task3(cb) {
    asyncOperation(() => {
      cb(); // 모든 작업이 끝나면 콜백 실행
    });
  }

  task1(() => {
    console.log('tasks 1, 2 and 3 executed');
  });
  ```

- **순차 반복(Sequential Iteration)**미리 정해진 작업이 아닌, 배열이나 컬렉션의 각 요소에 대해 비동기 작업을 순차적으로 반복해야 할 때 사용.

### 웹 스파이더 예시 코드

- **spiderLinks()**: HTML 페이지에서 링크들을 추출하여, 각 링크를 재귀적으로 순차 다운로드.

  ```
  function spiderLinks(currentUrl, body, nesting, cb) {
    if (nesting === 0) {
      return process.nextTick(cb);
    }
    const links = getPageLinks(currentUrl, body);
    if (links.length === 0) {
      return process.nextTick(cb);
    }

    function iterate(index) {
      if (index === links.length) {
        return cb(); // 모든 링크 처리 완료
      }
      spider(links[index], nesting - 1, function (err) {
        if (err) {
          return cb(err);
        }
        iterate(index + 1);
      });
    }
    iterate(0);
  }

  ```

[`process.nextTick`의 정의](https://www.notion.so/process-nextTick-7b76630c78894953a3b7613e702564e0?pvs=21)

---

### 일반화된 순차 반복 패턴

```
function iterate(index) {
  if (index === tasks.length) {
    return finish();
  }
  const task = tasks[index];
  task(() => iterate(index + 1));
}

function finish() {
  // 모든 반복 완료 후 처리
}

iterate(0);

```

- **용도**
  - 배열을 비동기 매핑할 때
  - 비동기 reduce 구현
  - 특정 조건에서 조기 종료
  - 무한한 요소에 대한 반복
- **헬퍼 함수 형태**

  ```
  iterateSeries(collection, iteratorCallback, finalCallback);

  ```

  - `collection`: 반복할 데이터
  - `iteratorCallback`: 각 아이템에 적용할 비동기 함수
  - `finalCallback`: 모든 아이템 처리 완료 후 실행되는 함수

---

## 🎲 정리

1. **순차 실행**은 각 작업의 결과가 다음에 영향을 줄 때 유용.
2. **콜백 기반 구현**에서는 다음 작업을 명시적으로 호출해야 하므로 “콜백 지옥”이 발생할 수 있음.
3. **순차 반복** 패턴은 배열이나 컬렉션에 대해 작업을 반복 적용할 때 자주 사용.
4. **헬퍼 함수**를 만들어 재사용하면 코드의 복잡도를 낮출 수 있음.

## 병렬 실행

### 1. 비동기 흐름과 병렬(동시) 실행

- **비동기** 작업들이 순차적 실행이 아닌 동시에(또는 겉보기에는 동시에) 시작되어, **모든 작업이 끝났을 때** 알림을 받기 원하는 경우가 있다.
- Node.js는 단일 스레드이지만 **논 블로킹** I/O와 이벤트 루프를 통해 동시성을 달성한다.
- “병렬”이라는 표현은 실제로는 동시에 실행하는 것이 아니라 비동기 방식과 이벤트 루프에 의해 인터리브(interleave)된다는 의미로 이해할 수 있다.

### 2. 간단한 병렬 실행 흐름 패턴

```
const tasks = [ /* ... */ ];
let completed = 0;

tasks.forEach(task => {
  task(() => {
    if (++completed === tasks.length) {
      finish(); // 모든 작업이 완료된 시점
    }
  });
});

function finish() {
  // 모든 작업 완료 후 처리
}

```

- 여러 개의 비동기 작업을 **한 번에** 시작하고, 각 작업의 콜백이 완료될 때 카운트를 증가시킨다.
- 모든 작업의 수와 완료된 작업의 수가 같아지면 `finish()`를 호출한다.

### 3. 웹 스파이더 예시 (버전 3)

- 링크된 페이지를 순차가 아닌 **병렬**로 다운로드하여 전체 속도를 높이는 사례.
- `spiderLinks()` 내부에서 한꺼번에 모든 `spider()` 호출을 시작하고, 각 호출이 끝날 때마다 카운터를 통해 완료 시점을 판단한다.
- 예시 코드:

  ```
  function spiderLinks(currentUrl, body, nesting, cb) {
    if (nesting === 0) {
      return process.nextTick(cb);
    }
    const links = getPageLinks(currentUrl, body);
    if (links.length === 0) {
      return process.nextTick(cb);
    }

    let completed = 0;
    let hasErrors = false;

    function done(err) {
      if (err) {
        hasErrors = true;
        return cb(err);
      }
      if (++completed === links.length && !hasErrors) {
        return cb();
      }
    }

    links.forEach(link => spider(link, nesting - 1, done));
  }

  ```

### 4. 경쟁 상태(race condition)와 해결

- Node.js의 단일 스레드 환경에서도 비동기 작업이 동시에 실행되면 **경쟁 상태**가 발생할 수 있다.
- 예: `spider()` 함수에서 특정 URL을 다운로드하기 전에 파일이 이미 있는지 확인하는 부분에서, 같은 파일을 중복으로 다운로드할 수 있다.
- **해결 방법**: 이미 진행 중인 URL을 기록(예: `Set`)해두어, 같은 URL 작업을 **중복 실행**하지 않도록 한다.

  ```
  const spidering = new Set();

  function spider(url, nesting, cb) {
    if (spidering.has(url)) {
      return process.nextTick(cb);
    }
    spidering.add(url);
    // 이후 다운로드 및 파싱 로직...
  }

  ```

- 경쟁 상태로 인해 중복 다운로드가 일어날 수 있으며, 이를 방지하기 위해 “**상호 배제(Mutual Exclusion)**” 기법을 단순화하여 적용한 사례이다.

### 🎲 정리

1. **Node.js의 병렬 실행**은 실제로는 이벤트 루프가 비동기 콜백을 처리하며 **동시성**을 제공한다.
2. **경쟁 상태**는 단일 스레드 환경에서도 발생할 수 있으므로, 같은 자원(파일 등)에 접근할 때는 충돌을 피하기 위한 관리가 필요하다.
3. **병렬 실행 패턴**을 적절히 활용하고, URL 중복 다운로드 등 경쟁 상태를 제어하면서, 비동기 작업의 장점을 극대화할 수 있다.

</br>

# 제한된 병렬 실행

### 무제한 병렬 작업의 문제점

- **과도한 자원 소모:** 무한정 병렬로 작업(파일 읽기, URL 접근, DB 쿼리 등)을 생성하면 제한된 리소스를 모두 소모하거나, 오픈 가능한 파일 수를 초과할 위험이 발생한다.
- **DoS(Denial-of-Service) 취약성:** 무한히 병렬 작업을 생성하는 서버는 악의적인 사용자의 요청에 쉽게 리소스를 소진해 정상적 응답이 불가해질 수 있다.
- **실행 충돌:** 특정 사이트에 대해 한꺼번에 과도한 요청을 보내면 연결 거부(ECONNREFUSED) 에러가 연달아 발생해 애플리케이션이 중단되거나 재시작이 필요한 상황에 이를 수 있다.

## 제한된 병렬 실행의 개념

- **핵심 아이디어**동시에 실행될 수 있는 작업 수에 ‘상한’을 두어 특정 시점에 병렬로 실행되는 작업의 총량을 제한한다.
- **작동 방식**
  1. **처음**: 동시성 제한 값(concurrency)에 도달하기 전까지 최대한 많은 작업을 할당한다.
  2. **작업 완료 시점**: 작업이 종료될 때마다 새 작업을 이어서 할당하여 동시성 한도를 넘어가지 않도록 조절한다.

## 전역 동시성 제한 vs. 큐(Queue)의 활용

- **전역 동시성 제한**주어진 일련의 작업만 실행한다면 간단히 처리 가능하나, 웹 크롤러처럼 작업 1개가 여러 작업을 재귀적으로 생성하는 경우엔 전역 제한만으론 제어가 복잡해진다.
- **큐(Queue)로 해결**중앙 집중식으로 동시성 제어를 담당하는 큐를 도입하면 새로 생성되는 작업을 큐에 ‘동적으로’ 추가하면서 전체 병렬 작업 수를 안정적으로 관리할 수 있다.

## TaskQueue 클래스 구현

```
export class TaskQueue {
  constructor(concurrency) {
    this.concurrency = concurrency;
    this.running = 0;
    this.queue = [];
  }

  pushTask(task) {
    this.queue.push(task);
    process.nextTick(this.next.bind(this));
    return this;
  }

  next() {
    while (this.running < this.concurrency && this.queue.length) {
      const task = this.queue.shift();
      task((err) => {
        if (err) {
          this.emit('error', err);
        }
        this.running--;
        process.nextTick(this.next.bind(this));
      });
      this.running++;
    }

    if (this.running === 0 && this.queue.length === 0) {
      this.emit('empty');
    }
  }
}

```

- **동작 구조**
  1. `pushTask(task)`: 새 작업을 큐에 넣고 `next()`로 작업을 진행시킨다.
  2. `next()` 내부 루프: `running`(현재 실행 중인 작업)과 `concurrency`(동시 작업 한도)를 비교해 가능한 만큼 작업을 꺼내 실행한다.
  3. 작업 완료 콜백: `running` 감소, 에러 발생 시 `error` 이벤트 전송. 큐가 비면 `empty` 이벤트 전송.

## # 웹 스파이더(크롤러) 적용 예시

### 1. `spiderTask` 함수

```
function spiderTask(url, nesting, queue, cb) {
  const filename = urlToFilename(url);
  fs.readFile(filename, 'utf8', (err, fileContent) => {
    if (err) {
      if (err.code !== 'ENOENT') {
        return cb(err);
      }
      // 파일이 없다면 다운로드
      return download(url, filename, (err, requestContent) => {
        if (err) {
          return cb(err);
        }
        spiderLinks(url, requestContent, nesting, queue);
        return cb();
      });
    }
    // 이미 파일이 있으면 바로 링크 탐색
    spiderLinks(url, fileContent, nesting, queue);
    return cb();
  });
}

```

- 로컬에 파일이 없으면 URL에서 다운로드
- 파일이 있으면 즉시 링크 파싱 후 다음 작업(링크 다운로드)을 큐에 등록

### 2. `spiderLinks` 함수

```
function spiderLinks(currentUrl, body, nesting, queue) {
  if (nesting === 0) {
    return;
  }
  const links = getPageLinks(currentUrl, body);
  if (links.length === 0) {
    return;
  }
  links.forEach(link => spider(link, nesting - 1, queue));
}

```

- 현재 페이지에서 발견된 링크를 순회하여 `spider` 함수를 이용해 큐에 작업을 추가

### 3. `spider` 함수

```
const spidering = new Set();

export function spider(url, nesting, queue) {
  if (spidering.has(url)) {
    return;
  }
  spidering.add(url);

  queue.pushTask((done) => {
    spiderTask(url, nesting, queue, done);
  });
}

```

- 이미 진행 중이거나 완료된 URL은 `spidering` 집합에 기록해 중복 요청 방지
- `pushTask`로 작업 등록 시 `spiderTask`가 실제 크롤링 로직을 수행

### 4. 실행 스크립트(`spider-cli.js`)

```
import { spider } from './spider.js';
import { TaskQueue } from './TaskQueue.js';

const url = process.argv[2];
const nesting = Number.parseInt(process.argv[3], 10) || 1;
const concurrency = Number.parseInt(process.argv[4], 10) || 2;

const spiderQueue = new TaskQueue(concurrency);
spiderQueue.on('error', console.error);
spiderQueue.on('empty', () => console.log('Download complete'));

spider(url, nesting, spiderQueue);

```

- CLI 파라미터로 `URL`, `nesting`, `concurrency(동시성)`을 입력받아 큐와 크롤러 초기화
- `empty` 이벤트가 발생하면 모든 다운로드가 완료됨을 알림

### 🎲 정리

- **병렬 작업에 적절한 동시성 제한을 두면** 서버 과부하나 DoS 공격에 대한 취약성을 크게 줄일 수 있다.
- **큐를 이용한 TaskQueue 패턴**은 유연하고 직관적으로 전역 동시성 한도를 관리해준다.
- **웹 스파이더 예시**를 통해 큐 기반 동시성 제어가 대규모 크롤링 작업에서도 안정적 동작을 제공하는 방식을 확인할 수 있다.
