"""Step 2: terminal chat loop. The model is stateless, so we resend the history."""

from ollama import ChatResponse, chat

MODEL = "llama3.2:3b"
SYSTEM_PROMPT = "Give all answers in short."
EXIT_WORDS = {"quit", "exit"}


def chat_turn(messages: list[dict], user_input: str) -> ChatResponse:
    """Send one user message; update `messages` only if the call succeeds."""
    user_msg = {"role": "user", "content": user_input}

    # Why: send a new list instead of appending first. If chat() raises,
    # `messages` is untouched, so no dangling user message is left behind.
    response = chat(model=MODEL, messages=[*messages, user_msg])

    messages.append(user_msg)
    # Why: the model only sees what we send. Without its own replies in the
    # history, it can't remember what it said.
    messages.append({"role": "assistant", "content": response.message.content})
    return response


def main() -> None:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        # Why: Ctrl+C / Ctrl+D come from input(), and both should end the program.
        try:
            user_input = input("User: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if user_input.lower() in EXIT_WORDS:
            break
        if not user_input:
            continue

        # Why: a failed call should not end the chat, but we must show the real
        # error. `except Exception` (not bare) lets Ctrl+C through.
        try:
            response = chat_turn(messages, user_input)
        except Exception as err:
            print(f"Error: {err}")
            continue

        print(f"AI: {response.message.content}")
        # Input tokens grow every turn because the whole history is resent.
        print(f"[tokens in: {response.prompt_eval_count}, out: {response.eval_count}]")


if __name__ == "__main__":
    main()
