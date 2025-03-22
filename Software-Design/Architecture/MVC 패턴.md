# MVC 패턴

MVC 패턴은 소프트웨어 개발 패턴 중 하나로, 소프트웨어를 세 가지 역할로 분리하는 모델이다.

<div align="center">
  <img src="https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FMb6u7%2FbtsHmGewnTD%2FkZkzC59LLONzeER0NaTQi0%2Fimg.png">
  <p><em>MVC 패턴 다이어그램 with 3계층 설계</em></p>
</div>

<div align="center">
  <img src="https://mblogthumb-phinf.pstatic.net/MjAxNzAzMjVfMTM0/MDAxNDkwNDQyNDI5OTAy.MUksll6Y9SzelJjmGW6zXOlPebJKOft3OhcnmhrcmTgg.4g4FxlhwEpgxp8kGXJVLf2LHlrRJhP7NqR7LJew8tL0g.PNG.jhc9639/ModelViewControllerDiagram.png?type=w800">
  <p><em>MVC 패턴 다이어그램</em></p>
</div>

## Model

- 데이터와 비즈니스 로직을 처리하는 부분
- 데이터베이스와 직접 연동하여 데이터를 조회하고 조작
- 데이터베이스 연동 로직을 분리하여 모델을 재사용 가능하게 함

> ### 규칙
>
> 1.  사용자가 편집하길 원하는 모든 데이터를 가지고 있어야 한다.
> 2.  뷰나 컨트롤러에 대해서 어떤 정보도 알지 말아야 한다.
> 3.  변경이 일어나면, 변경 통지에 대한 처리방법을 구현해야만 한다.

## View

- 사용자 인터페이스를 담당하는 부분
- 모델에서 제공하는 데이터를 화면에 표시
- 사용자의 입력을 받아 모델에 전달

> ### 규칙
>
> 1.  모델이 가지고 있는 정보를 따로 저장해서는 안된다.
> 2.  모델이나 컨트롤러와 같이 다른 구성요소들을 몰라야 된다.
> 3.  변경이 일어나면 변경통지에 대한 처리방법을 구현해야만 한다.

## Controller

- 모델과 뷰를 연결하는 부분
- 사용자의 입력을 받아 모델에 전달
- 모델에서 제공하는 데이터를 뷰에 전달

> ### 규칙
>
> 1.  모델이나 뷰에 대해서 알고 있어야 한다.
> 2.  모델이나 뷰의 변경을 모니터링 해야 한다.

## 예시

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
```

```python
class UserView:
    def display_user(self, user):
        print(f"User: {user.name}, Age: {user.age}")
```

```python
class UserController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def display_user(self):
        self.view.display_user(self.model)
```

```python
user_controller = UserController(User("John", 25), UserView())
user_controller.display_user()
```

```
User: John, Age: 25
```
