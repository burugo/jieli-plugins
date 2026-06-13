#!/usr/bin/env node
import { main } from "./jieli_node.mjs";

const [command, ...args] = process.argv.slice(2);
const allowed = new Set(["read-thread", "find-threads", "handoff-info"]);

if (!allowed.has(command)) {
  console.error("Usage: jieli_helper.mjs <read-thread|find-threads|handoff-info> [args...]");
  process.exit(2);
}

process.argv = [process.argv[0], process.argv[1], ...args];
process.exit(await main(command));
