### 스트림의 중요성 발견

이벤트 기반 플랫폼에서 I/O를 처리하는 가장 효율적인 방법 : 실시간으로 입력을 사용학 출력을 내보내는것

## 6-1. 버퍼링 대 스트리밍

- 버퍼 : 작업이 완료될때까지 데이터를 버퍼에 수집
- 스트림: 처리할수 있는 소비자에게 즉시 전달(공간과 시간측면에서 효율적)

  - 결합성 : 인터페이스와의 결합성

  ```jsx
  import { createReadStream, createWriteStream } from 'fs' import { createGzip } from 'zlib'
  const filename = process.argv[2]

  createReadStream(filename)
  .pipe(createGzip())
  .pipe(createWriteStream(`${filename}.gz`))
  .on('finish', () => console.log('File successfully compressed'))

  ```

  - 공간 효율성: 커다란 파일을 읽어야할때 쉽게 메모리가 부족해질 수 있음
  - 시간 효율성: 버퍼를 사용할 경우 전체파일을 읽고 압축한 경우에만 업로드가 시작, 하지만 스트림을 이용한 경우 파일시스템에서 읽은 즉시 데이터 청크를 압축하고 전송 가능
  - 스트림을 사용하면 전체파일을 기다리지 않고 첫번째 데이터 청크를 전송하자마자 조립이 시작됨, 이는 각 작업이 병렬적으로 비동기적 실행이 되기 때문에 효율적 시간을 쓸 수 있음

  ```jsx
  //gzip-receive.js
  import { createServer } from "http";
  import { createWriteStream } from "fs";
  import { createGunzip } from "zlib";
  import { basename, join } from "path";

  const server = createServer((req, res) => {
    const filename = basename(req.headers["x-filename"]);
    const destFilename = join("received_files", filename);
    console.log(`File request received: ${filename}`);
    req
      .pipe(createGunzip())
      .pipe(createWriteStream(destFilename))
      .on("finish", () => {
        res.writeHead(201, { "Content-Type": "text/plain" });
        res.end("OK\n");
        console.log(`File saved: ${destFilename}`);
      });
  });

  server.listen(3000, () => console.log("Listening on http://localhost:3000"));
  ```

  ```jsx
  //gzip-send.js
  import { request } from "http";
  import { createGzip } from "zlib";
  import { createReadStream } from "fs";
  import { basename } from "path";

  const filename = process.argv[2];
  const serverHost = process.argv[3];

  const httpRequestOptions = {
    hostname: serverHost,
    port: 3000,
    path: "/",
    method: "PUT",
    headers: {
      "Content-Type": "application/octet-stream",
      "Content-Encoding": "gzip",
      "X-Filename": basename(filename),
    },
  };

  const req = request(httpRequestOptions, (res) => {
    console.log(`Server response: ${res.statusCode}`);
  });

  createReadStream(filename)
    .pipe(createGzip())
    .pipe(req)
    .on("finish", () => {
      console.log("File successfully sent");
    });
  ```

- 조립성
  - Node.js의 pipe() 함수를 통해 여러 스트림을 연결할 수 있음
  - 각 스트림은 단일 기능을 담당하는 프로세스를 서로 연결 가능
  - 균일한 인터페이스와 API를 통해 상호 작용가능
  ```jsx
  createReadStream(filename)
    .pipe(createGzip())
    .pipe(createCipheriv("aes192", secret, iv))
    //암호화하는 코드 쉽게 스트림 연결
    //-> 유일한 전제조건: 데이터 형태를 뒤으 스트림이 지원해야함
    .pipe(req);
  ```
  - 장점 : 깔끔하게 파이프라인을 이용해 포함하기만 하면 됨

## **6-2** 스트림 시작하기

**6-2-1** 스트림 해부

- 뒤에서 나오는 스트림 클래스 = `EventEmitter`의 인스턴스
  - `end`, `finish`, `error` 와 같은 여러 유형의 이벤트를 생성가능
- Binary 모드: 버퍼 또는 문자열과 같은 청크 형태로 데이터를 스트리밍
- 객체모드: 데이터를 일련의 개별 객체로 스트리밍

**6-2-2** Readable 스트림

