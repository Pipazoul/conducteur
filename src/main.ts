import {Command} from "npm:commander";
import server from "./lib/server.ts";
const program = new Command();

program
  .name('conducteur')
  .description('A simple docker orchestration tool')
  .version('0.0.1');

  // start --config <file> 
program.command('start')
    .description('🚈 Start server')
    .option('--config <file>', 'Configuration file')
    .action(async (options) => {
        await server.start(options.config);
    });
  
// add node <name> <url> <token> command
program.command('add-node <name> <url> <token>')
  .description('🚃 Add a new node')
  .action((name, url, token) => {
    console.log(`Adding node ${name} with url ${url} and token ${token}`);
  });


program.parse();