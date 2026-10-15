"""Step 1: one call to Ollama, print the answer, token counts and duration."""

from ollama import ChatResponse, ResponseError, chat

# Constants at the top: easy to change, easy to find.
MODEL = "llama3.2:3b"
PROMPT = "Why is the sky blue?"
TEMPERATURE = 0  # 0 = repeatable output, which is what you want when comparing runs
NS_PER_SECOND = 1_000_000_000  # Ollama reports durations in nanoseconds


def main() -> None:
    try:
        response: ChatResponse = chat(
            model=MODEL,
            messages=[{"role": "user", "content": PROMPT}],
            options={"temperature": TEMPERATURE},
        )
    except ConnectionError:
        # Why: the server isn't running. Say what to do, not just that it failed.
        raise SystemExit("Can't reach Ollama. Is the app running? Try: curl http://localhost:11434")
    except ResponseError as err:
        # Why: the server answered but refused, e.g. 404 for a wrong model name.
        raise SystemExit(f"Ollama rejected the request ({err.status_code}): {err.error}")

    seconds = response.total_duration / NS_PER_SECOND

    print(f"Answer: {response.message.content}")
    print(f"Input tokens:  {response.prompt_eval_count}")
    print(f"Output tokens: {response.eval_count}")
    print(f"Duration: {seconds:.2f}s")


# Why: lets another file import this one without running the call.
if __name__ == "__main__":
    main()