- non-flowing 모드 / pause 모드

  - 스트림에서 읽기를 위한 기본 패턴
  - `read()` 함수를 이용해 새로운데이터가 있다는 readable이벤트에 리스너 연결하여 내부 버퍼가 비워질때 까지 읽음
  - Readable 스트임 내부 버퍼에서 데이터 청크를 갖고오는 Buffer 객체

  ```jsx
  process.stdin
    .on("readable", () => {
      let chunk;
      console.log("New data available");

      while ((chunk = process.stdin.read()) !== null) {
        console.log(
          `Chunk read (${chunk.length} bytes): "${chunk.toString()}"`
        );
      }
    })
    .on("end", () => console.log("End of stream"));
  ```

- flowing 모드

  - 데이터가 도착하자마자 데이터 리스너로 바로 전달하는 방식

  ```jsx
  process.stdin
  .on('data', (chunk) => {
  	console.log('New data available') console.log(
  	`Chunk read (${chunk.length} bytes): "${chunk.toString()}"` )
  })
  .on('end', () => console.log('End of stream'))

  ```

  - 데이터 흐름을 제어하는 유연성이 떨어짐
  - `resume()`으로 명시적 호출, `pause()`로 내부 버퍼에 캐시하도록 해 non-flowing 모드로 전환

- 비동기 반복자
  - Readable 스트림은 비동기 반복자(Iterator)
    → promise 반환하는 함수의 작성
- Readable Stream 의 구현

  1. 클래스 상속방식

     - 구현

       ```jsx
       import { Readable } from 'stream'

       export class CustomStream extends Readable {
         constructor(options) {
           super(options)
           // 초기화 코드
         }

         _read(size) {
           // 데이터를 읽고 this.push()로 전달
           // 스트림 종료시 this.push(null)
         }
       }

       const customStream = new CustomStream()
       customStream
       	.on('data',(chunck) => { console.log() }
       	.on('end', () => { console.log("end")}
       ```

  2. 댠순화된 생성자

     - 구현

       ```jsx
       import { Readable } from "stream";

       const customStream = new Readable({
         read(size) {
           // 데이터를 읽고 this.push()로 전달
           // 스트림 종료시 this.push(null)
         },
       });
       ```

  3. 반복가능자 (Iterables)로 Readable 스트림 얻기

     - 구현

       ```jsx
       import { Readable } from "stream";

       const data = [
         /* 데이터 배열 */
       ];
       const mountainsStream = Readable.from(data);
       mountainsStream.on("data", (mountain) => {
         console.log(`${mountain.name.padStart(14)}\t${mountain.height}m`);
       });
       ```

**6-2-3** Writable 스트림

- 대상 데이터의 목적지를 나타냄
  - `writable.write(chunk, [encoding], [callback])`
  - `writable.end([chunk], [encoding], [callback])`
- 배압(Backpressure)
  - 스트림에서 데이터가 소비보다 더 빨리 기록되는 병목현상을 해결하기 위함
  - 빨리 들어오는 데이터를 버퍼링하는 해결이 가능한데 스트림이 데이터 생성자에게 이제 버퍼링을 하지 않아도 된다고 피드백을 제공
    - writable. write() 의 highWaterMark 제한
    - 버퍼가 비워지면 다시 drain 이벤트가 발생해 다시 씀
  ```jsx
  const server = createServer((req, res) => {
    res.writeHead(200, { "Content-Type": "text/plain" });
    function generateMore() {
      while (chance.bool({ likelihood: 95 })) {
        const randomChunk = chance.string({
          length: 16 * 1024 - 1,
        });
        const shouldContinue = res.write(`${randomChunk}\n`); // (3)
        if (!shouldContinue) {
          console.log("back-pressure");
          return res.once("drain", generateMore);
        }
      }
      res.end("\n\n");
    }
    generateMore();
    res.on("finish", () => console.log("All data sent"));
  });
  ```

**6-2-4** Duplex 스트림

- 이중 스트림 : 읽기 및 쓰기가 가능한 스트림
- read(), write() 하거나 drain 등을 모두 수신 가능
- Duplex() 생성자에 전달되는 options 객체는 내부적으로 Readable(), Writable() 생성자에 모두 전달
- allowHalfOpen 옵션: false → Readable 쪽이 끝날때 Writable 쪽을 자동 종료

**6-2-5** Transform 스트림

- 데이터 변환을 처리하도록 설계된 특수한 종류의 Duplex 스트림

**필요한 함수**

