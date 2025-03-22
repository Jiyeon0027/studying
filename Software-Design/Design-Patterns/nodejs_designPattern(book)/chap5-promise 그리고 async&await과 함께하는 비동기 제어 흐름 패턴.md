## 콜백의 문제점

- 콜백 지옥 발생
- 오류 관리 취약

→ **Promise, async/await** 등장

## 프라미스(Promise)

- 비동기식 작업의 최종 결과를 담고 있는 객체

1. 결과값이 아직 정해지지 않은 상태 = 대기중(pending)
2. 성공적으로 완료되어 결과 값이 반환된 상태 = 이행됨(fulfilled)
3. 작업이 실패하거나 에러가 발생한 상태 = 거부됨(rejected)
4. 작업이 완료되었으며, 결과가 성공 또는 실패로 확정된 상태 = 결정된(settled)

```jsx
// 콜백 코드
asyncOperation(10, (err, result) => {
  if (err) {
    console.log(err);
  } else {
    console.log(result);
  }
});
```

```jsx
// 프라미스 코드
asyncOperation(10)
  .then((result) => {
    console.log(result);
  })
  .catch((err) => {
    console.log(err);
  });
```

## 프라미스 체인(Promise)

- 각 단계에서 비동기 작업이 완료될 때 다음 단계로 결과가 전달
- **비동기 작업을 순차적으로 연결**하여 실행 흐름을 명확하게 관리

## 프라미스 생성

```jsx
// 지정된 밀리초 후에 현재의 시간을 이행하는 프라미스를 반환

function delay(milliseconds) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve(new Date());
    }, milliseconds);
  });
}

console.log(`Delaying...${new Date().getSeconds()}s`);
delay(1000).then((newDate) => {
  console.log(`Done ${newDate.getSeconds()}s`);
});
```

- then() 핸들러 안의 console.log() 는 delay() 호출에서부터 대략 1초 뒤에 실행

## 프라미스화

- 콜백 기반함수를 프라미스를 반환하는 동일한 함수로 변환

```jsx
function promisify(callbackBasedApi) {
  return function promisified(...args) {
    // (promisified 함수 반환)
    return new Promise((resolve, reject) => {
      // 프라미스 생성
      const newArgs = [
        ...args, // 기존 인자 유지
        function (err, result) {
          // 특별한 콜백 추가
          if (err) {
            return reject(err); // 에러 발생 시 프라미스 거부
          }
          resolve(result); // 성공 시 프라미스 이행
        },
      ];
      callbackBasedApi(...newArgs); // 원래 API 호출
    });
  };
}
```

```jsx
// 콜백 방식
setTimeout((err) => {
  if (err) console.error(err); // 에러 처리
  console.log("작업 완료");
}, 1000); // 1초 뒤 실행

// 프라미스화
const promisifiedSetTimeout = promisify(setTimeout);

promisifiedSetTimeout(1000)
  .then(() => {
    console.log("작업 완료"); // 1초 뒤 실행
  })
  .catch((err) => {
    console.error(err); // 에러 처리
  });
```

## spider.js 변경

- 웹 URL을 입력으로 받아 해당 URL의 내용을 로컬 파일로 다운로드

```jsx
// 콜백 방식
function download(url, filename, cb) {
  console.log(`Downloading ${url}`);
  superagent.get(url).end((err, res) => {
    if (err) {
      // 매 단계에서 명시적으로 에러 확인 후 처리
      return cb(err);
    }
    saveFile(filename, res.text, (err) => {
      // superagent.get의 결과로 다시 saveFile 호출
      if (err) {
        // 매 단계에서 명시적으로 에러 확인 후 처리
        return cb(err);
      }
      console.log(`Downloaded and saved: ${url}`);
      cb(null, res.text); // 최종적으로 cb 호출
    });
  });
}

// 프라미스 방식
const mkdirpPromises = promisify(mkdirp);

function download(url, filename) {
  console.log(`Downloading ${url}`);
  let content;
  return superagent
    .get(url)
    .then((res) => {
      content = res.text;
      return mkdirpPromises(dirname(filename));
    })
    .then(() => fsPromises.writeFile(filename, content))
    .then(() => {
      console.log(`Downloaded and saved: ${url}`);
      return content;
    })
    .catch((err) => {
      console.error(`Failed to download ${url}:`, err);
      throw err;
    });
}
```

- 콜백 지옥을 피하고 논리 흐름이 명확
- `.catch`를 사용해 한 번에 에러를 처리

