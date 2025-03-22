# TSOA

## 단점

### **Promise 미지원**

Promise가 정식 도입되기 이전부터 존재했던 라이브러리인 만큼, 비동기 처리를 콜백 방식으로 하도록 만들어져 있다. 비즈니스로직에서 비동기 작업을 Promise 기반으로 처리하더라도, 최종적으로 각각의 미들웨어에선 비동기로직 결과를 Express 미들웨어 콜백으로 반환하는 로직으로 일일이 감싸줘야 한다

```jsx
// 이렇게 모든 미들웨어는 항상 응답 콜백 또는 next 를 호출해줘야 합니다.
app.get("/mydata/:id", async (req, res, next) => {
  try {
    const data = await getMyData(req.params.id);
    res.status(200).json(data);
  } catch (err) {
    next(err);
  }
});
```

간단한 wrapper 사용시

```jsx
// 아주 간단한 wrapper 함수
const withControl = (control: (req: Request) => any): RequestHandler => {
  return async (req, res, next) => {
    try {
      const response = await control(req);
      res.status(200).json(response);
    } catch (err) {
      res.status(500).json({ message: err.message });
    }
  };
};

app.get(
  "/mydata/:id",
  withControl(async (req) => {
    const data = await getMyData(req.params.id);
    return data;
  })
);
```

### request 타입 검증

타입 정의가 가능하긴 하지만 실제 request로 들어온 값에 대한 타입 검증 과정을 거치진 않는다. 때문에 request 데이터에 대한 타입 밸리데이션 로직이 별도로 필요

- 예시

```tsx
//현재 validation 예시
const email = system.ensure(req.body.email, null);
const type = system.ensure(req.body.type, null);
```

validation 로직도 결국 사람이 일일이 만드는 것인 만큼 type validation **로직과 type definition 간 괴리가 생길 수 있고, 타입스크립트는 실행시점엔 자바스크립트나 다름없음**

### 문서화 도구

높은 자유도를 가진 Express는 프로젝트 내의 어느 곳에서 어떻게 API 라우터가 작성되고 사용되어야 하는지 특별히 정해진 게 없다.

→ [swagger](https://swagger.io/)와 같은 도구로 API 문서화를 하려 하게 되면 약점(문서 자동생성불가)

→ 문제점 : 작성한 API 문서와 실제 API 작동 방식에 큰 차이가 있을 수 있고, API의 작동 방식을 수정하면서 API 문서를 업데이트하는 걸 까먹고 넘어갈 가능성

(TypeScript Open API)는 특정 방식으로 작성된 컨트롤러 코드를 정적 분석해 openAPI 스펙에 맞게 express 등 http 라이브러리에 대응하는 코드로 빌드 해주는 라이브러리

TSOA는 런타임에서의 타입 괴리를 해결하기 위해 독특한, (어쩌면 무식한) 방법을 사용합니다. 컨트롤러 코드, 그리고 컨트롤러가 참조하는 타입 파일들을 읽어서 소스코드를 파싱해 그 결과를 런타임에서도 읽을 수 있는 코드로 변환합니다. 이때 타입 정의뿐 아니라 주석까지도 파싱 해냅니다.

- `annotaion` 을 통해 라우터 기능 대체
  - `@Route(”users”)` ⇒ `router.[http메소드](”users”)`
  - `@Get()` ⇒ `router.get(”users”)`
    - `@Get(”{userId}”)` ⇒ `router.get(”users/:userId”)`
  - `@SuccessResponse()` : 성공인 경우 응답 결과 (실패 처리도 물론 가능)

</br>

---

**참고링크**
[TSOA로 HTTP API 개발하기](https://boostbrothers.github.io/technology/2022/03/03/TSOA%EB%A1%9C-HTTP-API-%EA%B0%9C%EB%B0%9C%ED%95%98%EA%B8%B0/)