- \_transform(chunk, encoding, callback): 데이터 변환 로직 구현
  - Readable의 \_read 와 비슷하지만 this.push 를 이용해 내부 읽기 버퍼로 데이터를 밀어 넣음
- \_flush(callback): 스트림 종료 전 마지막 데이터 처리
  - 위에서 스트림의 내부버퍼에 데이터가 남아있지만 스트림이 종료된 경우 남은 데이터를 푸시할 수 있는 함수

```jsx

_transform (chunk, encoding, callback) {
const pieces = (this.tail + chunk).split(this.searchStr) // (1)
const lastPiece = pieces[pieces.length - 1]
const tailLen = this.searchStr.length - 1
this.tail = lastPiece.slice(-tailLen) pieces[pieces.length - 1] = lastPiece.slice(0, -tailLen)
this.push(pieces.join(this.replaceStr))
callback() }

_flush (callback) { this.push(this.tail) callback()
}
```

- 데이터를 집계하거나 필터링하도록 사용가능

  ```jsx

  _transform (record, enc, cb) {
  	if (record.country === this.country) {
  	this.push(record) }
  	cb()
  }
  //transform 을 이용해 필터링
  ```

**6-2-6** PassThrough 스트림

- 변환을 적용하지 않고 모든 데이터 청크를 출력
- 관찰이 가능하고 느린 파이프 연결, 지연스트림을 구현

```jsx
import { PassThrough } from 'stream'
let bytesWritten = 0
const monitor = new PassThrough() monitor.on('data', (chunk) => {
	bytesWritten += chunk.length })
	monitor.on('finish', () => { console.log(`${bytesWritten} bytes written`)
})
monitor.write('Hello!') monitor.end()
//다른 파이프라인을 건들지 않고 모니터링 가능
```

**6-2-7** 지연(Lazy) 스트림

- 동시에 다수의 스트림을 생성하는 경우 오류가 발생할 가능성
  →비용이 많이 드는 초기화를 지연시킬때 스트림 필요
- passTrough 스트림을 이용해 구현

```jsx
import lazystream from "lazystream";
const lazyURandom = new lazystream.Readable(function (options) {
  return fs.createReadStream("/dev/urandom");
});
```

**6-2-8** 파이프를 사용하여 스트림 연결하기

- 스트림 두개를 연결 (read, write)

```jsx
// replace.js
import { ReplaceStream } from "./replace-stream.js";
process.stdin
  .pipe(new ReplaceStream(process.argv[2], process.argv[3]))
  .pipe(process.stdout);
```

- 이렇게 진행할 경우 흡입 (suction) 이 생성되어 자동으로 데이터가 흐름 (제어할 필요가 없음)

- 파이프의 오류처리
  - 파이프는 오류가 자동으로 전파되지 않음

```jsx
stream1
  .on("error", () => {})
  .pipe(stream2)
  .on("error", () => {}); // 하지만 이렇게 계속 오류 리스너를 연결할 경우 이상적이지 않음
```

이상적인 유틸리티 함수

```jsx
pipeline(stream1, stream2, stream3, ... , cb)

pipeline(
	process.stdin,
	createGunzip(),
	uppercasify,
	createGzip(),
	process.stdout,
	(err) => {
		if (err) {
		console.error(err)
		process.exit(1)
		}
	}
)

```

## 6-3 스트림을 사용한 비동기 제어흐름 패턴

### 6-3-1. **순차적 실행**

- 스트림은 기본적으로 순서를 유지하며 데이터를 처리
- EX)`Transform` 스트림의 `_transform()` 메서드는 이전 작업이 완료될 때까지 대기하며, 데이터 청크를 순서대로 처리

- **코드 예제:**