```jsx
// 프라미스 방식
function spiderLinks(currentUrl, content, nesting) {
  let promise = Promise.resolve();
  if (nesting === 0) {
    return promise;
  }
  const links = getPageLinks(currentUrl, content);
  for (const link of links) {
    promise = promise.then(() => spider(link, nesting - 1));
  }
  return promise;
}
```

- `links` 배열의 각 링크를 차례대로 처리
- 현재 링크에 대해 작업이 끝난 후에 다음 링크를 처리하도록 비동기 작업을 순차적으로 연결
- 모든 링크를 순서대로 처리한 후 최종 결과를 반환

```jsx
// 콜백 방식
export function spider(url, nesting, cb) {
  const filename = urlToFilename(url);
  fs.readFile(filename, "utf8", (err, fileContent) => {
    if (err) {
      // 매 단계에서 명시적으로 에러 확인 후 처리
      if (err.code !== "ENOENT") {
        return cb(err);
      }
      return download(url, filename, (err, requestContent) => {
        if (err) {
          // 매 단계에서 명시적으로 에러 확인 후 처리
          return cb(err);
        }
        spiderLinks(url, requestContent, nesting, cb);
      });
    }
    spiderLinks(url, fileContent, nesting, cb);
  });
}

// 프라미스 방식
export function spider(url, nesting) {
  const filename = urlToFilename(url);
  return fsPromises
    .readFile(filename, "utf8")
    .catch((err) => {
      // catch를 사용해 에러를 처리
      if (err.code !== "ENOENT") {
        throw err;
      }
      return download(url, filename);
    })
    .then((content) => spiderLinks(url, content, nesting));
}
```

- 콜백을 사용할 때 사용자가 직접 수행해야 했던 오류 전파를 하기 위한 로직 제거

## 병렬 실행

```tsx
// 순차적 방식
function spiderLinks(currentUrl, content, nesting) {
  let promise = Promise.resolve();
  if (nesting === 0) {
    return promise;
  }
  const links = getPageLinks(currentUrl, content);
  for (const link of links) {
    promise = promise.then(() => spider(link, nesting - 1));
  }
  return promise;
}

// 병렬적 방식
function spiderLinks(currentUrl, content, nesting) {
  if (nesting === 0) {
    return Promise.resolve();
  }
  const links = getPageLinks(currentUrl, content);
  const promises = links.map((link) => spider(link, nesting - 1));
  return Promise.all(promises);
}
```

| **특징**             | **순차적 방식**                               | **병렬적 방식**                                     |
| -------------------- | --------------------------------------------- | --------------------------------------------------- |
| **실행 방식**        | 한 번에 한 작업씩 처리                        | 모든 작업을 동시에 실행                             |
| **비동기 처리 순서** | 이전 작업이 완료된 후 다음 작업 실행          | 모든 작업이 동시에 시작됨                           |
| **속도**             | 느림 (작업이 많아질수록 지연 시간이 누적됨)   | 빠름 (모든 작업이 병렬로 실행됨)                    |
| **코드 구조**        | `for...of`와 `promise.then` 사용              | `map`과 `Promise.all` 사용                          |
| **사용 사례**        | 각 작업이 **순차적으로 실행**되어야 하는 경우 | 작업 간에 **의존성이 없는 병렬 처리**가 가능한 경우 |

- 순차적 방식
  - 이전 작업(`promise.then(...)`)이 완료될 때까지 기다리므로, 각 작업이 차례로 실행
- 병렬적 방식
  - 동시에 spider()를 호출하여 반환된 각 프라미스는 최종적으로 promises 배열에 수집
  - `Promise.all`을 사용하여 **모든 비동기 작업을 병렬로 실행**
  - 모든 작업이 병렬로 시작되며, 모든 작업이 완료되었을 때 최종적으로 이행
  - 배열 중 하나라도 거부되면 즉시 거부

## Async/await

- 콜백 지옥보다는 낫지만 여전히 then() 호출

```tsx
async function playingWithDelays() {
  console.log("Delaying...", new Date());
  const dateAfterOneSecond = await delay(1000);
  console.log(dateAfterOneSecond);
  const dateAfterThreeSeconds = await delay(3000);
  console.log(dateAfterThreeSeconds);
  return "done";
}

playingWithDelays().then((result) => {
  console.log(`After 4 seconds: ${result}`);
});

// example
// Delaying... 2025-01-13T12:00:00.000Z
// 2025-01-13T12:00:01.000Z
// 2025-01-13T12:00:04.000Z
// After 4 seconds: done
```

- `async/await` 는 동기 코드처럼 읽기 쉽고 가독성이 높은 코드를 작성

## try-catch

