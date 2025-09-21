import "dotenv/config";
import { Agent, run } from "@openai/agents";
import readline from "readline";


const agent = new Agent({
  name: "Customer Support Agent",
  tools: [],
  instructions:
    "You are an expert customer support agent which helps users in answering their query.",
});


const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

// Wrap rl.question into a Promise so we can use async/await
const ask = (query) => new Promise((resolve) => rl.question(query, resolve));

const main = async () => {
  while (true) {
    const userInput = await ask("> ");

    if (userInput.toLowerCase() === "exit") {
      console.log("Exiting...");
      rl.close();
      break;
    }

    try {
      const result = await run(agent, userInput);
      console.log("AI:", result.finalOutput ?? result.output_text ?? result);
    } catch (err) {
      console.error("Error running agent:", err);
    }
  }
};

main();
