import speech_recognition as sr
from langgraph.checkpoint.mongodb import MongoDBSaver
from graph import create_chat_graph
import asyncio
from openai import AsyncOpenAI
from openai.helpers import LocalAudioPlayer

openai = AsyncOpenAI()

MONGODB_URI = "mongodb://admin:admin@localhost:27017"
config = {"configurable": {"thread_id": "4"}}


def main():
    with MongoDBSaver.from_conn_string(MONGODB_URI) as checkpointer:
        graph_with_mongo = create_chat_graph(checkpointer=checkpointer)
        r = sr.Recognizer()

        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            r.pause_threshold = 1
            while True:

                print("Say something!")
                audio = r.listen(source)

                print("Processing...!")
                try:
                    sst = r.recognize_google(audio)

                    print("You said: " + sst)

                    for event in graph_with_mongo.stream(
                        {"messages": [{"role": "user", "content": sst}]},
                        config,
                        stream_mode="values",
                    ):
                        if "messages" in event:
                            last_message = event["messages"][-1]
                            last_message.pretty_print()

                            asyncio.run(speak(last_message.content))

                    if "bye" in sst.lower():
                        exit()
                    else:
                        continue

                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results; {e}")


async def speak(response: str):
    async with openai.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="shimmer",
        input=response,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",
    ) as response:
        await LocalAudioPlayer().play(response)


if __name__ == "__main__":
    main()