```tsx
function delayError(milliseconds) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      reject(new Error(`Error after ${milliseconds}ms`));
    }, milliseconds);
  });
}

async function playingWithErrors(throwSyncError) {
  try {
    if (throwSyncError) {
      throw new Error("This is a synchronous error");
    }
    await delayError(1000);
  } catch (err) {
    console.error(`We have an error: ${err.message}`);
  } finally {
    console.log("Done");
  }
}

playingWithErrors(true);
//  We have an error: This is a synchronous error
//  Done

playingWithErrors(false);
//  We have an error: Error after 1000ms
//  Done
```

- 동기적 에러(`throw new Error(...)`)는 `try`-`catch`로 간단히 처리 가능
- 비동기 함수에서 발생한 에러(`Promise.reject`)는 `await`와 `try-catch`를 사용해 동일한 방식으로 처리 가능
- `finally` 는 에러 발생 여부와 상관없이 항상 실행
- 동기와 비동기 에러 처리의 일관된 접근

## spider.js 변경

```jsx
// 프라미스 방식
const mkdirpPromises = promisify(mkdirp);

function download(url, filename) {
  console.log(`Downloading ${url}`);
  let content;
  return superagent
    .get(url)
    .then((res) => {
      content = res.text;
      return mkdirpPromises(dirname(filename));
    })
    .then(() => fsPromises.writeFile(filename, content))
    .then(() => {
      console.log(`Downloaded and saved: ${url}`);
      return content;
    });
}

// await 방식
async function download(url, filename) {
  console.log(`Downloading ${url}`);
  const { text: content } = await superagent.get(url);
  await mkdirpPromises(dirname(filename));
  await fsPromises.writeFile(filename, content);
  console.log(`Downloaded and saved: ${url}`);
  return content;
}
```

- 얼마나 간단하고 간결해졌는지 잠시 살펴봅시다…

```jsx
// 프라미스 방식
function spiderLinks(currentUrl, content, nesting) {
  let promise = Promise.resolve();
  if (nesting === 0) {
    return promise;
  }
  const links = getPageLinks(currentUrl, content);
  for (const link of links) {
    promise = promise.then(() => spider(link, nesting - 1));
  }
  return promise;
}

// await 방식
async function spiderLinks(currentUrl, content, nesting) {
  if (nesting === 0) {
    return;
  }
  const links = getPageLinks(currentUrl, content);
  for (const link of links) {
    await spider(link, nesting - 1);
  }
}
```

- 간단한 반복이 존재하고 각 항목에 대해 spider()가 반환하는 프라미스를 기다림

```jsx
// 프라미스 방식
export function spider(url, nesting) {
  const filename = urlToFilename(url);
  return fsPromises
    .readFile(filename, "utf8")
    .catch((err) => {
      if (err.code !== "ENOENT") {
        throw err;
      }
      return download(url, filename);
    })
    .then((content) => spiderLinks(url, content, nesting));
}

// await 방식
export async function spider(url, nesting) {
  const filename = urlToFilename(url);
  let content;
  try {
    content = await fsPromises.readFile(filename, "utf8");
  } catch (err) {
    if (err.code !== "ENOENT") {
      throw err;
    }
    content = await download(url, filename);
  }
  return spiderLinks(url, content, nesting);
}
```

- try-catch문으로 에러를 간단하게 다룸

## 안티 패턴 (forEach + async/await)

```jsx
// for ... of
async function spiderLinks(currentUrl, content, nesting) {
    if (nesting === 0) {
        return;
    }
    const links = getPageLinks(currentUrl, content);
    for (const link of links) {
        await spider(link, nesting - 1);
}

// forEach
async function spiderLinks(currentUrl, content, nesting) {
    if (nesting === 0) {
        return;
    }
    const links = getPageLinks(currentUrl, content);
    links.forEach(async function(link) {
        await spider(link, nesting - 1);
    });
}
```

- for … of
  - `for...of`는 `await`와 함께 사용될 때 비동기 작업을 하나씩 순차적으로 기다려가며 실행
  - 순차적 실행을 보장
- forEach (★비권장)
  - `forEach`는 동기적으로 반복을 진행하며, `async` 함수 내에서 반환된 프라미스를 **기다리지 않기 때문에** 병렬로 실행
  - `forEach` 자체가 비동기 작업을 기다리지 않으므로, 원하는 대로 순차적 실행 불가

```jsx
async function processLinksWithMap(links) {
  const promises = links.map((link) => someAsyncFunction(link)); // 병렬 실행
  await Promise.all(promises); // 모든 비동기 작업이 끝날 때까지 기다림
}

async function processLinksWithForEach(links) {
  links.forEach((link) => someAsyncFunction(link)); // 병렬 실행되지만 Promise.all()을 사용하지 않음
}
```