![순차적실행](https://prod-files-secure.s3.us-west-2.amazonaws.com/322c341c-efaf-49ce-b325-e72497d14902/73503b85-620c-4a29-bb57-ead148c468e9/image.png)

- 여러 파일의 내용을 순차적으로 연결하여 하나의 파일로 저장.
- `Readable.from()`을 이용해 파일 배열을 Readable 스트림으로 변환.
- 각 파일의 내용을 읽어 `destStream`에 파이프 연결.
- **특징:** 순서 보장.

---

### 6-3-2. **병렬 실행**

- 스트림의 기본 동작은 순서를 유지하지만, 비동기 작업을 병렬로 실행하면 처리 속도를 개선할 수 있음.(병목현상을 줄임)
- 데이터 청크 간의 순서가 중요하지 않을 때 유용.

- **코드 예제:**

![병렬실행](https://prod-files-secure.s3.us-west-2.amazonaws.com/322c341c-efaf-49ce-b325-e72497d14902/c8980774-5103-4d53-9a13-4513ace33b5e/image.png)

- `ParallelStream` 클래스는 Transform 스트림을 확장하여 병렬 실행 구현.
- `_transform()` 메서드에서 `done()`을 호출하기 전에 다음 작업을 트리거.
- **특징:** 작업 순서가 보존되지 않음.

---

### 6-3-3. 순서가 없는 동시성 제한 **병렬 실행**

- 병렬 실행에서 과도한 리소스 사용을 방지하려면, 동시 실행 작업의 수를 제한해야 함.
- 제한된 병렬 실행은 시스템 안정성과 효율성을 유지하는 데 중요.

- **코드 예제:**

![순서없는동시성제한](https://prod-files-secure.s3.us-west-2.amazonaws.com/322c341c-efaf-49ce-b325-e72497d14902/bb071185-9e37-4aa5-8c44-1c932da6a644/image.png)

- `LimitedParallelStream` 클래스는 `ParallelStream`을 확장하여 동시성 제한 추가.
- 동시 실행 중인 작업의 수를 추적하고, 제한에 도달하면 대기열에서 다음 작업을 처리.
- `_transform()`에서 실행 슬롯이 부족하면 `continueCb`에 대기

# **6-4** 파이핑(Piping) 패턴

### **6-4-1** 스트림 결합

**여러 스트림을 결합하여 하나의 스트림처럼 동작하게 하는 방식**

![image.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/322c341c-efaf-49ce-b325-e72497d14902/fa14e489-72ac-480f-9857-1e2de7791bb6/image.png)

장점:

1. **블랙박스화**: 내부 스트림 구조를 감출 수 있어 재사용 가능성이 높아집니다.
2. **오류 관리 단순화**: 개별 스트림의 `error` 리스너를 설정할 필요 없이, 결합된 스트림에서 한 번만 처리하면 됩니다.

## **6-4-2** 스트림 분기

**단일 Readable 스트림의 데이터를 여러 Writable 스트림으로 동시에 전달**

![스트림분기](https://prod-files-secure.s3.us-west-2.amazonaws.com/322c341c-efaf-49ce-b325-e72497d14902/2a54f385-c8dd-47ee-9511-274d874e07b0/image.png)

**장점**

- 동일한 데이터를 다양한 목적으로 처리 가능.
- 예: 같은 데이터를 다른 포맷으로 변환하거나, 두 개의 목적지로 저장.

**주의사항**

1. **배압 관리**: 한 스트림이 느리면 전체 파이프라인에 영향을 줄 수 있음.
2. **데이터 손실 방지**: 새로운 스트림이 추가되었을 때 이전 청크를 처리할 수 없음.
3. **`end` 이벤트 관리**: `{ end: false }` 옵션으로 종료를 제어해야 함. input Pipe 가 종료되면 종료됨

## **6-4-3** 스트림 병합

여러 Readable 스트림의 데이터를 하나의 Writable 스트림으로 병합.

![스트림병합](https://prod-files-secure.s3.us-west-2.amazonaws.com/322c341c-efaf-49ce-b325-e72497d14902/a016e936-cad1-449e-9941-5d26e2602060/image.png)

**주의사항**

1. 모든 소스가 끝나야 목적지 스트림이 종료됨.( 모든 소스가 읽기를 완료한 경우에만 목적지에서 end()를 호출하도록)
2. 데이터 순서 보장을 위해 추가적인 로직이 필요할 수 있음.

## **6-4-4** 멀티플렉싱 및 디멀티플렉싱

- 멀티플렉싱: 여러 스트림(채널)을 결합하는 작업
- 디멀티플렉싱: 수신된 데이터를 원래의 스트림으로 재구성하는 작업

예시) 원격 로거 만들기

- 클라이언트 측에서 로그를 generate → 패킷으로 묶어 목적지 스트림에 기록 → end이벤트에 대한 리스너를 목적지 스트림에 등록
- 서버측에서 스트림에서 읽기를 시작, 데이터를 읽은후 적절한 목적지 채널에 기록
