from behave import given, then, when

from src.hello_world import hello_world


@given("the project is set up")
def step_given_project_set_up(context) -> None:
    pass


@when("I call the hello_world function")
def step_when_call_hello_world(context) -> None:
    context.result = hello_world()


@then('it should return "{expected_message}"')
def step_then_return_expected_message(context, expected_message) -> None:
    assert (
        context.result == expected_message
    ), f"Expected '{expected_message}', got '{context.result}'"