- `map`은 각 반복에서 `Promise`를 반환하므로, 이를 모아서 병렬적으로 처리하고 결과를 기다리기 위해 `Promise.all`을 사용
- `forEach`는 각 반복에서 실행되는 함수의 결과를 반환하지 않기 때문에, 병렬 처리 결과를 모은 후 기다리는 방식이 불가능

## 병렬 실행

1. await 표현식 사용
2. Promise.all()에 의존 (★권장)

   ```jsx
   // await 표현식
   async function spiderLinks(currentUrl, content, nesting) {
     if (nesting === 0) {
       return;
     }
     const links = getPageLinks(currentUrl, content);
     const promises = links.map((link) => spider(link, nesting - 1));
     const results = await Promise.all(promises);
     return results;
   }
   ```

   - `await`를 사용하여 `Promise.all(promises)`의 결과를 기다리고, 그 결과를 `results`에 저장한 후 반환
   - `results`를 반환하기 전에 모든 `promises`가 완료될 때까지 이 함수 내부에서 대기

   ```jsx
   // Promise.all
   async function spiderLinks(currentUrl, content, nesting) {
     if (nesting === 0) {
       return;
     }
     const links = getPageLinks(currentUrl, content);
     const promises = links.map((link) => spider(link, nesting - 1));
     return Promise.all(promises);
   }
   ```

   - 모든 `promises`가 완료되길 기다리는 Promise 객체를 반환
   - 호출자가 Promise를 기다도록 만들어 더 깔끔한 코드 (★권장)
     - 함수 내부에서 대기하지 않고, 호출자에게 결과를 기다릴 책임을 넘기므로 함수가 더 단순
     - 호출자가 Promise를 기다릴지, 바로 처리할지 결정 가능(즉시 대기 / await, 나중에 처리 / then)
     - 비동기 관점에서 Promise를 반환하는 함수는 일관성 유지

## 무한 재귀 프라미스 해결 체인

### 메모리 누수 발생 코드

```jsx
// 무한 동작 정의
function leakingLoop() {
  return delay(1).then(() => {
    console.log(`Tick ${Date.now()}`);
    return leakingLoop();
  });
}
```

- 프라미스 체인이 끊어지지 않고 계속 연결
- 각 `leakingLoop()` 호출은 새로운 프라미스를 반환하고, 그 프라미스는 이전에 실행된 `leakingLoop()`의 프라미스와 연결
- 프라미스가 해결되지 않고 계속 연결되어 메모리 누수가 발생

### 해결 방법 1: 프라미스 체인 끊기

```jsx
function nonLeakingLoop() {
  delay(1).then(() => {
    console.log(`Tick ${Date.now()}`);
    nonLeakingLoop();
  });
}
```

- return을 사용하지 않아 반환되는 프라미스 체인이 끊김
- 각각의 프라미스는 다른 프라미스와 연결되지 않고 독립적으로 실행
- 하지만 에러 전파의 어려움

### 해결 방법 2: 프라미스 내부에서 에러 처리

```jsx
function nonLeakingLoopWithErrors() {
  return new Promise((resolve, reject) => {
    (function internalLoop() {
      delay(1)
        .then(() => {
          console.log(`Tick ${Date.now()}`);
          internalLoop(); // 재귀 호출
        })
        .catch((err) => {
          reject(err); // 에러 발생 시 reject
        });
    })();
  });
}
```

- 프라미스 생성자 안에 재귀 함수를 감싸기
- 에러가 발생하면 프라미스 거부되도록 처리
- 재귀 중 에러 발생 시 catch에서 처리 후 바로 reject()
- 에러 발생 시 모든 프라미스 간의 연결이 끊어져 메모리 누수 문제 해결

### 해결 방법 3: async/await 사용

```jsx
async function nonLeakingLoopAsync() {
  while (true) {
    await delay(1);
    console.log(`Tick ${Date.now()}`);
  }
}
```

- `await`를 사용하여 비동기 작업(`delay(1)`)이 완료될 때까지 기다린 후, 계속해서 반복
- 동기처럼 처리할 수 있으며 간결하게 해결 가능

## 요약

- 프라미스와 async/await는 깔끔한 코드와 직관적인 오류 관리 제공
- 비동기 작업을 병렬로 실행할 땐 Promise.all()
- 메모리 누수를 해결하기 위해서는
  - 프라미스 체인 끊기 (return 사용X)
  - try-catch블록으로 reject하여 에러 처리
  - await으로 비동기 작업이 끝날 때까지 대기
